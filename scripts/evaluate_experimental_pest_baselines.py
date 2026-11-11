"""Audit fixed rule and zero-input baselines in the experimental pest runtime."""
from dataclasses import asdict
import json
import math
import os

from evaluate_baseline_pairs import ROOT, live_children
import yaml

from mars_env.artifacts import new_run, sha256, write_json
from mars_env.baseline_evaluation import evaluate_episode, summarize, verify_pairs
from mars_env.experimental_env import ExperimentalPestEnv
from mars_env.exogenous import generate_season
from mars_env.pests import PestParameters
from mars_env.policies import NoInputPolicy, RulePolicy
from mars_env.process_backend import LegacyProcessBackend
from mars_env.resources import EPS, ResourceRules


def check_masks(record, rules, spray_threshold):
    condition = record["season"]
    beta, shock = condition["beta"], condition["shock"]
    water_left = rules.initial_water
    water_used = nitrogen_used = sprays = 0
    stage_entry = announcement = last_spray = None
    survey_days = 0
    spray_available_days = 0
    for row in record["daily_tape"]:
        day, stage = row["decision_day"], row["istage"]
        if shock:
            if stage_entry is None and stage == shock["stage"]:
                stage_entry = day
            if stage_entry is not None and announcement is None and day >= stage_entry + shock["delay_days"]:
                fraction = shock["fraction"]
                if shock["contract"] == "remaining_fraction":
                    water_left *= 1 - fraction
                else:
                    water_left = max(0, (1 - fraction) * rules.initial_water - water_used)
                announcement = day

        bulletin = row["public_bulletin"]
        expected_fraction = shock["fraction"] if announcement is not None else 0
        expected_age = day - announcement if announcement is not None else 0
        if (bulletin["announced"] != int(announcement is not None)
                or not math.isclose(bulletin["reduction_fraction"], expected_fraction, abs_tol=1e-7)
                or not math.isclose(bulletin["days_since_announcement"], expected_age, abs_tol=1e-5)):
            raise ValueError(f"Public water bulletin differs on decision day {day}")

        # Replay remaining product budgets from cumulative actions, without using the environment ledger.
        closed = stage == rules.input_closed_stage
        nitrogen_cash = beta * rules.nitrogen_budget - nitrogen_used * rules.nitrogen_price
        spray_cash = beta * rules.spray_budget - sprays * rules.spray_price
        spray_available = (spray_cash + EPS >= rules.spray_price
                           and stage < rules.spray_stage_limit
                           and (last_spray is None or day - last_spray >= rules.spray_interval))
        expected = [
            *(x <= water_left + EPS and not (closed and x > 0) for x in rules.water_grid),
            *(x * rules.nitrogen_price <= nitrogen_cash + EPS and not (closed and x > 0) for x in rules.nitrogen_grid),
            True, spray_available,
        ]
        if row["mask"] != expected:
            raise ValueError(f"Independent resource mask differs on decision day {day}")
        survey = row["public_survey"]
        survey_days += survey["survey_value"] > 0
        spray_available_days += spray_available
        action = rules.decode(row["action_indices"])
        if record["policy"] == "no_input":
            if any(row["action_indices"]):
                raise ValueError("Zero-input policy applied an input")
        else:
            expected_spray = int(spray_available and spray_threshold > 0
                                 and survey["survey_value"] >= spray_threshold)
            if action.spray != expected_spray:
                raise ValueError(f"Public survey spray rule differs on decision day {day}")
        water_left -= action.water_mm
        water_used += action.water_mm
        nitrogen_used += action.nitrogen_kg_ha
        sprays += action.spray
        if action.spray:
            last_spray = day
    return {"decision_days": record["steps"], "survey_available_days": survey_days,
            "spray_available_days": spray_available_days, "water_announcement_day": announcement}


def make_environment(config, season, parameters, noise_std, rules):
    def backend_factory(**kwargs):
        return LegacyProcessBackend(mode="experimental_pest", season=season,
                                    parameters=parameters, noise_std=noise_std, **kwargs)

    return ExperimentalPestEnv(season=season, parameters=parameters, noise_std=noise_std,
                               rules=rules, backend_factory=backend_factory,
                               grain_price=config["economics"]["grain_usd_kg"])


def run_episode(config, season, parameters, noise_std, policy, rules):
    env = make_environment(config, season, parameters, noise_std, rules)
    try:
        return evaluate_episode(env, policy, season, rules, env.grain_price,
                                reset_options={}, record_decision_context=True)
    finally:
        env.close()


def main():
    if os.environ.get("MARS_CANONICAL_UFGA_METADATA") != "1":
        raise RuntimeError("Use the corrected metadata image")
    config = yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8"))
    spec = json.loads((ROOT / "configs/faw_technical_sensitivity.json").read_text(encoding="utf-8-sig"))
    assert spec["scope"] == "technical_diagnostic_only"
    overrides = spec["baseline_overrides"]
    assert all(config["pest"][key] is None for key in overrides)
    pest = {**config["pest"], **overrides}
    parameters = PestParameters.from_config({**config, "pest": pest})
    rules = ResourceRules.from_config(config)
    rule = RulePolicy(baseline_nitrogen=tuple(sorted(config["management"]["baseline_nitrogen"].items())))
    policies = {"no_input": NoInputPolicy(), "rule": rule}
    run = new_run(ROOT, "baseline_pairs_experimental_pest")
    os.environ["MARS_RUN_DIR"] = str(run)
    print(f"RUN_DIR={run}", flush=True)
    write_json(run / "settings.json", {"pest": pest, "policies": {k: asdict(v) for k, v in policies.items()},
                                      "split": "validation", "season_ids": list(range(4))})
    records, files = [], {}
    try:
        for season_id in range(4):
            season = generate_season(config, split="validation", season_id=season_id)
            for name, policy in policies.items():
                row = run_episode(config, season, parameters, pest["survey_noise_std"], policy, rules)
                row["policy"] = name
                row["mask_audit"] = check_masks(row, rules, rule.survey_threshold)
                name_on_disk = f"{name}_season_{season_id}.json"
                write_json(run / name_on_disk, row)
                files[name_on_disk] = sha256(run / name_on_disk)
                records.append(row)
                result = row["episode_result"]
                print(f"season={season_id} policy={name} steps={row['steps']} sprays={result['sprays']} "
                      f"termination={result['reason']}", flush=True)
        checks = verify_pairs(records)
        alive = live_children()
        if alive:
            raise RuntimeError(f"Owned child processes remain: {alive}")
        write_json(run / "verification.json", {
            "passed": True, "scope": "experimental pest baseline technical diagnostic",
            "validation_pairs": len(checks), "native_seasons": len(records),
            "weather_pairing": checks, "summary": summarize(records),
            "verified_decision_days": sum(row["steps"] for row in records),
            "observed_water_announcements": sum(row["mask_audit"]["water_announcement_day"] is not None
                                                for row in records),
            "actual_sprays": sum(row["episode_result"]["sprays"] for row in records),
            "constraint_violations": sum(row["constraint_violations"] for row in records),
            "episode_files": files, "settings_sha256": sha256(run / "settings.json"),
            "owned_live_children_after_close": alive, "thresholds_tuned": False,
            "final_test_split_used": False, "research_ready": False, "main_training_allowed": False,
        })
    except BaseException as exc:
        write_json(run / "failure.json", {"passed": False, "error": repr(exc), "completed_episodes": len(records)})
        raise


if __name__ == "__main__":
    main()
