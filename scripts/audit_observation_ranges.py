"""Actual ranges of the 45 policy observation fields on validation seasons.

Runs the rule policy (none, early_40, late_60) and a no-input policy (none) through the experimental pest
environment, and records each field's raw value (scaled value x fixed scale) on every decision morning.
Reports min, max, percentiles, share of scaled values above 1, distinct values and constant fields, and
checks dap against season_day. Validation split only; no final test access.
"""
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
from mars_env.exogenous import evaluation_conditions, generate_season
from mars_env.observations import FIELDS
from mars_env.pests import pest_settings
from mars_env.policies import RulePolicy
from mars_env.process_backend import LegacyProcessBackend
from mars_env.resources import ResourceRules

SEASONS = tuple(range(4500, 4520))
JOBS = [("rule", c) for c in ("none", "early_40", "late_60")] + [("no_input", "none")]


def run(job):
    policy_name, condition, season_id = job
    config = yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8"))
    parameters, noise = pest_settings(config)
    rules, price = ResourceRules.from_config(config), config["economics"]["grain_usd_kg"]
    rule = RulePolicy.from_config(config)
    season = generate_season(config, split="validation", season_id=season_id).with_condition(
        beta=1.0, shock=evaluation_conditions(config)[condition])
    env = ExperimentalPestEnv(season=season, parameters=parameters, noise_std=noise, rules=rules, grain_price=price,
                              backend_factory=partial(LegacyProcessBackend, mode="experimental_pest", season=season,
                                                      parameters=parameters, noise_std=noise))
    frames = []
    try:
        obs, _ = env.reset()
        for _ in range(240):
            frames.append(obs[-len(FIELDS):].copy())
            mask = env.action_masks()
            action = rule.action(obs, mask.copy(), rules) if policy_name == "rule" else (0, 0, 0)
            obs, _, terminated, truncated, _ = env.step(action)
            if terminated or truncated:
                frames.append(obs[-len(FIELDS):].copy())
                break
    finally:
        env.close()
    return policy_name, condition, np.asarray(frames)


def main():
    run_dir = new_run(ROOT, "observation_ranges")
    os.environ["MARS_RUN_DIR"] = str(run_dir)
    print("RUN_DIR=" + str(run_dir), flush=True)
    jobs = [(p, c, s) for p, c in JOBS for s in SEASONS]
    with ProcessPoolExecutor(max_workers=8, mp_context=get_context("fork")) as pool:
        results = list(pool.map(run, jobs))
    scales = np.asarray([s for _, s in FIELDS], dtype=float)
    everything = np.concatenate([f for _, _, f in results]) * scales
    report = {}
    for i, (name, scale) in enumerate(FIELDS):
        v = everything[:, i]
        by_group = {f"{p}|{c}": [float(np.min(f[:, i] * scale)), float(np.max(f[:, i] * scale))]
                    for p, c in JOBS for f in [np.concatenate([x for pp, cc, x in results if (pp, cc) == (p, c)])]}
        report[name] = {"scale": scale, "min": float(v.min()), "p1": float(np.percentile(v, 1)),
                        "mean": float(v.mean()), "p99": float(np.percentile(v, 99)), "max": float(v.max()),
                        "share_scaled_above_1": float(np.mean(np.abs(v / scale) > 1)),
                        "max_scaled": float(np.max(np.abs(v / scale))), "distinct": int(len(np.unique(np.round(v, 6)))),
                        "constant": bool(np.ptp(v) == 0), "by_group_min_max": by_group}
        print(f"{name:26s} scale {scale:>9g} min {v.min():10.4g} p1 {report[name]['p1']:10.4g} "
              f"mean {v.mean():10.4g} p99 {report[name]['p99']:10.4g} max {v.max():10.4g} "
              f">1 {report[name]['share_scaled_above_1']:.3f} distinct {report[name]['distinct']}", flush=True)
    names = [n for n, _ in FIELDS]
    duplicate = None
    if "season_day" in names:
        dap, day = everything[:, names.index("dap")], everything[:, names.index("season_day")]
        duplicate = {"dap_equals_season_day_share": float(np.mean(dap == day)),
                     "max_abs_difference": float(np.max(np.abs(dap - day)))}
        print("DAP_VS_SEASON_DAY", duplicate, flush=True)
    with np.errstate(invalid="ignore", divide="ignore"):
        corr = np.corrcoef(everything.T)
    size = len(names)
    pairs = sorted(((abs(corr[a, b]), names[a], names[b]) for a in range(size) for b in range(a + 1, size)
                    if np.isfinite(corr[a, b]) and abs(corr[a, b]) > 0.98), reverse=True)
    print("HIGH_CORRELATION", [(round(c, 4), a, b) for c, a, b in pairs], flush=True)
    write_json(run_dir / "verification.json", {"passed": True, "split": "validation", "seasons": list(SEASONS),
                                               "groups": [f"{p}|{c}" for p, c in JOBS], "frames": int(len(everything)),
                                               "fields": report, "dap_vs_season_day": duplicate,
                                               "high_correlation": [[c, a, b] for c, a, b in pairs],
                                               "final_test_split_used": False, "research_ready": False})


if __name__ == "__main__":
    main()
