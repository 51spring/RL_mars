"""Does early irrigation pay more in the training seasons met at 300k-460k steps than elsewhere?

For training seasons sampled from step windows (same reduction draws as training, probability 0.75), compares
the rule policy with the rule policy plus 10 mm per day during stages 1-2 (before stage 3). A larger gain in a
window would show that its seasons reward the early-irrigation drift seen in the pilots. Training split only.
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
from mars_env.economics import grain_price
from mars_env.experimental_env import ExperimentalPestEnv
from mars_env.exogenous import generate_season
from mars_env.pests import pest_settings
from mars_env.policies import RulePolicy
from mars_env.process_backend import LegacyProcessBackend
from mars_env.resources import ResourceRules

STEPS_PER_SEASON = 132.8
WINDOWS = {"100k-300k": (100_000, 300_000), "300k-460k": (300_000, 460_000), "700k-1024k": (700_000, 1_024_000)}
PER_WINDOW = 48


def run(job):
    season_id, early_mm = job
    config = yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8"))
    parameters, noise = pest_settings(config)
    rules, price, rule = ResourceRules.from_config(config), grain_price(config), RulePolicy.from_config(config)
    season = generate_season(config, split="train", season_id=season_id,
                             reduction_probability=config["scenarios"]["reduction_probability"])
    env = ExperimentalPestEnv(season=season, parameters=parameters, noise_std=noise, rules=rules, grain_price=price,
                              backend_factory=partial(LegacyProcessBackend, mode="experimental_pest", season=season,
                                                      parameters=parameters, noise_std=noise))
    try:
        obs, _ = env.reset()
        for _ in range(240):
            mask = env.action_masks()
            action = rule.action(obs, mask.copy(), rules)
            if early_mm and int(env.state["istage"]) in (1, 2):
                action[0] = max(i for i, x in enumerate(rules.water_grid) if x <= early_mm and mask[i])
            obs, _, terminated, truncated, info = env.step(action)
            if terminated or truncated:
                result = info["episode_result"]
                break
    finally:
        env.close()
    shock = season.shock
    return {"season_id": season_id, "early_mm": early_mm, "net_return": result["net_return"],
            "water_mm": result["water_mm"], "cut_day": None if shock is None else shock.day,
            "cut_fraction": None if shock is None else shock.fraction}


def main():
    out = new_run(ROOT, "early_irrigation_value_by_window")
    os.environ["MARS_RUN_DIR"] = str(out)
    print("RUN_DIR=" + str(out), flush=True)
    rng = np.random.default_rng(0)
    samples = {name: sorted(rng.choice(np.arange(int(a / STEPS_PER_SEASON), int(b / STEPS_PER_SEASON)), PER_WINDOW, replace=False).tolist())
               for name, (a, b) in WINDOWS.items()}
    jobs = [(s, mm) for ids in samples.values() for s in ids for mm in (0, 10)]
    with ProcessPoolExecutor(max_workers=8, mp_context=get_context("fork")) as pool:
        rows = list(pool.map(run, jobs))
    report = {}
    for name, ids in samples.items():
        base = {r["season_id"]: r for r in rows if r["season_id"] in ids and r["early_mm"] == 0}
        early = {r["season_id"]: r for r in rows if r["season_id"] in ids and r["early_mm"] == 10}
        gain = np.array([early[s]["net_return"] - base[s]["net_return"] for s in ids])
        draws = gain[np.random.default_rng(1).integers(0, gain.size, (10000, gain.size))].mean(axis=1)
        report[name] = {"seasons": ids, "rule_mean": float(np.mean([base[s]["net_return"] for s in ids])),
                        "early_gain_mean": float(gain.mean()), "early_gain_ci95": [float(x) for x in np.percentile(draws, (2.5, 97.5))],
                        "share_seasons_early_pays": float(np.mean(gain > 0))}
        print(name, {k: v for k, v in report[name].items() if k != "seasons"}, flush=True)
    write_json(out / "verification.json", {"passed": True, "split": "train", "per_window": PER_WINDOW, "windows": report,
                                           "rows": rows, "final_test_split_used": False, "research_ready": False})


if __name__ == "__main__":
    main()
