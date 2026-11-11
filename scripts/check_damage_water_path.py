"""Does early pest defoliation save water, and does that pay under a water reduction? (validation only)

Variants share each season's weather, survey noise and budget. The rule policy irrigates and fertilises.
- pest_free: arrival tape set to zero.
- early_only: arrivals only before day 30 after planting and one spray forced on the first day with
  vstage >= 7, so leaf loss happens almost only before V7 (Blanco et al. 2022/2023 tolerance window).
- no_spray: full arrival tape and no spraying.
Literature direction for comparison: Oveysi et al. 2010 reported an early (V8) defoliation yield loss of
19.2 % when fully irrigated and 14.8 % under water deficit.
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
from mars_env.exogenous import evaluation_conditions, generate_season
from mars_env.pests import pest_settings
from mars_env.policies import RulePolicy
from mars_env.process_backend import LegacyProcessBackend
from mars_env.resources import ResourceRules

CONFIG = yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8"))
PARAMETERS, NOISE = pest_settings(CONFIG)
VARIANTS = ("pest_free", "early_only", "no_spray")
CONDITIONS = ("none", "early_40", "early_60")
LAST_ARRIVAL_DAY = 30


def episode(job):
    season_id, condition, variant = job
    rules, price = ResourceRules.from_config(CONFIG), CONFIG["economics"]["grain_usd_kg"]
    rule = RulePolicy.from_config(CONFIG)
    season = generate_season(CONFIG, split="validation", season_id=season_id).with_condition(
        beta=1.0, shock=evaluation_conditions(CONFIG)[condition])
    arrivals = np.array(season.pest_arrivals)
    if variant == "pest_free":
        arrivals[:] = 0
    elif variant == "early_only":
        arrivals[LAST_ARRIVAL_DAY:] = 0
    season = replace(season, pest_arrivals=arrivals)
    env = ExperimentalPestEnv(season=season, parameters=PARAMETERS, noise_std=NOISE, rules=rules, grain_price=price,
                              backend_factory=partial(LegacyProcessBackend, mode="experimental_pest", season=season,
                                                      parameters=PARAMETERS, noise_std=NOISE))
    transpiration = evaporation = early_loss = late_loss = 0.0
    forced = False
    try:
        observation, _ = env.reset()
        while True:
            state = env.state
            mask = env.action_masks()
            action = rule.action(observation, mask.copy(), rules)
            action[2] = 0
            if variant == "early_only" and not forced and float(state["vstage"]) >= 7 and mask[16]:
                action[2], forced = 1, True
            transpiration += float(state["ep"])
            evaporation += float(state.get("es", 0.0))
            vstage = float(state["vstage"])
            observation, _, terminated, truncated, info = env.step(action)
            diagnostic = env.state.get("mars_pest_diagnostic")
            if diagnostic:
                if vstage < 7:
                    early_loss += float(diagnostic["applied_fraction"])
                else:
                    late_loss += float(diagnostic["applied_fraction"])
            assert not truncated
            if terminated:
                result = info["episode_result"]
                break
    finally:
        env.close()
    return {"season_id": season_id, "condition": condition, "variant": variant, "forced_spray": forced,
            "transpiration_mm": transpiration, "soil_evaporation_mm": evaporation,
            "leaf_loss_before_v7": early_loss, "leaf_loss_after_v7": late_loss, **result}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seasons", type=int, default=40)
    parser.add_argument("--first-season", type=int, default=1200)
    args = parser.parse_args()
    run = new_run(ROOT, "damage_water_path")
    os.environ["MARS_RUN_DIR"] = str(run)
    print("RUN_DIR=" + str(run), flush=True)
    seasons = range(args.first_season, args.first_season + args.seasons)
    jobs = [(s, c, v) for s in seasons for c in CONDITIONS for v in VARIANTS]
    with ProcessPoolExecutor(max_workers=4, mp_context=get_context("fork")) as pool:
        rows = list(pool.map(episode, jobs, chunksize=3))
    write_json(run / "seasons.json", rows)
    key = {(r["season_id"], r["condition"], r["variant"]): r for r in rows}
    summary = {}
    for condition in CONDITIONS:
        summary[condition] = {}
        for variant in VARIANTS:
            items = [r for r in rows if r["condition"] == condition and r["variant"] == variant]
            summary[condition][variant] = {name: float(np.mean([r[name] for r in items])) for name in
                                           ("water_mm", "transpiration_mm", "soil_evaporation_mm", "harvested_grain_kg_ha",
                                            "net_return", "leaf_loss_before_v7", "leaf_loss_after_v7", "sprays")}
        for variant in ("early_only", "no_spray"):
            loss = [1 - key[s, condition, variant]["harvested_grain_kg_ha"] / key[s, condition, "pest_free"]["harvested_grain_kg_ha"]
                    for s in seasons]
            saved = [key[s, condition, "pest_free"]["water_mm"] - key[s, condition, variant]["water_mm"] for s in seasons]
            gain = [key[s, condition, variant]["net_return"] - key[s, condition, "pest_free"]["net_return"] for s in seasons]
            summary[condition][f"{variant}_vs_pest_free"] = {
                "yield_loss_mean": float(np.mean(loss)), "water_saved_mm_mean": float(np.mean(saved)),
                "net_difference_mean": float(np.mean(gain)), "share_net_higher_than_pest_free": float(np.mean(np.array(gain) > 0))}
    write_json(run / "verification.json", {"passed": True, "split": "validation", "summary": summary,
                                           "literature_direction": "Oveysi 2010: early defoliation yield loss 19.2% full irrigation, 14.8% deficit",
                                           "final_test_split_used": False, "research_ready": False})
    for condition, value in summary.items():
        print(condition, flush=True)
        for name, item in value.items():
            print("  ", name, {k: round(v, 3) for k, v in item.items()}, flush=True)


if __name__ == "__main__":
    main()
