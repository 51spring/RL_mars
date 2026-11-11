"""Coordinate search for stage-specific rule irrigation, on validation seasons without reduction.

Tuning and confirmation seasons do not overlap. Reduction conditions are reported only and
never enter the objective. The configuration file is not modified.
"""
import argparse
import ast
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
from mars_env.baseline_evaluation import evaluate_episode
from mars_env.comparison import lower_tail_mean
from mars_env.experimental_env import ExperimentalPestEnv
from mars_env.exogenous import evaluation_conditions, generate_season
from mars_env.pests import pest_settings
from mars_env.policies import RulePolicy
from mars_env.process_backend import LegacyProcessBackend
from mars_env.resources import ResourceRules

PARAMETERS, NOISE = pest_settings(yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8")))
STAGES = (3, 4, 5)
THRESHOLDS = (0.1, 0.2, 0.3, 0.4, 0.5)
AMOUNTS = (5, 10, 15, 20)
START = ((0.3, 10), (0.3, 10), (0.3, 10))


def episode(job):
    season_id, setting, condition, config = job
    rules, price = ResourceRules.from_config(config), config["economics"]["grain_usd_kg"]
    policy = replace(RulePolicy.from_config(config),
                     stage_water=tuple((stage, *value) for stage, value in zip(STAGES, setting)))
    shock = evaluation_conditions(config)[condition]
    season = generate_season(config, split="validation", season_id=season_id).with_condition(beta=1.0, shock=shock)
    env = ExperimentalPestEnv(season=season, parameters=PARAMETERS, noise_std=NOISE, rules=rules, grain_price=price,
                              backend_factory=partial(LegacyProcessBackend, mode="experimental_pest", season=season,
                                                      parameters=PARAMETERS, noise_std=NOISE))
    try:
        result = evaluate_episode(env, policy, season, rules, price, reset_options={})["episode_result"]
    finally:
        env.close()
    return {"season_id": season_id, "condition": condition, **result}


def run_setting(pool, setting, seasons, condition, config):
    return list(pool.map(episode, [(season, setting, condition, config) for season in seasons], chunksize=2))


def stats(rows):
    net = [row["net_return"] for row in rows]
    return {"mean": float(np.mean(net)), "lower_10_mean": lower_tail_mean(net),
            "water_mm": float(np.mean([row["water_mm"] for row in rows])),
            "grain": float(np.mean([row["harvested_grain_kg_ha"] for row in rows])),
            "failures": int(sum(row["reason"] == "crop_failure" for row in rows))}


def paired_interval(a, b, replicates=10000, seed=0):
    difference = np.array([y["net_return"] - x["net_return"] for x, y in zip(a, b)], float)
    rng = np.random.default_rng(seed)
    draws = difference[rng.integers(0, difference.size, (replicates, difference.size))].mean(axis=1)
    return {"mean_difference": float(difference.mean()), "ci95": [float(x) for x in np.percentile(draws, (2.5, 97.5))]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tune-seasons", type=int, default=40)
    parser.add_argument("--confirm-seasons", type=int, default=80)
    parser.add_argument("--condition-seasons", type=int, default=40)
    parser.add_argument("--rounds", type=int, default=2)
    parser.add_argument("--start", type=ast.literal_eval, default=START, help="((thr, mm), (thr, mm), (thr, mm))")
    parser.add_argument("--thresholds", type=float, nargs="+", default=list(THRESHOLDS))
    parser.add_argument("--amounts", type=float, nargs="+", default=list(AMOUNTS))
    parser.add_argument("--tune-first", type=int, default=4000)
    parser.add_argument("--confirm-first", type=int, default=4100)
    args = parser.parse_args()
    start = tuple(tuple(value) for value in args.start)
    thresholds, amounts = tuple(args.thresholds), tuple(args.amounts)
    config = yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8"))
    run = new_run(ROOT, "rule_baseline_search")
    os.environ["MARS_RUN_DIR"] = str(run)
    print("RUN_DIR=" + str(run), flush=True)
    tune = list(range(args.tune_first, args.tune_first + args.tune_seasons))
    confirm = list(range(args.confirm_first, args.confirm_first + args.confirm_seasons))
    assert not set(tune) & set(confirm)
    with ProcessPoolExecutor(max_workers=4, mp_context=get_context("fork")) as pool:
        scores, history = {}, []

        def score(setting):
            if setting not in scores:
                scores[setting] = stats(run_setting(pool, setting, tune, "none", config))
                write_json(run / "status.json", {"evaluated_settings": len(scores)})
                print("SCORE", setting, round(scores[setting]["mean"], 2), flush=True)
            return scores[setting]["mean"]

        best = start
        for round_index in range(args.rounds):
            before = best
            for position in range(len(STAGES)):
                for field, options in ((0, thresholds), (1, amounts)):
                    candidates = []
                    for option in options:
                        value = list(best[position])
                        value[field] = option
                        candidates.append(best[:position] + (tuple(value),) + best[position + 1:])
                    best = max(candidates + [best], key=score)
                    history.append({"round": round_index, "stage": STAGES[position], "field": field, "best": best})
            if best == before:
                break
        if best == start:
            write_json(run / "verification.json", {"passed": True, "split": "validation", "tune_seasons": tune,
                       "start": start, "best": best, "changed": False, "history": history,
                       "tune_scores": [{"setting": key, **value} for key, value in scores.items()],
                       "thresholds": thresholds, "amounts": amounts, "final_test_split_used": False, "research_ready": False})
            print("BEST unchanged", best, scores[best], flush=True)
            return
        base_rows = run_setting(pool, start, confirm, "none", config)
        best_rows = run_setting(pool, best, confirm, "none", config)
        conditions = [name for name in evaluation_conditions(config) if name != "none"]
        subset = confirm[:args.condition_seasons]
        reduction = {}
        for condition in conditions:
            start_rows = run_setting(pool, start, subset, condition, config)
            tuned_rows = run_setting(pool, best, subset, condition, config)
            reduction[condition] = {"current": stats(start_rows), "tuned": stats(tuned_rows),
                                    "paired": paired_interval(start_rows, tuned_rows)}
    report = {"passed": True, "split": "validation", "tune_seasons": tune, "confirm_seasons": confirm,
              "start": start, "best": best, "changed": True, "stages": STAGES, "history": history,
              "thresholds": thresholds, "amounts": amounts,
              "tune_scores": [{"setting": key, **value} for key, value in scores.items()],
              "confirm": {"current": stats(base_rows), "tuned": stats(best_rows),
                          "paired": paired_interval(base_rows, best_rows)},
              "reduction_report_only": reduction, "final_test_split_used": False, "research_ready": False}
    write_json(run / "verification.json", report)
    print("BEST", best, "TUNE", scores[best], flush=True)
    print("CONFIRM", report["confirm"], flush=True)
    for condition, value in reduction.items():
        print(condition, round(value["current"]["mean"], 1), round(value["tuned"]["mean"], 1), value["paired"], flush=True)


if __name__ == "__main__":
    main()
