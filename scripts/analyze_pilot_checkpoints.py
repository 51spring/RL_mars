"""Mechanism diagnostics for a pilot run's checkpoints (irrigation channel, policy b1).

1. Fixed probe states: observations and masks from rule-policy rollouts on validation seasons (none and
   early_40). For every checkpoint: mean entropy of the irrigation head, mean probability of each water
   amount, and KL divergence from the previous checkpoint on the same states.
2. Selected checkpoints: greedy rollouts on validation seasons, irrigation by growth stage and net return.
Validation split only. Uses the current observation code, so it only fits checkpoints trained with it.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
from functools import partial
import json
from multiprocessing import get_context
import os
from pathlib import Path
import sys

import numpy as np
import torch
import yaml
from sb3_contrib import MaskablePPO

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from mars_env.artifacts import new_run, write_json
from mars_env.economics import grain_price
from mars_env.experimental_env import ExperimentalPestEnv
from mars_env.exogenous import evaluation_conditions, generate_season
from mars_env.pests import pest_settings
from mars_env.policies import CompositePolicy, FrozenChannels, RulePolicy
from mars_env.process_backend import LegacyProcessBackend
from mars_env.resources import ResourceRules

PROBE_SEASONS = tuple(range(4500, 4508))
EVAL_SEASONS = tuple(range(4500, 4516))
CONDITIONS = ("none", "early_40")


def make_env(config, season_id, condition):
    parameters, noise = pest_settings(config)
    season = generate_season(config, split="validation", season_id=season_id).with_condition(
        beta=1.0, shock=evaluation_conditions(config)[condition])
    rules = ResourceRules.from_config(config)
    env = ExperimentalPestEnv(season=season, parameters=parameters, noise_std=noise, rules=rules,
                              grain_price=grain_price(config),
                              backend_factory=partial(LegacyProcessBackend, mode="experimental_pest", season=season,
                                                      parameters=parameters, noise_std=noise))
    return env, rules


def rollout(job):
    config, season_id, condition, checkpoint = job
    torch.set_num_threads(1)
    rule = RulePolicy.from_config(config)
    policy = rule if checkpoint is None else CompositePolicy(
        rule, (FrozenChannels(MaskablePPO.load(checkpoint, device="cpu"), (0,), deterministic=True),))
    env, rules = make_env(config, season_id, condition)
    states, stage_water, net = [], {}, None
    try:
        obs, _ = env.reset()
        for _ in range(240):
            mask = env.action_masks()
            stage = int(env.state["istage"])
            states.append((obs.copy(), mask[:6].copy(), stage))
            action = policy.action(obs, mask.copy(), rules)
            stage_water[stage] = stage_water.get(stage, 0.0) + rules.water_grid[int(action[0])]
            obs, _, terminated, truncated, info = env.step(action)
            if terminated or truncated:
                net = info["episode_result"]["net_return"]
                break
    finally:
        env.close()
    return {"season_id": season_id, "condition": condition, "checkpoint": checkpoint, "net_return": net,
            "stage_water": stage_water, "states": states if checkpoint is None else None}


def head_distribution(model, observations, masks):
    with torch.no_grad():
        obs = torch.as_tensor(observations, dtype=torch.float32)
        dist = model.policy.get_distribution(obs, action_masks=masks)
        inner = dist.distribution
        probs = inner.probs if hasattr(inner, "probs") else inner[0].probs
    return probs.numpy()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, required=True, help="pilot run directory")
    parser.add_argument("--rollout-steps", type=int, nargs="+", default=[153600, 460800, 1177600, 1433600, 2048000])
    args = parser.parse_args()
    config = yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8"))
    state = json.loads((args.run / "pilot_state.json").read_text(encoding="utf-8"))
    out = new_run(ROOT, "pilot_checkpoint_diagnostics")
    os.environ["MARS_RUN_DIR"] = str(out)
    print("RUN_DIR=" + str(out), flush=True)
    with ProcessPoolExecutor(max_workers=8, mp_context=get_context("fork")) as pool:
        probes = list(pool.map(rollout, [(config, s, c, None) for s in PROBE_SEASONS for c in CONDITIONS]))
        observations = np.stack([o for p in probes for o, _, _ in p["states"]])
        masks = np.stack([m for p in probes for _, m, _ in p["states"]])
        stages = np.array([s for p in probes for _, _, s in p["states"]])
        rows, previous = [], None
        for entry in state["checkpoints"]:
            model = MaskablePPO.load(args.run / entry["file"], device="cpu")
            probs = head_distribution(model, observations, masks)
            entropy = -(probs * np.log(np.clip(probs, 1e-12, 1))).sum(axis=1)
            row = {"steps": entry["steps"], "entropy_mean": float(entropy.mean()),
                   "near_deterministic_share": float(np.mean(probs.max(axis=1) > 0.99)),
                   "water_probabilities": [float(x) for x in probs.mean(axis=0)],
                   "expected_water_mm_by_stage": {int(s): float((probs[stages == s] @ np.array(ResourceRules.from_config(config).water_grid)).mean())
                                                  for s in sorted(set(stages)) if s in (1, 2, 3, 4, 5)}}
            if previous is not None:
                kl = (previous * (np.log(np.clip(previous, 1e-12, 1)) - np.log(np.clip(probs, 1e-12, 1)))).sum(axis=1)
                row["kl_from_previous_mean"] = float(kl.mean())
                row["greedy_action_change_share"] = float(np.mean(previous.argmax(axis=1) != probs.argmax(axis=1)))
            previous = probs
            rows.append(row)
            print("CKPT", entry["steps"], round(row["entropy_mean"], 3), round(row["near_deterministic_share"], 3),
                  round(row.get("kl_from_previous_mean", 0), 4), round(row.get("greedy_action_change_share", 0), 3),
                  {k: round(v, 1) for k, v in row["expected_water_mm_by_stage"].items()}, flush=True)
        files = {e["steps"]: str(args.run / e["file"]) for e in state["checkpoints"]}
        jobs = [(config, s, c, files[step]) for step in args.rollout_steps for s in EVAL_SEASONS for c in CONDITIONS]
        jobs += [(config, s, c, None) for s in EVAL_SEASONS for c in CONDITIONS]
        results = list(pool.map(rollout, jobs))
    timing = {}
    for step in args.rollout_steps + [None]:
        key = "rule" if step is None else str(step)
        for condition in CONDITIONS:
            items = [r for r in results if r["condition"] == condition and r["checkpoint"] == (None if step is None else files[step])]
            timing[f"{key}|{condition}"] = {
                "net_return": float(np.mean([r["net_return"] for r in items])),
                "water_mm_by_stage": {str(s): float(np.mean([r["stage_water"].get(s, 0.0) for r in items])) for s in (1, 2, 3, 4, 5)}}
            print("TIMING", key, condition, round(timing[f"{key}|{condition}"]["net_return"], 1),
                  {k: round(v, 1) for k, v in timing[f"{key}|{condition}"]["water_mm_by_stage"].items()}, flush=True)
    write_json(out / "verification.json", {"passed": True, "source_run": str(args.run), "probe_seasons": list(PROBE_SEASONS),
                                           "probe_states": int(len(observations)), "checkpoints": rows, "timing": timing,
                                           "note": "config at analysis time (new price and irrigation rule) differs from the pilot's start",
                                           "split": "validation", "final_test_split_used": False, "research_ready": False})


if __name__ == "__main__":
    main()
