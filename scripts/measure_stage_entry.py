"""Growth-stage entry days and stage irrigation of the rule policy on validation seasons.

Evidence for the reduction calendar (training window, three evaluation days) and for
the reserve of the reduction-response rule. No reduction, budget multiplier 1.0.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from multiprocessing import get_context
import os
from pathlib import Path
import sys

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from mars_env.economics import grain_price
from mars_env.artifacts import new_run, write_json
from mars_env.baseline_evaluation import evaluate_episode
from mars_env.experimental_env import ExperimentalPestEnv
from mars_env.exogenous import generate_season
from mars_env.pests import pest_settings
from mars_env.policies import RulePolicy
from mars_env.process_backend import LegacyProcessBackend
from mars_env.resources import ResourceRules

PARAMETERS, NOISE = pest_settings(yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8")))
STAGES = (9, 1, 2, 3, 4, 5, 6)


def measure(args):
    season_id, config = args
    rules = ResourceRules.from_config(config)
    price = grain_price(config)
    rule = RulePolicy.from_config(config)
    season = generate_season(config, split="validation", season_id=season_id).with_condition(beta=1.0, shock=None)
    env = ExperimentalPestEnv(season=season, parameters=PARAMETERS, noise_std=NOISE, rules=rules, grain_price=price,
                              backend_factory=partial(LegacyProcessBackend, mode="experimental_pest", season=season,
                                                      parameters=PARAMETERS, noise_std=NOISE))
    try:
        row = evaluate_episode(env, rule, season, rules, price, reset_options={}, record_decision_context=True)
    finally:
        env.close()
    entry, water = {}, {}
    for day in row["daily_tape"]:
        stage = day["istage"]
        entry.setdefault(stage, day["decision_day"])
        amount = rules.water_grid[day["action_indices"][0]]
        water.setdefault(stage, []).append(amount)
    return {"season_id": season_id, "entry": entry, "steps": row["steps"], "reason": row["episode_result"]["reason"],
            "water_mm": row["episode_result"]["water_mm"],
            "stage_water": {stage: float(sum(values)) for stage, values in water.items()},
            "stage_events": {stage: sum(value > 0 for value in values) for stage, values in water.items()}}


def describe(values):
    values = np.asarray(values, dtype=float)
    return {"n": int(values.size), "mean": float(values.mean()), "sd": float(values.std(ddof=1)),
            "min": float(values.min()), "p05": float(np.percentile(values, 5)), "p50": float(np.percentile(values, 50)),
            "p95": float(np.percentile(values, 95)), "max": float(values.max())}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seasons", type=int, default=120)
    parser.add_argument("--first-season", type=int, default=1000)
    args = parser.parse_args()
    config = yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8"))
    run = new_run(ROOT, "stage_entry_rule_policy")
    os.environ["MARS_RUN_DIR"] = str(run)
    print("RUN_DIR=" + str(run), flush=True)
    jobs = [(season, config) for season in range(args.first_season, args.first_season + args.seasons)]
    with ProcessPoolExecutor(max_workers=4, mp_context=get_context("fork")) as pool:
        rows = list(pool.map(measure, jobs))
    entry = {stage: describe([row["entry"][stage] for row in rows if stage in row["entry"]]) for stage in STAGES}
    water = {stage: describe([row["stage_water"].get(stage, 0.0) for row in rows]) for stage in (1, 2, 3, 4, 5)}
    events = {stage: describe([row["stage_events"].get(stage, 0) for row in rows]) for stage in (1, 2, 3, 4, 5)}
    report = {"passed": True, "split": "validation", "first_season": args.first_season, "seasons": len(rows),
              "failures": sum(row["reason"] == "crop_failure" for row in rows),
              "entry_day_after_planting": entry, "stage_irrigation_mm": water, "stage_irrigation_events": events,
              "season_length": describe([row["steps"] for row in rows]),
              "season_water_mm": describe([row["water_mm"] for row in rows]),
              "final_test_split_used": False, "research_ready": False}
    write_json(run / "seasons.json", rows)
    write_json(run / "verification.json", report)
    print(report, flush=True)


if __name__ == "__main__":
    main()
