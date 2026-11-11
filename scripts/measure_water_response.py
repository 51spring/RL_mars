"""Yield and crop water use of the rule policy across seasonal irrigation supplies.

Validation seasons only, no mid-season reduction, budget multiplier 1.0. The same seasons
are used at every supply so differences come from the irrigation limit alone.
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
from mars_env.experimental_env import ExperimentalPestEnv
from mars_env.exogenous import generate_season
from mars_env.pests import pest_settings
from mars_env.policies import RulePolicy
from mars_env.process_backend import LegacyProcessBackend
from mars_env.resources import ResourceRules

PARAMETERS, NOISE = pest_settings(yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8")))
SUPPLIES = (0, 20, 40, 60, 80, 100, 120, 160, 200)


def measure(job):
    season_id, supply, config = job
    rules = replace(ResourceRules.from_config(config), initial_water=float(supply))
    price = config["economics"]["grain_usd_kg"]
    rule = RulePolicy.from_config(config)
    season = generate_season(config, split="validation", season_id=season_id).with_condition(beta=1.0, shock=None)
    env = ExperimentalPestEnv(season=season, parameters=PARAMETERS, noise_std=NOISE, rules=rules, grain_price=price,
                              backend_factory=partial(LegacyProcessBackend, mode="experimental_pest", season=season,
                                                      parameters=PARAMETERS, noise_std=NOISE))
    try:
        observation, _ = env.reset()
        rain = transpiration = 0.0
        while True:
            rain += float(env.state["rain"])
            transpiration += float(env.state["ep"])
            action = rule.action(observation, env.action_masks().copy(), rules)
            observation, _, terminated, truncated, info = env.step(action)
            assert not truncated
            if terminated:
                result = info["episode_result"]
                break
    finally:
        env.close()
    return {"season_id": season_id, "supply_mm": supply, "rain_mm": rain, "transpiration_mm": transpiration, **result}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seasons", type=int, default=80)
    parser.add_argument("--first-season", type=int, default=1000)
    args = parser.parse_args()
    config = yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8"))
    run = new_run(ROOT, "water_response_rule_policy")
    os.environ["MARS_RUN_DIR"] = str(run)
    print("RUN_DIR=" + str(run), flush=True)
    jobs = [(season, supply, config) for season in range(args.first_season, args.first_season + args.seasons)
            for supply in SUPPLIES]
    with ProcessPoolExecutor(max_workers=4, mp_context=get_context("fork")) as pool:
        rows = list(pool.map(measure, jobs, chunksize=4))
    write_json(run / "seasons.json", rows)
    summary = {}
    for supply in SUPPLIES:
        items = [row for row in rows if row["supply_mm"] == supply]
        grain = np.array([row["harvested_grain_kg_ha"] for row in items], float)
        net = np.array([row["net_return"] for row in items], float)
        lowest = np.sort(net)[:max(1, int(np.ceil(0.1 * net.size)))]
        summary[supply] = {
            "seasons": len(items), "failure_rate": float(np.mean([row["reason"] == "crop_failure" for row in items])),
            "grain_mean": float(grain.mean()), "grain_p05": float(np.percentile(grain, 5)), "grain_min": float(grain.min()),
            "net_mean": float(net.mean()), "net_lower_10_mean": float(lowest.mean()),
            "water_used_mean": float(np.mean([row["water_mm"] for row in items])),
            "rain_mean": float(np.mean([row["rain_mm"] for row in items])),
            "rain_p05": float(np.percentile([row["rain_mm"] for row in items], 5)),
            "transpiration_mean": float(np.mean([row["transpiration_mm"] for row in items]))}
    write_json(run / "verification.json", {"passed": True, "split": "validation", "first_season": args.first_season,
                                           "summary": summary, "final_test_split_used": False, "research_ready": False})
    for supply, value in summary.items():
        print(supply, {key: round(number, 3) for key, number in value.items()}, flush=True)


if __name__ == "__main__":
    main()
