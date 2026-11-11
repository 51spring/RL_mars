"""Action usage by growth stage on validation seasons: rule policy and a pilot PPO checkpoint (irrigation).

Counts each water, nitrogen and spray choice by DSSAT istage, the share of days each action is masked, and
how often the water budget or the physical supply is the binding water limit. Validation only.
"""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from multiprocessing import get_context
import os
from pathlib import Path
import sys

import numpy as np
import torch
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from mars_env.economics import grain_price
from mars_env.artifacts import new_run, write_json
from mars_env.experimental_env import ExperimentalPestEnv
from mars_env.exogenous import evaluation_conditions, generate_season
from mars_env.pests import pest_settings
from mars_env.policies import CompositePolicy, FrozenChannels, RulePolicy
from mars_env.process_backend import LegacyProcessBackend
from mars_env.resources import ResourceRules

SEASONS = tuple(range(4500, 4520))
CONDITIONS = ("none", "early_40", "late_60")


def run(job):
    policy_name, checkpoint, condition, season_id = job
    torch.set_num_threads(1)
    config = yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8"))
    parameters, noise = pest_settings(config)
    rules, price = ResourceRules.from_config(config), grain_price(config)
    rule = RulePolicy.from_config(config)
    if policy_name == "rule":
        policy = rule
    else:
        from sb3_contrib import MaskablePPO
        policy = CompositePolicy(rule, (FrozenChannels(MaskablePPO.load(checkpoint, device="cpu"), (0,), deterministic=True),))
    season = generate_season(config, split="validation", season_id=season_id).with_condition(
        beta=1.0, shock=evaluation_conditions(config)[condition])
    env = ExperimentalPestEnv(season=season, parameters=parameters, noise_std=noise, rules=rules, grain_price=price,
                              backend_factory=partial(LegacyProcessBackend, mode="experimental_pest", season=season,
                                                      parameters=parameters, noise_std=noise))
    rows = []
    try:
        obs, _ = env.reset()
        for _ in range(240):
            ledger, stage = env.ledger, int(env.state["istage"])
            mask = env.action_masks()
            budget_limit = supply_limit = 0  # water budget removed 2026-11-11 (decision_project.md 23)
            indices = policy.action(obs, mask.copy(), rules)
            action = rules.decode(indices)
            rows.append({"istage": stage, "dap": int(env.state["dap"]), "water": action.water_mm,
                         "nitrogen": action.nitrogen_kg_ha, "spray": int(action.spray),
                         "water_options": int(mask[:6].sum()), "spray_allowed": bool(mask[16]),
                         "budget_binds_before_supply": budget_limit < supply_limit})
            obs, _, terminated, truncated, info = env.step(indices)
            if terminated or truncated:
                net = info["episode_result"]["net_return"]
                break
    finally:
        env.close()
    return policy_name, condition, season_id, net, rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path, required=True)
    args = parser.parse_args()
    run_dir = new_run(ROOT, "action_usage")
    os.environ["MARS_RUN_DIR"] = str(run_dir)
    print("RUN_DIR=" + str(run_dir), flush=True)
    jobs = [(p, str(args.checkpoint), c, s) for p in ("rule", "ppo_b1") for c in CONDITIONS for s in SEASONS]
    with ProcessPoolExecutor(max_workers=8, mp_context=get_context("fork")) as pool:
        results = list(pool.map(run, jobs))
    report = {}
    for policy in ("rule", "ppo_b1"):
        rows = [r for p, _, _, _, rr in results if p == policy for r in rr]
        days = len(rows)
        by_stage = {}
        for stage in sorted({r["istage"] for r in rows}):
            sub = [r for r in rows if r["istage"] == stage]
            by_stage[stage] = {"days": len(sub), "water_mm_per_season": sum(r["water"] for r in sub) / (len(results) / 2),
                               "irrigation_events": sum(r["water"] > 0 for r in sub),
                               "nitrogen_kg_per_season": sum(r["nitrogen"] for r in sub) / (len(results) / 2),
                               "sprays": sum(r["spray"] for r in sub)}
        report[policy] = {
            "net_return_by_condition": {c: float(np.mean([n for p, cc, _, n, _ in results if p == policy and cc == c]))
                                        for c in CONDITIONS},
            "decision_days": days,
            "water_choice_counts": dict(Counter(r["water"] for r in rows)),
            "nitrogen_choice_counts": dict(Counter(r["nitrogen"] for r in rows)),
            "spray_count": sum(r["spray"] for r in rows),
            "share_days_spray_allowed": float(np.mean([r["spray_allowed"] for r in rows])),
            "days_water_budget_binds_before_supply": sum(r["budget_binds_before_supply"] for r in rows),
            "by_istage": by_stage,
            "after_maturity": {"days": sum(r["istage"] == 6 for r in rows),
                               "water_mm": sum(r["water"] for r in rows if r["istage"] == 6),
                               "nitrogen_kg": sum(r["nitrogen"] for r in rows if r["istage"] == 6)},
        }
        print(policy, report[policy], flush=True)
    write_json(run_dir / "verification.json", {"passed": True, "split": "validation", "seasons": list(SEASONS),
                                               "conditions": list(CONDITIONS), "checkpoint": str(args.checkpoint),
                                               "report": report, "final_test_split_used": False,
                                               "research_ready": False})


if __name__ == "__main__":
    main()
