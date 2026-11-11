"""Rule policy against the reduction-response rule on the nine reduction conditions (validation only)."""
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
from mars_env.comparison import lower_tail_mean
from mars_env.experimental_env import ExperimentalPestEnv
from mars_env.exogenous import evaluation_conditions, generate_season
from mars_env.pests import pest_settings
from mars_env.policies import ReductionResponseRule, RulePolicy
from mars_env.process_backend import LegacyProcessBackend
from mars_env.resources import ResourceRules

PARAMETERS, NOISE = pest_settings(yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8")))


def evaluate(job):
    season_id, condition, name, config = job
    rules, price = ResourceRules.from_config(config), grain_price(config)
    policy = RulePolicy.from_config(config) if name == "rule" else ReductionResponseRule.from_config(config)
    season = generate_season(config, split="validation", season_id=season_id).with_condition(
        beta=config["scenarios"]["evaluation_beta"], shock=evaluation_conditions(config)[condition])
    env = ExperimentalPestEnv(season=season, parameters=PARAMETERS, noise_std=NOISE, rules=rules, grain_price=price,
                              backend_factory=partial(LegacyProcessBackend, mode="experimental_pest", season=season,
                                                      parameters=PARAMETERS, noise_std=NOISE))
    try:
        result = evaluate_episode(env, policy, season, rules, price, reset_options={})["episode_result"]
    finally:
        env.close()
    return {"season_id": season_id, "condition": condition, "policy": name, **result}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seasons", type=int, default=40)
    parser.add_argument("--first-season", type=int, default=3000)
    args = parser.parse_args()
    config = yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8"))
    run = new_run(ROOT, "reduction_rule_comparison")
    os.environ["MARS_RUN_DIR"] = str(run)
    print("RUN_DIR=" + str(run), flush=True)
    conditions = [name for name in evaluation_conditions(config) if name != "none"]
    jobs = [(season, condition, name, config) for season in range(args.first_season, args.first_season + args.seasons)
            for condition in conditions for name in ("rule", "response")]
    with ProcessPoolExecutor(max_workers=4, mp_context=get_context("fork")) as pool:
        rows = list(pool.map(evaluate, jobs, chunksize=4))
    write_json(run / "seasons.json", rows)
    summary = {}
    for condition in conditions:
        summary[condition] = {}
        for name in ("rule", "response"):
            net = [row["net_return"] for row in rows if row["condition"] == condition and row["policy"] == name]
            summary[condition][name] = {"mean": float(np.mean(net)), "lower_10_mean": lower_tail_mean(net)}
    overall = {name: {key: float(np.mean([summary[c][name][key] for c in conditions])) for key in ("mean", "lower_10_mean")}
               for name in ("rule", "response")}
    write_json(run / "verification.json", {"passed": True, "split": "validation", "seasons": args.seasons, "first_season": args.first_season,
                                           "by_condition": summary, "nine_condition_mean": overall,
                                           "final_test_split_used": False, "research_ready": False})
    for condition, value in summary.items():
        print(condition, {name: (round(item["mean"], 1), round(item["lower_10_mean"], 1)) for name, item in value.items()}, flush=True)
    print("overall", overall, flush=True)


if __name__ == "__main__":
    main()
