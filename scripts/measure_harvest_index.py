"""Harvest index of the rule policy (validation only): harvested dry grain / above-ground biomass at maturity.

Evidence for the reward-shaping coefficient eta, which multiplies above-ground biomass to value the
expected grain. No reduction, budget multiplier 1.0.
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
from mars_env.artifacts import new_run, write_json
from mars_env.experimental_env import ExperimentalPestEnv
from mars_env.exogenous import generate_season
from mars_env.pests import pest_settings
from mars_env.policies import RulePolicy
from mars_env.process_backend import LegacyProcessBackend
from mars_env.resources import ResourceRules

CONFIG = yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8"))
PARAMETERS, NOISE = pest_settings(CONFIG)


def episode(season_id):
    rules, price = ResourceRules.from_config(CONFIG), CONFIG["economics"]["grain_usd_kg"]
    rule = RulePolicy.from_config(CONFIG)
    season = generate_season(CONFIG, split="validation", season_id=season_id).with_condition(beta=1.0, shock=None)
    env = ExperimentalPestEnv(season=season, parameters=PARAMETERS, noise_std=NOISE, rules=rules, grain_price=price,
                              backend_factory=partial(LegacyProcessBackend, mode="experimental_pest", season=season,
                                                      parameters=PARAMETERS, noise_std=NOISE))
    peak_topwt = 0.0
    try:
        observation, _ = env.reset()
        while True:
            action = rule.action(observation, env.action_masks().copy(), rules)
            observation, _, terminated, truncated, info = env.step(action)
            peak_topwt = max(peak_topwt, float(env.state["topwt"]))
            assert not truncated
            if terminated:
                result = info["episode_result"]
                final_topwt = float(env.state["topwt"])
                break
    finally:
        env.close()
    grain = result["harvested_grain_kg_ha"]
    return {"season_id": season_id, "grain": grain, "final_topwt": final_topwt, "peak_topwt": peak_topwt,
            "hi_final": grain / final_topwt if final_topwt else None, "hi_peak": grain / peak_topwt if peak_topwt else None}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seasons", type=int, default=40)
    parser.add_argument("--first-season", type=int, default=1300)
    args = parser.parse_args()
    run = new_run(ROOT, "harvest_index")
    os.environ["MARS_RUN_DIR"] = str(run)
    print("RUN_DIR=" + str(run), flush=True)
    with ProcessPoolExecutor(max_workers=4, mp_context=get_context("fork")) as pool:
        rows = list(pool.map(episode, range(args.first_season, args.first_season + args.seasons)))
    summary = {key: {"mean": float(np.mean([r[key] for r in rows])), "p05": float(np.percentile([r[key] for r in rows], 5)),
                     "p95": float(np.percentile([r[key] for r in rows], 95))} for key in ("hi_final", "hi_peak", "grain", "final_topwt")}
    write_json(run / "verification.json", {"passed": True, "split": "validation", "rows": rows, "summary": summary,
                                           "current_eta": CONFIG["reward_shaping"]["eta_by_stage"][1],
                                           "final_test_split_used": False, "research_ready": False})
    print(summary, flush=True)


if __name__ == "__main__":
    main()
