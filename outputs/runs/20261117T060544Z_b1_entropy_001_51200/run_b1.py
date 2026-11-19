"""Compare entropy coefficients 0 and 0.01 for b1 at the same 13% irrigation initialization."""
from concurrent.futures import ProcessPoolExecutor
import json
from dataclasses import replace
from functools import partial
from multiprocessing import get_context
import os
from pathlib import Path
import shutil
from statistics import mean
import sys

import torch
import yaml

SOURCE = Path("/workspace")
PRIOR = Path("/prior")
RUN = Path(__file__).resolve().parent
BASELINE = Path("/baseline")
FIRST_STAGE = RUN / "stage_20480"
NONZERO_MASS = 0.13
ENTROPY_COEF = 0.01
ARMS = (0.0, ENTROPY_COEF)
STEPS = (20_480, 51_200)
CONDITIONS = ("none", "early_40")
EARLY_DAY = 13
sys.path.insert(0, str(SOURCE / "scripts"))
import run_comparison as comparison


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def initialize(config, fit):
    partial_record = FIRST_STAGE / f"{fit.label}_partial.json"
    if partial_record.exists():
        return
    cfg = config["training"]
    env = comparison.ChannelCycler(config, learn=fit.learn,
                                   reduction_probability=fit.reduction_probability)
    try:
        model = comparison.MaskablePPO(
            "MlpPolicy", env, device="cpu", seed=fit.seed, gamma=cfg["gamma"], gae_lambda=cfg["gae_lambda"],
            n_steps=cfg["n_steps"], batch_size=cfg["batch_size"], n_epochs=cfg["n_epochs"],
            ent_coef=ENTROPY_COEF,
            policy_kwargs={"net_arch": {"pi": cfg["policy_layers"], "vf": cfg["value_layers"]}},
        )
        probabilities = torch.tensor([1 - NONZERO_MASS] + [NONZERO_MASS / 5] * 5)
        with torch.no_grad():
            model.policy.action_net.weight.zero_()
            model.policy.action_net.bias.copy_(probabilities.log())
        assert torch.allclose(model.policy.action_net.bias.softmax(0), probabilities)
        initial = FIRST_STAGE / f"{fit.label}_initial.zip"
        partial = FIRST_STAGE / f"{fit.label}_partial.zip"
        model.save(initial)
        shutil.copyfile(initial, partial)
    finally:
        env.close()
    comparison.write_json(partial_record, {
        "steps": 0, "checkpoint_sha256": comparison.sha256(partial),
        "season_cursors": [0] * cfg["n_envs"], "seconds": 0.0,
        "completed_train_seasons": 0, "chunks": 0, "selection": [], "best": None,
    })
    print("INITIALIZE", fit.label, "nonzero mass", NONZERO_MASS, flush=True)


def prepare_fit(fit):
    source_progress = read_json(FIRST_STAGE / f"{fit.label}_partial.json")
    assert source_progress["steps"] == STEPS[0]
    for suffix in ("partial.zip", "best.zip", "partial.json"):
        source = FIRST_STAGE / f"{fit.label}_{suffix}"
        target = RUN / source.name
        if not target.exists():
            shutil.copyfile(source, target)


class MeasuredIrrigation:
    """Apply the greedy action and measure the masked distribution on the same observation."""

    def __init__(self, model):
        self.policy = model.policy
        self.policy.set_training_mode(False)
        self.entropies = []

    def apply(self, observation, mask, action):
        legal = mask[:6]
        with torch.no_grad():
            tensor, _ = self.policy.obs_to_tensor(observation)
            distribution = self.policy.get_distribution(tensor, action_masks=legal)
            action[0] = int(distribution.get_actions(deterministic=True).item())
            if legal.sum() > 1:
                self.entropies.append(float(distribution.entropy().item()))
        return action


def evaluate(job):
    config, fit, season_id = job
    torch.set_num_threads(1)
    rules = comparison.ResourceRules.from_config(config)
    price = comparison.grain_price(config)
    parameters, noise = comparison.pest_settings(config)
    reference = comparison.RulePolicy.from_config(config)
    condition_options = comparison.evaluation_conditions(config)
    base_season = comparison.generate_season(config, split="validation", season_id=season_id)
    rows, weather = [], {}
    for coef, folder in ((0.0, BASELINE), (ENTROPY_COEF, RUN)):
        checkpoints = (folder / "stage_20480" / f"{fit.label}_partial.zip", folder / f"{fit.label}_final.zip")
        for step, checkpoint in zip(STEPS, checkpoints):
            model = comparison.MaskablePPO.load(checkpoint, device="cpu")
            assert model.ent_coef == coef and model.num_timesteps == step
            for condition in CONDITIONS:
                irrigation = MeasuredIrrigation(model)
                policy = comparison.CompositePolicy(reference, (irrigation,))
                season = base_season.with_condition(beta=config["scenarios"]["evaluation_beta"],
                                                    shock=condition_options[condition])
                backend = partial(comparison.LegacyProcessBackend, mode="experimental_pest", season=season,
                                  parameters=parameters, noise_std=noise)
                env = comparison.ExperimentalPestEnv(season=season, parameters=parameters, noise_std=noise,
                                                     rules=rules, grain_price=price, backend_factory=backend)
                try:
                    record = comparison.evaluate_episode(env, policy, season, rules, price, reset_options={})
                finally:
                    env.close()
                tape = record["daily_tape"]
                trace = {day["yrdoy"]: day["weather"] for day in tape}
                assert all(weather[day] == trace[day] for day in weather.keys() & trace.keys())
                weather.update(trace)
                result = record["episode_result"]
                early_water = sum(rules.water_grid[d["action_indices"][0]] for d in tape
                                  if d["decision_day"] < EARLY_DAY)
                if condition == "early_40":
                    assert result["water_cut_day"] == EARLY_DAY
                    assert abs(result["water_cut_mm"] - (rules.initial_water - early_water) * 0.4) < 1e-6
                violations = comparison.resource_violations(result, result["water_cut_mm"], rules, season.beta)
                rows.append({"seed": fit.seed, "season": season_id, "condition": condition, "steps": step,
                             "ent_coef": coef, "water_before_day13_mm": early_water,
                             "entropy_sum": sum(irrigation.entropies), "entropy_days": len(irrigation.entropies),
                             "resource_violations": violations, **result})
    return rows


def summary(rows, initial_water):
    entropy_days = sum(r["entropy_days"] for r in rows)
    assert entropy_days > 0
    return {
        "episodes": len(rows),
        "no_irrigation": sum(r["water_mm"] == 0 for r in rows),
        "exhausted_before_day13": sum(r["water_before_day13_mm"] >= initial_water - 1e-6 for r in rows),
        "mean_action_entropy_nats": sum(r["entropy_sum"] for r in rows) / entropy_days,
        "eligible_entropy_days": entropy_days,
        **{f"mean_{key}": mean(r[key] for r in rows)
           for key in ("water_mm", "water_before_day13_mm", "harvested_grain_kg_ha", "net_return")},
    }


def main():
    os.environ["MARS_RUN_DIR"] = str(RUN)
    torch.set_num_threads(1)
    prior_design = read_json(PRIOR / "design.json")
    config_file = PRIOR / "config.yaml"
    assert comparison.sha256(config_file) == prior_design["config_sha256"]
    assert os.environ["MARS_IMAGE_ID"] == prior_design["image"]
    for relative, digest in prior_design["source_sha256"].items():
        assert comparison.sha256(SOURCE / relative) == digest, f"Source changed: {relative}"
    config = yaml.safe_load(config_file.read_text(encoding="utf-8"))
    assert not prior_design["policy_protocol"]["behavior_cloning"]
    assert "sparse_nonzero_mass" not in config["training"]
    seeds, seasons = prior_design["policy_seeds"], prior_design["seasons"]
    plan = [fit for fit in comparison.training_plan(config, steps=STEPS[-1], seeds=seeds)
            if fit.regime == "b" and fit.policy == 1]
    baseline_design = read_json(BASELINE / "design.json")
    for key, expected in (("seeds", seeds), ("seasons", seasons), ("conditions", list(CONDITIONS)),
                          ("checkpoints_compared", list(STEPS))):
        assert baseline_design[key] == expected, f"Comparison protocol differs in {key}"
    assert baseline_design["prior_config_sha256"] == comparison.sha256(config_file)
    assert baseline_design["source_sha256"] == prior_design["source_sha256"]
    assert baseline_design["image"] == prior_design["image"]
    assert baseline_design["initialization_nonzero_probability"] == NONZERO_MASS
    comparison.write_json(RUN / "design.json", {
        "prior_run": os.environ["MARS_PRIOR_RUN"], "prior_design_sha256": comparison.sha256(PRIOR / "design.json"),
        "prior_config_sha256": comparison.sha256(config_file), "checkpoints_compared": list(STEPS),
        "seeds": seeds, "seasons": seasons, "split": "validation", "conditions": list(CONDITIONS),
        "baseline": os.environ["MARS_BASELINE_RUN"], "baseline_design_sha256": comparison.sha256(BASELINE / "design.json"),
        "initialization_nonzero_probability": NONZERO_MASS, "entropy_coefficients": list(ARMS),
        "entropy_measure": "masked Shannon entropy on greedy evaluation states with at least two legal actions",
        "action_probabilities_when_all_legal": [0.87] + [0.026] * 5,
        "weather_and_budget_paired": True, "final_test_split_used": False, "hypothesis_tests_run": False,
        "source_sha256": prior_design["source_sha256"], "image": os.environ["MARS_IMAGE_ID"],
    })
    FIRST_STAGE.mkdir(exist_ok=True)
    for fit in plan:
        initialize(config, fit)
        comparison.train(FIRST_STAGE, config, replace(fit, steps=STEPS[0]))
        prepare_fit(fit)
        comparison.train(RUN, config, fit)
    rows = []
    for fit in plan:
        print("EVALUATING", fit.label, flush=True)
        batch = RUN / f"{fit.label}_episodes.json"
        if batch.exists():
            data = read_json(batch)
        else:
            jobs = [(config, fit, season) for season in seasons]
            with ProcessPoolExecutor(max_workers=8, mp_context=get_context("fork")) as pool:
                data = [row for result in pool.map(evaluate, jobs) for row in result]
            comparison.write_json(batch, data)
        rows.extend(data)
    expected = {(seed, season, condition, step) for seed in seeds for season in seasons
                for condition in CONDITIONS for step in STEPS}
    def key(row):
        return row["seed"], row["season"], row["condition"], row["steps"]
    indexed = {coef: {key(r): r for r in rows if r["ent_coef"] == coef} for coef in ARMS}
    assert len(rows) == 2 * len(expected) and all(set(group) == expected for group in indexed.values())
    assert sum(r["resource_violations"] for r in rows) == 0
    baseline_rows = {key(r): r for r in read_json(BASELINE / "episodes.json")}
    assert set(baseline_rows) == expected
    for k, saved in baseline_rows.items():
        replay = indexed[0.0][k]
        assert all(replay[field] == saved[field] for field in (
            "water_mm", "water_before_day13_mm", "harvested_grain_kg_ha", "net_return"
        )), f"Matched control did not reproduce at {k}"
    water = config["environment"]["initial_water_mm"]
    results = {coef: {step: {cond: summary(
        [r for r in indexed[coef].values() if r["steps"] == step and r["condition"] == cond], water)
        for cond in CONDITIONS} for step in STEPS} for coef in ARMS}
    metrics = ("net_return", "water_mm", "water_before_day13_mm", "harvested_grain_kg_ha")
    paired_delta = {}
    for step in STEPS:
        paired_delta[step] = {}
        for cond in CONDITIONS:
            keys = sorted(k for k in expected if k[2:] == (cond, step))
            paired_delta[step][cond] = {
                metric: mean(indexed[ENTROPY_COEF][k][metric] - indexed[0.0][k][metric] for k in keys)
                for metric in metrics
            }
    by_seed = {seed: {cond: mean(
        indexed[ENTROPY_COEF][k]["net_return"] - indexed[0.0][k]["net_return"]
        for k in sorted(expected) if k[0] == seed and k[2:] == (cond, STEPS[-1])
    ) for cond in CONDITIONS} for seed in seeds}
    comparison.write_json(RUN / "episodes.json", rows)
    comparison.write_json(RUN / "verification.json", {
        "passed": True, "episodes": len(rows), "resource_violations": 0, "summary": results,
        "paired_delta_001_minus_0": paired_delta, "seed_net_return_delta_at_51200": by_seed,
        "saved_controls_reproduced": True, "final_test_split_used": False, "hypothesis_tests_run": False,
    })
    print("COMPLETED", len(rows), "episodes", flush=True)


if __name__ == "__main__":
    main()

