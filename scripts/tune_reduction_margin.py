"""Choose the reduction-response rule's demand margin on validation seasons, then confirm.

The margin scales the expected remaining demand below which the reserve applies. Objective: mean
net return over the nine reduction conditions on the tuning seasons. Confirmation seasons do not
overlap. The configuration file is not modified.
"""
import argparse
import copy
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
import os
from pathlib import Path
import sys

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
from evaluate_reduction_rule import evaluate
from mars_env.artifacts import new_run, write_json
from mars_env.comparison import lower_tail_mean
from mars_env.exogenous import evaluation_conditions

MARGINS = (0.6, 0.7, 0.8, 0.9, 1.0)


def with_margin(config, margin):
    variant = copy.deepcopy(config)
    variant["reduction_response_rule"]["demand_margin"] = margin
    return variant


def summary(rows, conditions):
    by_condition = {c: [r["net_return"] for r in rows if r["condition"] == c] for c in conditions}
    return {"mean": float(np.mean([np.mean(v) for v in by_condition.values()])),
            "lower_10_mean": float(np.mean([lower_tail_mean(v) for v in by_condition.values()])),
            "by_condition": {c: float(np.mean(v)) for c, v in by_condition.items()}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tune-seasons", type=int, default=40)
    parser.add_argument("--confirm-seasons", type=int, default=40)
    parser.add_argument("--tune-first", type=int, default=3100)
    parser.add_argument("--confirm-first", type=int, default=3200)
    parser.add_argument("--margins", type=float, nargs="+", default=list(MARGINS))
    args = parser.parse_args()
    margins = tuple(args.margins)
    config = yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8"))
    run = new_run(ROOT, "reduction_margin_tuning")
    os.environ["MARS_RUN_DIR"] = str(run)
    print("RUN_DIR=" + str(run), flush=True)
    conditions = [c for c in evaluation_conditions(config) if c != "none"]
    tune = list(range(args.tune_first, args.tune_first + args.tune_seasons))
    confirm = list(range(args.confirm_first, args.confirm_first + args.confirm_seasons))
    assert not set(tune) & set(confirm)
    with ProcessPoolExecutor(max_workers=4, mp_context=get_context("fork")) as pool:
        def run_rows(seasons, name, margin):
            variant = with_margin(config, margin)
            return list(pool.map(evaluate, [(s, c, name, variant) for s in seasons for c in conditions], chunksize=4))

        scores = {}
        for margin in margins:
            scores[margin] = summary(run_rows(tune, "response", margin), conditions)
            print("TUNE", margin, round(scores[margin]["mean"], 2), round(scores[margin]["lower_10_mean"], 2), flush=True)
        best = max(margins, key=lambda m: scores[m]["mean"])
        rule = summary(run_rows(confirm, "rule", best), conditions)
        response = summary(run_rows(confirm, "response", best), conditions)
    report = {"passed": True, "split": "validation", "tune_seasons": tune, "confirm_seasons": confirm,
              "margins": margins, "tune": {str(m): v for m, v in scores.items()}, "selected_margin": best,
              "confirm": {"rule": rule, "response": response}, "final_test_split_used": False, "research_ready": False}
    write_json(run / "verification.json", report)
    print("BEST", best, flush=True)
    print("CONFIRM rule", round(rule["mean"], 2), round(rule["lower_10_mean"], 2), flush=True)
    print("CONFIRM response", round(response["mean"], 2), round(response["lower_10_mean"], 2), flush=True)
    for c in conditions:
        print(c, round(rule["by_condition"][c], 1), round(response["by_condition"][c], 1), flush=True)


if __name__ == "__main__":
    main()
