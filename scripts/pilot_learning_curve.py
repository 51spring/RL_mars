"""Pilot learning curve for one comparison fit, with periodic checkpoints and resume.

Trains one fit of the comparison plan (default b1: irrigation PPO, rule nitrogen and spraying) on the
training split, saves a checkpoint every --chunk steps (model, season cursors, timing) and evaluates the
saved policy on fixed validation seasons against the rule policy. Validation only; no final test access.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
from functools import partial
import json
from multiprocessing import get_context
import os
from pathlib import Path
import sys
import time

import numpy as np
import torch
import yaml
from sb3_contrib import MaskablePPO
from stable_baselines3.common.vec_env import SubprocVecEnv

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
from mars_env.economics import grain_price
from mars_env.artifacts import new_run, sha256, write_json
from mars_env.baseline_evaluation import evaluate_episode
from mars_env.comparison import training_plan
from mars_env.experimental_env import ExperimentalPestEnv
from mars_env.exogenous import evaluation_conditions, generate_season
from mars_env.pests import pest_settings
from mars_env.policies import CompositePolicy, FrozenChannels, RulePolicy
from mars_env.process_backend import LegacyProcessBackend
from mars_env.resources import ResourceRules
from mars_env.training_env import ChannelCycler
from run_comparison import Audit, NAMES, SIZES

EVAL_SEASONS = tuple(range(4500, 4516))
EVAL_CONDITIONS = ("none", "early_40")


def make_model(config, env, fit, gae_lambda, n_steps=None, batch_size=None, n_epochs=None):
    cfg = config["training"]
    model = MaskablePPO("MlpPolicy", env, device="cpu", seed=fit.seed, gamma=cfg["gamma"], gae_lambda=gae_lambda,
                        n_steps=n_steps or cfg["n_steps"], batch_size=batch_size or cfg["batch_size"],
                        n_epochs=n_epochs or cfg["n_epochs"],
                        policy_kwargs={"net_arch": {"pi": cfg["policy_layers"], "vf": cfg["value_layers"]}})
    with torch.no_grad():
        offset = 0
        for channel in fit.learn:
            count, mass = SIZES[channel], cfg["sparse_nonzero_mass"][NAMES[channel]]
            model.policy.action_net.weight[offset:offset + count].zero_()
            model.policy.action_net.bias[offset:offset + count].copy_(
                torch.tensor([1 - mass] + [mass / (count - 1)] * (count - 1)).log())
            offset += count
    return model


def evaluate(job):
    checkpoint, learn, season_id, condition, mode = job
    torch.set_num_threads(1)
    config = yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8"))
    parameters, noise = pest_settings(config)
    rules, price = ResourceRules.from_config(config), grain_price(config)
    rule = RulePolicy.from_config(config)
    if mode == "rule":
        policy = rule
    else:
        torch.manual_seed(season_id)
        model = MaskablePPO.load(checkpoint, device="cpu")
        policy = CompositePolicy(rule, (FrozenChannels(model, learn, deterministic=mode == "greedy"),))
    season = generate_season(config, split="validation", season_id=season_id).with_condition(
        beta=1.0, shock=evaluation_conditions(config)[condition])
    env = ExperimentalPestEnv(season=season, parameters=parameters, noise_std=noise, rules=rules, grain_price=price,
                              backend_factory=partial(LegacyProcessBackend, mode="experimental_pest", season=season,
                                                      parameters=parameters, noise_std=noise))
    try:
        result = evaluate_episode(env, policy, season, rules, price, reset_options={})["episode_result"]
    finally:
        env.close()
    return {"season_id": season_id, "condition": condition, "mode": mode, "net_return": result["net_return"],
            "water_mm": result["water_mm"], "nitrogen_kg_ha": result["nitrogen_kg_ha"], "sprays": result["sprays"]}


def summarise(rows):
    out = {}
    for mode in sorted({r["mode"] for r in rows}):
        for condition in EVAL_CONDITIONS:
            items = [r for r in rows if r["mode"] == mode and r["condition"] == condition]
            out[f"{mode}|{condition}"] = {key: float(np.mean([r[key] for r in items]))
                                          for key in ("net_return", "water_mm", "nitrogen_kg_ha", "sprays")}
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fit", default="b1_s0")
    parser.add_argument("--steps", type=int, default=500_000)
    parser.add_argument("--chunk", type=int, default=50_000)
    parser.add_argument("--n-envs", type=int, default=8)
    parser.add_argument("--gae-lambda", type=float)
    parser.add_argument("--resume", type=Path)
    parser.add_argument("--n-steps", type=int, help="PPO rollout length per environment (default: config)")
    parser.add_argument("--batch-size", type=int)
    parser.add_argument("--n-epochs", type=int)
    args = parser.parse_args()
    config = yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8"))
    gae_lambda = args.gae_lambda if args.gae_lambda is not None else config["training"]["gae_lambda"]
    fit = {f.label: f for f in training_plan(config, steps=args.steps, seeds=[int(args.fit.split("_s")[1])])}[args.fit]
    if fit.frozen:
        raise ValueError("Pilot supports fits without frozen networks (policy 1 or 4)")
    rollout = (args.n_steps or config["training"]["n_steps"]) * args.n_envs
    if args.chunk % rollout:
        parser.error(f"Chunk must be a multiple of the rollout size {rollout}")
    run = args.resume or new_run(ROOT, f"pilot_{args.fit}")
    os.environ["MARS_RUN_DIR"] = str(run)
    print("RUN_DIR=" + str(run), flush=True)
    state_path = run / "pilot_state.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else {
        "fit": args.fit, "gae_lambda": gae_lambda, "n_envs": args.n_envs, "target_steps": args.steps,
        "n_steps": args.n_steps or config["training"]["n_steps"], "batch_size": args.batch_size or config["training"]["batch_size"],
        "n_epochs": args.n_epochs or config["training"]["n_epochs"],
        "config_sha256": sha256(run / "config.yaml"), "checkpoints": []}
    if args.resume:
        assert state["config_sha256"] == sha256(ROOT / "configs/proposal_v2.yaml"), "config changed since the pilot started"
        assert (state["n_envs"], state["gae_lambda"]) == (args.n_envs, gae_lambda)
    torch.set_num_threads(1)
    env = SubprocVecEnv([partial(ChannelCycler, config, learn=fit.learn, rank=rank, n_envs=args.n_envs,
                                 reduction_probability=fit.reduction_probability) for rank in range(args.n_envs)],
                        start_method="spawn")
    try:
        if state["checkpoints"]:
            last = state["checkpoints"][-1]
            model = MaskablePPO.load(run / last["file"], env=env, device="cpu")
            for rank, cursor in enumerate(last["season_cursors"]):
                env.env_method("set_season_cursor", cursor, indices=[rank])
            print("RESUMED", model.num_timesteps, flush=True)
        else:
            model = make_model(config, env, fit, gae_lambda, state["n_steps"], state["batch_size"], state["n_epochs"])
            baseline = []
            with ProcessPoolExecutor(max_workers=4, mp_context=get_context("fork")) as pool:
                baseline = list(pool.map(evaluate, [(None, fit.learn, s, c, "rule") for s in EVAL_SEASONS for c in EVAL_CONDITIONS]))
            state["rule_policy"] = summarise(baseline)
            write_json(state_path, state)
            print("RULE", state["rule_policy"], flush=True)
        while model.num_timesteps < args.steps:
            audit = Audit()
            start = time.perf_counter()
            model.learn(min(args.chunk, args.steps - model.num_timesteps), reset_num_timesteps=False, callback=audit)
            seconds = time.perf_counter() - start
            assert audit.truncations == 0 and all(torch.isfinite(p).all() for p in model.policy.parameters())
            name = f"checkpoint_{model.num_timesteps:09d}.zip"
            model.save(run / name)
            with ProcessPoolExecutor(max_workers=4, mp_context=get_context("fork")) as pool:
                rows = list(pool.map(evaluate, [(str(run / name), fit.learn, s, c, m) for s in EVAL_SEASONS
                                                for c in EVAL_CONDITIONS for m in ("greedy", "sampled")]))
            entry = {"file": name, "steps": model.num_timesteps, "chunk_seconds": seconds,
                     "steps_per_second": args.chunk / seconds, "train_seasons": len(audit.returns),
                     "train_return_mean": float(np.mean(audit.returns)) if audit.returns else None,
                     "season_cursors": env.env_method("season_cursor"), "checkpoint_sha256": sha256(run / name),
                     "validation": summarise(rows)}
            state["checkpoints"].append(entry)
            write_json(state_path, state)
            print("CHECKPOINT", model.num_timesteps, round(entry["steps_per_second"], 1),
                  {k: round(v["net_return"], 1) for k, v in entry["validation"].items()}, flush=True)
    finally:
        env.close()
    write_json(run / "verification.json", {"passed": True, **state, "split": "validation",
                                           "final_test_split_used": False, "research_ready": False})


if __name__ == "__main__":
    main()
