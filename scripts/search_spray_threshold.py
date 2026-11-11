"""Choose the rule policy's survey threshold for spraying on validation seasons, then confirm.

Objective: mean net return without reduction on the tuning seasons. Adoption rule (stated before the
run): replace the current threshold only if the paired 95 % interval of the mean difference on the
non-overlapping confirmation seasons lies above zero. Reduction conditions are reported only.
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
from mars_env.baseline_evaluation import evaluate_episode
from mars_env.comparison import lower_tail_mean
from mars_env.experimental_env import ExperimentalPestEnv
from mars_env.exogenous import evaluation_conditions, generate_season
from mars_env.pests import pest_settings
from mars_env.policies import RulePolicy
from mars_env.process_backend import LegacyProcessBackend
from mars_env.resources import ResourceRules

CONFIG = yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8"))
PARAMETERS, NOISE = pest_settings(CONFIG)
THRESHOLDS = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8)


def episode(job):
    season_id, threshold, condition = job
    rules, price = ResourceRules.from_config(CONFIG), grain_price(CONFIG)
    policy = replace(RulePolicy.from_config(CONFIG), survey_threshold=threshold)
    season = generate_season(CONFIG, split="validation", season_id=season_id).with_condition(
        beta=1.0, shock=evaluation_conditions(CONFIG)[condition])
    env = ExperimentalPestEnv(season=season, parameters=PARAMETERS, noise_std=NOISE, rules=rules, grain_price=price,
                              backend_factory=partial(LegacyProcessBackend, mode="experimental_pest", season=season,
                                                      parameters=PARAMETERS, noise_std=NOISE))
    try:
        result = evaluate_episode(env, policy, season, rules, price, reset_options={})["episode_result"]
    finally:
        env.close()
    return {"season_id": season_id, "threshold": threshold, "condition": condition, **result}


def stats(rows):
    net = [r["net_return"] for r in rows]
    return {"mean": float(np.mean(net)), "lower_10_mean": lower_tail_mean(net),
            "sprays": float(np.mean([r["sprays"] for r in rows])),
            "grain": float(np.mean([r["harvested_grain_kg_ha"] for r in rows]))}


def paired(a, b, replicates=10000, seed=0):
    d = np.array([y["net_return"] - x["net_return"] for x, y in zip(a, b)], float)
    draws = d[np.random.default_rng(seed).integers(0, d.size, (replicates, d.size))].mean(axis=1)
    return {"mean_difference": float(d.mean()), "ci95": [float(x) for x in np.percentile(draws, (2.5, 97.5))]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tune-first", type=int, default=4000)
    parser.add_argument("--tune-seasons", type=int, default=40)
    parser.add_argument("--confirm-first", type=int, default=4400)
    parser.add_argument("--confirm-seasons", type=int, default=80)
    parser.add_argument("--condition-seasons", type=int, default=40)
    args = parser.parse_args()
    current = CONFIG["baseline_policy"]["survey_threshold"]
    run = new_run(ROOT, "spray_threshold_search")
    os.environ["MARS_RUN_DIR"] = str(run)
    print("RUN_DIR=" + str(run), flush=True)
    tune = list(range(args.tune_first, args.tune_first + args.tune_seasons))
    confirm = list(range(args.confirm_first, args.confirm_first + args.confirm_seasons))
    assert not set(tune) & set(confirm)
    with ProcessPoolExecutor(max_workers=4, mp_context=get_context("fork")) as pool:
        def rows(seasons, threshold, condition="none"):
            return list(pool.map(episode, [(s, threshold, condition) for s in seasons], chunksize=2))
        scores = {}
        for threshold in THRESHOLDS:
            scores[threshold] = stats(rows(tune, threshold))
            print("TUNE", threshold, round(scores[threshold]["mean"], 2), round(scores[threshold]["sprays"], 2), flush=True)
        best = max(THRESHOLDS, key=lambda t: scores[t]["mean"])
        report = {"passed": True, "split": "validation", "current": current, "thresholds": THRESHOLDS,
                  "tune_seasons": tune, "tune": {str(t): v for t, v in scores.items()}, "best": best,
                  "final_test_split_used": False, "research_ready": False}
        if best != current:
            base, tuned = rows(confirm, current), rows(confirm, best)
            reduction = {}
            for condition in [c for c in evaluation_conditions(CONFIG) if c != "none"]:
                a, b = rows(confirm[:args.condition_seasons], current, condition), rows(confirm[:args.condition_seasons], best, condition)
                reduction[condition] = {"current": stats(a), "tuned": stats(b), "paired": paired(a, b)}
            report.update(confirm_seasons=confirm, confirm={"current": stats(base), "tuned": stats(tuned),
                                                            "paired": paired(base, tuned)},
                          reduction_report_only=reduction)
            report["adopt"] = report["confirm"]["paired"]["ci95"][0] > 0
    write_json(run / "verification.json", report)
    print("BEST", best, "ADOPT", report.get("adopt"), flush=True)
    if "confirm" in report:
        print("CONFIRM", report["confirm"], flush=True)
        for condition, value in report["reduction_report_only"].items():
            print(condition, round(value["current"]["mean"], 1), round(value["tuned"]["mean"], 1), value["paired"], flush=True)


if __name__ == "__main__":
    main()
