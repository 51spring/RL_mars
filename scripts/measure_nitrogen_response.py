"""Yield and return of the rule policy across seasonal nitrogen schedules (validation only).

Irrigation and spraying follow the configured rule, supply is the configured water, there is no
reduction, and the nitrogen budget is lifted so that every schedule can be applied in full.
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
from mars_env.economics import grain_price
from mars_env.artifacts import new_run, write_json
from mars_env.comparison import lower_tail_mean
from mars_env.experimental_env import ExperimentalPestEnv
from mars_env.exogenous import generate_season
from mars_env.pests import pest_settings
from mars_env.policies import RulePolicy
from mars_env.process_backend import LegacyProcessBackend
from mars_env.resources import ResourceRules

PARAMETERS, NOISE = pest_settings(yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8")))
SCHEDULES = {
    "0": (),
    "57": ((45, 27), (65, 20), (85, 10)),
    "116 (current)": ((45, 54), (65, 35), (85, 27)),
    "116 (old 40-45-80)": ((40, 27), (45, 35), (80, 54)),
    "174": ((45, 80), (65, 54), (85, 40)),
    "240": ((45, 80), (65, 80), (85, 80)),
}


def measure(job):
    season_id, name, config = job
    rules = replace(ResourceRules.from_config(config), nitrogen_budget=10000.0)
    price = grain_price(config)
    rule = replace(RulePolicy.from_config(config), baseline_nitrogen=SCHEDULES[name])
    season = generate_season(config, split="validation", season_id=season_id).with_condition(beta=1.0, shock=None)
    env = ExperimentalPestEnv(season=season, parameters=PARAMETERS, noise_std=NOISE, rules=rules, grain_price=price,
                              backend_factory=partial(LegacyProcessBackend, mode="experimental_pest", season=season,
                                                      parameters=PARAMETERS, noise_std=NOISE))
    try:
        observation, _ = env.reset()
        stress = []
        while True:
            stress.append(float(env.state["nstres"]))
            action = rule.action(observation, env.action_masks().copy(), rules)
            observation, _, terminated, truncated, info = env.step(action)
            assert not truncated
            if terminated:
                result = info["episode_result"]
                break
    finally:
        env.close()
    return {"season_id": season_id, "schedule": name, "mean_nstres": float(np.mean(stress)), **result}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seasons", type=int, default=80)
    parser.add_argument("--first-season", type=int, default=1000)
    args = parser.parse_args()
    config = yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8"))
    run = new_run(ROOT, "nitrogen_response_rule_policy")
    os.environ["MARS_RUN_DIR"] = str(run)
    print("RUN_DIR=" + str(run), flush=True)
    jobs = [(season, name, config) for season in range(args.first_season, args.first_season + args.seasons)
            for name in SCHEDULES]
    with ProcessPoolExecutor(max_workers=4, mp_context=get_context("fork")) as pool:
        rows = list(pool.map(measure, jobs, chunksize=4))
    write_json(run / "seasons.json", rows)
    summary = {}
    for name in SCHEDULES:
        items = [row for row in rows if row["schedule"] == name]
        net = [row["net_return"] for row in items]
        summary[name] = {"seasons": len(items), "nitrogen_kg_ha": float(np.mean([r["nitrogen_kg_ha"] for r in items])),
                         "grain_mean": float(np.mean([r["harvested_grain_kg_ha"] for r in items])),
                         "grain_p05": float(np.percentile([r["harvested_grain_kg_ha"] for r in items], 5)),
                         "net_mean": float(np.mean(net)), "net_lower_10_mean": lower_tail_mean(net),
                         "water_mm": float(np.mean([r["water_mm"] for r in items])),
                         "mean_nstres": float(np.mean([r["mean_nstres"] for r in items])),
                         "failure_rate": float(np.mean([r["reason"] == "crop_failure" for r in items]))}
    write_json(run / "verification.json", {"passed": True, "split": "validation", "first_season": args.first_season,
                                           "schedules": {k: list(map(list, v)) for k, v in SCHEDULES.items()},
                                           "summary": summary, "nitrogen_budget_lifted": True,
                                           "final_test_split_used": False, "research_ready": False})
    for name, value in summary.items():
        print(name, {key: round(number, 3) for key, number in value.items()}, flush=True)


if __name__ == "__main__":
    main()
