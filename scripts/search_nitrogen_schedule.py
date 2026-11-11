"""Coordinate search for the rule policy's three nitrogen applications (day and amount).

Validation seasons without reduction; the nitrogen budget is lifted during the search so the
schedule alone decides the total. Tuning and confirmation seasons do not overlap. Reduction
conditions are reported only. The configuration file is not modified.
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
DAYS = ((35, 40, 45, 50, 55), (55, 60, 65, 70, 75), (75, 80, 85, 90, 95))
START = ((45, 54), (65, 35), (85, 27))


def episode(job):
    season_id, schedule, condition, config = job
    rules = replace(ResourceRules.from_config(config), nitrogen_budget=10000.0)
    price = config["economics"]["grain_usd_kg"]
    policy = replace(RulePolicy.from_config(config), baseline_nitrogen=tuple((d, a) for d, a in schedule if a > 0))
    season = generate_season(config, split="validation", season_id=season_id).with_condition(
        beta=1.0, shock=evaluation_conditions(config)[condition])
    env = ExperimentalPestEnv(season=season, parameters=PARAMETERS, noise_std=NOISE, rules=rules, grain_price=price,
                              backend_factory=partial(LegacyProcessBackend, mode="experimental_pest", season=season,
                                                      parameters=PARAMETERS, noise_std=NOISE))
    try:
        result = evaluate_episode(env, policy, season, rules, price, reset_options={})["episode_result"]
    finally:
        env.close()
    return {"season_id": season_id, "condition": condition, **result}


def run_setting(pool, schedule, seasons, condition, config):
    return list(pool.map(episode, [(season, schedule, condition, config) for season in seasons], chunksize=2))


def stats(rows):
    net = [row["net_return"] for row in rows]
    return {"mean": float(np.mean(net)), "lower_10_mean": lower_tail_mean(net),
            "nitrogen_kg_ha": float(np.mean([row["nitrogen_kg_ha"] for row in rows])),
            "water_mm": float(np.mean([row["water_mm"] for row in rows])),
            "grain": float(np.mean([row["harvested_grain_kg_ha"] for row in rows])),
            "failures": int(sum(row["reason"] == "crop_failure" for row in rows))}


def paired_interval(a, b, replicates=10000, seed=0):
    difference = np.array([y["net_return"] - x["net_return"] for x, y in zip(a, b)], float)
    draws = difference[np.random.default_rng(seed).integers(0, difference.size, (replicates, difference.size))].mean(axis=1)
    return {"mean_difference": float(difference.mean()), "ci95": [float(x) for x in np.percentile(draws, (2.5, 97.5))]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tune-seasons", type=int, default=40)
    parser.add_argument("--confirm-seasons", type=int, default=80)
    parser.add_argument("--condition-seasons", type=int, default=40)
    parser.add_argument("--rounds", type=int, default=2)
    parser.add_argument("--start", type=ast.literal_eval, default=START)
    parser.add_argument("--tune-first", type=int, default=4000)
    parser.add_argument("--confirm-first", type=int, default=4300)
    args = parser.parse_args()
    config = yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8"))
    amounts = tuple(config["environment"]["nitrogen_grid_kg_ha"])
    start = tuple(tuple(value) for value in args.start)
    run = new_run(ROOT, "nitrogen_schedule_search")
    os.environ["MARS_RUN_DIR"] = str(run)
    print("RUN_DIR=" + str(run), flush=True)
    tune = list(range(args.tune_first, args.tune_first + args.tune_seasons))
    confirm = list(range(args.confirm_first, args.confirm_first + args.confirm_seasons))
    assert not set(tune) & set(confirm)
    with ProcessPoolExecutor(max_workers=4, mp_context=get_context("fork")) as pool:
        scores, history = {}, []

        def score(schedule):
            if schedule not in scores:
                scores[schedule] = stats(run_setting(pool, schedule, tune, "none", config))
                write_json(run / "status.json", {"evaluated_settings": len(scores)})
                print("SCORE", schedule, round(scores[schedule]["mean"], 2), flush=True)
            return scores[schedule]["mean"]

        best = start
        for round_index in range(args.rounds):
            before = best
            for position in range(3):
                for field, options in ((0, DAYS[position]), (1, amounts)):
                    candidates = []
                    for option in options:
                        value = list(best[position])
                        value[field] = option
                        candidates.append(best[:position] + (tuple(value),) + best[position + 1:])
                    best = max(candidates + [best], key=score)
                    history.append({"round": round_index, "application": position + 1, "field": field, "best": best})
            if best == before:
                break
        result = {"passed": True, "split": "validation", "tune_seasons": tune, "start": start, "best": best,
                  "days": DAYS, "amounts": amounts, "history": history,
                  "tune_scores": [{"schedule": key, **value} for key, value in scores.items()],
                  "nitrogen_budget_lifted": True, "final_test_split_used": False, "research_ready": False}
        if best != start:
            base_rows = run_setting(pool, start, confirm, "none", config)
            best_rows = run_setting(pool, best, confirm, "none", config)
            reduction = {}
            for condition in [name for name in evaluation_conditions(config) if name != "none"]:
                a = run_setting(pool, start, confirm[:args.condition_seasons], condition, config)
                b = run_setting(pool, best, confirm[:args.condition_seasons], condition, config)
                reduction[condition] = {"current": stats(a), "tuned": stats(b), "paired": paired_interval(a, b)}
            result.update(confirm_seasons=confirm, confirm={"current": stats(base_rows), "tuned": stats(best_rows),
                                                            "paired": paired_interval(base_rows, best_rows)},
                          reduction_report_only=reduction)
    write_json(run / "verification.json", result)
    print("BEST", best, scores[best], flush=True)
    if "confirm" in result:
        print("CONFIRM", result["confirm"], flush=True)
        for condition, value in result["reduction_report_only"].items():
            print(condition, round(value["current"]["mean"], 1), round(value["tuned"]["mean"], 1), value["paired"], flush=True)


if __name__ == "__main__":
    main()
