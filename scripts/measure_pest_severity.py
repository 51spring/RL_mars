"""Untreated defoliation severity for candidate leaf-loss coefficients (validation only).

Severity on a day = 1 - LAI(untreated) / LAI(pest-free twin) while the twin's LAI is at least 0.5.
Pre-stated selection: the candidate whose median seasonal peak severity is closest to 25 %,
among candidates with at most 10 % of seasons above 50 % (Hruska 2019 as cited by Abang 2024).
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

ALPHAS = (0.03, 0.02, 0.015, 0.01, 0.0075, 0.005)


def episode(job):
    season_id, alpha, config = job
    base_parameters, noise = pest_settings(config)
    parameters = base_parameters if alpha is None else replace(base_parameters, alpha=alpha)
    rules, price = ResourceRules.from_config(config), config["economics"]["grain_usd_kg"]
    rule = RulePolicy.from_config(config)
    season = generate_season(config, split="validation", season_id=season_id).with_condition(beta=1.0, shock=None)
    if alpha is None:
        season = replace(season, pest_arrivals=np.zeros_like(season.pest_arrivals))
    env = ExperimentalPestEnv(season=season, parameters=parameters, noise_std=noise, rules=rules, grain_price=price,
                              backend_factory=partial(LegacyProcessBackend, mode="experimental_pest", season=season,
                                                      parameters=parameters, noise_std=noise))
    lai = []
    try:
        observation, _ = env.reset()
        while True:
            action = rule.action(observation, env.action_masks().copy(), rules)
            action[2] = 0
            observation, _, terminated, truncated, info = env.step(action)
            lai.append(float(env.state["xlai"]))
            assert not truncated
            if terminated:
                result = info["episode_result"]
                break
    finally:
        env.close()
    return {"season_id": season_id, "alpha": alpha, "lai": lai, "grain": result["harvested_grain_kg_ha"],
            "net": result["net_return"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seasons", type=int, default=40)
    parser.add_argument("--first-season", type=int, default=1100)
    args = parser.parse_args()
    config = yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8"))
    run = new_run(ROOT, "pest_severity_alpha")
    os.environ["MARS_RUN_DIR"] = str(run)
    print("RUN_DIR=" + str(run), flush=True)
    seasons = range(args.first_season, args.first_season + args.seasons)
    jobs = [(s, a, config) for s in seasons for a in (None, *ALPHAS)]
    with ProcessPoolExecutor(max_workers=4, mp_context=get_context("fork")) as pool:
        rows = list(pool.map(episode, jobs, chunksize=2))
    free = {r["season_id"]: r for r in rows if r["alpha"] is None}
    summary = {}
    for alpha in ALPHAS:
        peaks, means, losses = [], [], []
        for row in (r for r in rows if r["alpha"] == alpha):
            twin = free[row["season_id"]]
            n = min(len(twin["lai"]), len(row["lai"]))
            severity = [1 - row["lai"][i] / twin["lai"][i] for i in range(n) if twin["lai"][i] >= 0.5]
            peaks.append(max(severity))
            means.append(float(np.mean(severity)))
            losses.append(1 - row["grain"] / twin["grain"])
        summary[str(alpha)] = {"peak_severity_median": float(np.median(peaks)),
                               "peak_severity_p90": float(np.percentile(peaks, 90)),
                               "share_peak_above_50pct": float(np.mean(np.array(peaks) > 0.5)),
                               "mean_severity_median": float(np.median(means)),
                               "yield_loss_median": float(np.median(losses)),
                               "yield_loss_p90": float(np.percentile(losses, 90)),
                               "share_yield_loss_above_20pct": float(np.mean(np.array(losses) > 0.2))}
    eligible = [a for a in ALPHAS if summary[str(a)]["share_peak_above_50pct"] <= 0.10]
    selected = min(eligible, key=lambda a: abs(summary[str(a)]["peak_severity_median"] - 0.25)) if eligible else None
    write_json(run / "verification.json", {"passed": selected is not None, "selected_alpha": selected,
                                           "rule": "median peak severity closest to 25% with <=10% of seasons above 50%",
                                           "summary": summary, "pest_free_grain_mean": float(np.mean([r["grain"] for r in free.values()])),
                                           "split": "validation", "final_test_split_used": False, "research_ready": False})
    for alpha, value in summary.items():
        print(alpha, {k: round(v, 3) for k, v in value.items()}, flush=True)
    print("SELECTED", selected, flush=True)


if __name__ == "__main__":
    main()
