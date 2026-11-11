"""Verify the irrigation-only wrapper on actual experimental DSSAT seasons."""
from dataclasses import asdict
import hashlib
import json
import math
import os

import numpy as np
import yaml

from evaluate_baseline_pairs import ROOT, live_children
from evaluate_experimental_pest_baselines import check_masks, make_environment
from mars_env.artifacts import new_run, sha256, write_json
from mars_env.exogenous import generate_season
from mars_env.pests import PestParameters
from mars_env.policies import IrrigationOnly, RulePolicy, public_values
from mars_env.resources import ResourceRules


def observation_hash(obs):
    return hashlib.sha256(np.asarray(obs, dtype="<f4").tobytes()).hexdigest()


def reject_masked_water(env, base, water_index):
    day, state, last = base.day, base.state, env.last_observation
    try:
        env.step(water_index)
    except ValueError as error:
        assert str(error) == "Masked irrigation action"
    else:
        raise AssertionError("Wrapper accepted a masked irrigation action")
    assert base.day == day and base.state is state and env.last_observation is last


def check_zero_budget_rejection(config, season, parameters, noise_std, rules, rule):
    constrained = season.with_condition(beta=0, shock=None)
    base = make_environment(config, constrained, parameters, noise_std, rules)
    env = IrrigationOnly(base, rule, rules=rules)
    try:
        env.reset()
        assert base.exogenous is constrained
        assert env.action_masks().tolist() == [True] + [False] * (len(rules.water_grid) - 1)
        reject_masked_water(env, base, 1)
        _, reward, terminated, truncated, info = env.step(0)
        assert base.day == 1 and reward == info["cost"] == 0
        assert not terminated and not truncated
        return {"season": constrained.manifest(), "rejected_water_index": 1,
                "state_unchanged_after_rejection": True, "legal_zero_advanced_one_day": True}
    finally:
        env.close()


def run_arm(base, season, rule, rules, arm):
    wrapped = arm != "rule"
    env = IrrigationOnly(base, rule, rules=rules) if wrapped else base
    water_count = len(rules.water_grid)
    spray_offset = water_count + len(rules.nitrogen_grid)
    tape, rejection_days = [], []
    try:
        obs, reset_info = env.reset()
        assert base.exogenous is season and reset_info["seed"] == season.backend_seed
        assert reset_info["experimental_only"] and not reset_info["research_ready"]
        assert (env.action_space.n == water_count if wrapped
                else env.action_space.nvec.tolist() == [water_count, len(rules.nitrogen_grid), 2])
        for day in range(base.max_days):
            state = base.state
            values = public_values(obs)
            date, stage = int(state["yrdoy"]), int(state["istage"])
            mask = base.action_masks()
            rule_action = rule.action(obs, mask.copy(), rules).tolist()
            if wrapped:
                assert np.array_equal(env.action_masks(), mask[:water_count])
                masked = np.flatnonzero(~mask[:water_count])
                if len(masked) and not rejection_days:
                    reject_masked_water(env, base, int(masked[0]))
                    rejection_days.append(day)
            chosen_water = 0 if arm == "zero_water" else rule_action[0]
            expected = [chosen_water, *rule_action[1:]]
            assert all(mask[offset + index] for offset, index in zip((0, water_count, spray_offset), expected))
            desired_n = dict(rule.baseline_nitrogen).get(round(values["dap"]), 0)
            assert rule_action[1] == max(i for i, amount in enumerate(rules.nitrogen_grid)
                                         if amount <= desired_n and mask[water_count + i])
            before_digest = observation_hash(obs)
            obs, reward, terminated, truncated, info = env.step(chosen_water if wrapped else expected)
            assert env.observation_space.contains(obs)
            action = rules.decode(expected)
            assert base.previous_action == action
            diagnostic = base.state["mars_pest_diagnostic"]
            assert diagnostic["day"] == day and diagnostic["spray"] == bool(action.spray)
            assert diagnostic["arrival"] == season.pest_arrivals[day]
            assert info["experimental_only"] and not info["research_ready"]
            cost = (action.water_mm * rules.water_price + action.nitrogen_kg_ha * rules.nitrogen_price
                    + action.spray * rules.spray_price + bool(action.water_mm) * rules.irrigation_labor
                    + bool(action.nitrogen_kg_ha) * rules.nitrogen_labor)
            assert math.isclose(info["cost"], cost, abs_tol=1e-7)
            assert math.isclose(reward, info["revenue"] - cost, abs_tol=1e-7)
            tape.append({
                "decision_day": day, "yrdoy": date, "istage": stage, "mask": mask.tolist(),
                "weather": {k: float(state[k]) for k in ("rain", "tmin", "tmax", "srad")},
                "action_indices": expected, "rule_action_indices": rule_action,
                "observation_sha256": before_digest, "next_observation_sha256": observation_hash(obs),
                "public_survey": {name: values[name] for name in ("survey_value", "survey_age")},
                "public_bulletin": {name: values[name] for name in
                                    ("announced", "reduction_fraction", "days_since_announcement")},
                "cost": cost, "raw_reward": reward, "revenue": info["revenue"],
                "terminated": terminated, "truncated": truncated,
            })
            assert not truncated
            if terminated:
                result = info["episode_result"]
                assert result["reason"] in ("harvest", "crop_failure")
                break
        else:
            raise AssertionError("Diagnostic season did not terminate")
    finally:
        env.close()

    actions = [rules.decode(row["action_indices"]) for row in tape]
    expected_cost = math.fsum(row["cost"] for row in tape)
    revenue = result["harvested_grain_kg_ha"] * base.grain_price
    assert all(row["revenue"] == 0 for row in tape[:-1])
    assert math.isclose(tape[-1]["revenue"], revenue)
    assert math.isclose(result["total_cost"], expected_cost, abs_tol=1e-6)
    assert math.isclose(result["net_return"], revenue - expected_cost, abs_tol=1e-6)
    assert math.isclose(result["net_return"], math.fsum(row["raw_reward"] for row in tape), abs_tol=1e-6)
    for field in ("water_mm", "nitrogen_kg_ha"):
        assert math.isclose(result[field], math.fsum(getattr(action, field) for action in actions))
    assert result["sprays"] == sum(action.spray for action in actions)
    record = {"policy": arm, "season": season.manifest(), "steps": len(tape), "daily_tape": tape,
              "episode_result": result, "masked_water_rejection_days": rejection_days}
    record["mask_audit"] = check_masks(record, rules, rule.survey_threshold)
    return record


def common_weather(a, b):
    assert a["season"] == b["season"]
    left, right = ({row["yrdoy"]: row["weather"] for row in record["daily_tape"]} for record in (a, b))
    assert len(left) == a["steps"] and len(right) == b["steps"]
    common = left.keys() & right.keys()
    assert common and all(left[day] == right[day] for day in common)
    return len(common)


def main():
    assert os.environ.get("MARS_CANONICAL_UFGA_METADATA") == "1"
    config = yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_bytes())
    state = json.loads((ROOT / "configs/field_calibration_candidate_screen.json").read_bytes())
    prior = (ROOT / state["experimental_pest_baseline_pair_evidence"]).parent
    settings = json.loads((prior / "settings.json").read_bytes())
    assert settings["split"] == "validation" and settings["season_ids"] == list(range(4))
    pest = settings["pest"]
    parameters = PestParameters.from_config({**config, "pest": pest})
    rule_settings = settings["policies"]["rule"]
    rule = RulePolicy(**{**rule_settings, "baseline_nitrogen": tuple(map(tuple, rule_settings["baseline_nitrogen"]))})
    rules = ResourceRules.from_config(config)
    run = new_run(ROOT, "experimental_irrigation_only_shared_rules")
    os.environ["MARS_RUN_DIR"] = str(run)
    print(f"RUN_DIR={run}", flush=True)
    write_json(run / "settings.json", {"pest": pest, "rule": asdict(rule), "split": "validation",
                                      "season_ids": settings["season_ids"],
                                      "baseline_settings_sha256": sha256(prior / "settings.json")})
    files, comparisons = {}, []
    try:
        for season_id in settings["season_ids"]:
            season = generate_season(config, split="validation", season_id=season_id)
            arms = {}
            for arm in ("rule", "matched_water", "zero_water"):
                base = make_environment(config, season, parameters, pest["survey_noise_std"], rules)
                record = arms[arm] = run_arm(base, season, rule, rules, arm)
                name = f"{arm}_season_{season_id}.json"
                write_json(run / name, record)
                files[name] = sha256(run / name)
                print(f"season={season_id} arm={arm} steps={record['steps']}", flush=True)
            reference, matched, zero = (arms[key] for key in ("rule", "matched_water", "zero_water"))
            prior_rule = json.loads((prior / f"rule_season_{season_id}.json").read_bytes())
            assert reference["season"] == prior_rule["season"]
            assert reference["episode_result"] == prior_rule["episode_result"]
            assert [r["action_indices"] for r in reference["daily_tape"]] == [
                r["action_indices"] for r in prior_rule["daily_tape"]]
            assert reference["daily_tape"] == matched["daily_tape"]
            assert reference["episode_result"] == matched["episode_result"]
            assert zero["episode_result"]["water_mm"] == 0
            override_days = sum(row["rule_action_indices"][0] != row["action_indices"][0]
                                for row in zero["daily_tape"])
            assert override_days
            comparisons.append({
                "season_id": season_id, "rule_matched_decision_days": matched["steps"],
                "zero_water_decision_days": zero["steps"], "zero_water_override_days": override_days,
                "zero_water_common_weather_dates": common_weather(reference, zero),
                "matched_sprays": matched["episode_result"]["sprays"],
                "zero_water_sprays": zero["episode_result"]["sprays"],
                "masked_water_rejections": sum(len(arm["masked_water_rejection_days"]) for arm in (matched, zero)),
                "termination_reasons": {name: record["episode_result"]["reason"] for name, record in arms.items()},
            })
        first = generate_season(config, split="validation", season_id=settings["season_ids"][0])
        rejection_probe = check_zero_budget_rejection(
            config, first, parameters, pest["survey_noise_std"], rules, rule,
        )
        assert not live_children()
        write_json(run / "verification.json", {
            "passed": True, "validation_addresses": len(comparisons), "native_seasons": len(files),
            "comparisons": comparisons, "episode_files": files,
            "masked_water_rejection_probe": rejection_probe,
            "rule_matched_observations_masks_actions_rewards_and_outcomes_exact": True,
            "constraint_violations": 0, "owned_live_children_after_close": [],
            "diagnostic_only": True, "thresholds_tuned": False, "final_test_split_used": False,
            "research_ready": False, "main_training_allowed": False,
        })
    except BaseException as exc:
        write_json(run / "failure.json", {"passed": False, "error": repr(exc),
                                          "completed_episodes": list(files)})
        raise


if __name__ == "__main__":
    main()
