"""Pest pressure, leaf loss and the value of spraying under the rule policy (validation only).

Variants share each season's weather, arrival and survey-noise tapes; the pest-free variant
replaces only the arrival tape with zeros. No water reduction, budget multiplier 1.0.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from functools import partial
from multiprocessing import get_context
import os
from pathlib import Path
import sys

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from mars_env.artifacts import new_run, write_json
from mars_env.comparison import lower_tail_mean
from mars_env.experimental_env import ExperimentalPestEnv
from mars_env.exogenous import generate_season
from mars_env.pests import pest_settings
from mars_env.policies import RulePolicy
from mars_env.process_backend import LegacyProcessBackend
from mars_env.resources import ResourceRules

PARAMETERS, NOISE = pest_settings(yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8")))
VARIANTS = ("rule_0.3", "no_spray", "rule_0.1", "rule_0.5", "pest_free")


def measure(job):
    season_id, variant, config = job
    rules, price = ResourceRules.from_config(config), config["economics"]["grain_usd_kg"]
    threshold = {"rule_0.1": 0.1, "rule_0.5": 0.5}.get(variant, 0.3)
    rule = replace(RulePolicy.from_config(config), survey_threshold=threshold)
    season = generate_season(config, split="validation", season_id=season_id).with_condition(beta=1.0, shock=None)
    if variant == "pest_free":
        season = replace(season, pest_arrivals=np.zeros_like(season.pest_arrivals))
    env = ExperimentalPestEnv(season=season, parameters=PARAMETERS, noise_std=NOISE, rules=rules, grain_price=price,
                              backend_factory=partial(LegacyProcessBackend, mode="experimental_pest", season=season,
                                                      parameters=PARAMETERS, noise_std=NOISE))
    densities, losses, spray_days, readings = [], [], [], []
    try:
        observation, _ = env.reset()
        day = 0
        while True:
            action = rule.action(observation, env.action_masks().copy(), rules)
            if variant == "no_spray":
                action[2] = 0
            if action[2]:
                spray_days.append(day)
            public = env.state["mars_pest_public"]
            if public["survey_available"] and public["survey_age"] == 0:
                readings.append(float(public["survey_value"]))
            observation, _, terminated, truncated, info = env.step(action)
            diagnostic = env.state.get("mars_pest_diagnostic")
            if diagnostic:
                densities.append(float(diagnostic["density"]))
                losses.append(float(diagnostic["applied_fraction"]))
            day += 1
            assert not truncated
            if terminated:
                result = info["episode_result"]
                break
    finally:
        env.close()
    return {"season_id": season_id, "variant": variant, **result, "spray_days": spray_days,
            "mean_density": float(np.mean(densities)) if densities else 0.0,
            "peak_density": float(np.max(densities)) if densities else 0.0,
            "applied_leaf_fraction_sum": float(np.sum(losses)),
            "survey_readings": readings}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seasons", type=int, default=80)
    parser.add_argument("--first-season", type=int, default=1000)
    parser.add_argument("--alpha", type=float, help="Override the configured leaf-loss coefficient for this run")
    args = parser.parse_args()
    if args.alpha is not None:
        global PARAMETERS
        PARAMETERS = replace(PARAMETERS, alpha=args.alpha)
    config = yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8"))
    run = new_run(ROOT, "pest_control_rule_policy")
    os.environ["MARS_RUN_DIR"] = str(run)
    print("RUN_DIR=" + str(run), flush=True)
    jobs = [(season, variant, config) for season in range(args.first_season, args.first_season + args.seasons)
            for variant in VARIANTS]
    with ProcessPoolExecutor(max_workers=4, mp_context=get_context("fork")) as pool:
        rows = list(pool.map(measure, jobs, chunksize=4))
    write_json(run / "seasons.json", rows)
    summary = {}
    for variant in VARIANTS:
        items = [row for row in rows if row["variant"] == variant]
        net = [row["net_return"] for row in items]
        days = [d for row in items for d in row["spray_days"]]
        readings = [r for row in items for r in row["survey_readings"]]
        summary[variant] = {
            "net_mean": float(np.mean(net)), "net_lower_10_mean": lower_tail_mean(net),
            "grain_mean": float(np.mean([r["harvested_grain_kg_ha"] for r in items])),
            "sprays_mean": float(np.mean([r["sprays"] for r in items])),
            "sprays_distribution": {str(k): int(sum(r["sprays"] == k for r in items)) for k in range(5)},
            "spray_day_percentiles": [float(np.percentile(days, q)) for q in (5, 50, 95)] if days else None,
            "mean_density": float(np.mean([r["mean_density"] for r in items])),
            "peak_density_mean": float(np.mean([r["peak_density"] for r in items])),
            "peak_density_p95": float(np.percentile([r["peak_density"] for r in items], 95)),
            "applied_leaf_fraction_sum_mean": float(np.mean([r["applied_leaf_fraction_sum"] for r in items])),
            "survey_reading_share_at_or_above_0.3": float(np.mean([r >= 0.3 for r in readings])) if readings else None,
            "survey_reading_percentiles": [float(np.percentile(readings, q)) for q in (50, 90, 99)] if readings else None,
        }
    write_json(run / "verification.json", {"passed": True, "split": "validation", "first_season": args.first_season,
                                           "summary": summary, "final_test_split_used": False, "research_ready": False})
    for variant, value in summary.items():
        print(variant, value, flush=True)


if __name__ == "__main__":
    main()
