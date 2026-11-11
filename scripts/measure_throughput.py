"""Training throughput of one comparison fit for several parallel environment counts.

For each setting: build the vectorised environments, run one warm-up rollout, then time --steps of
PPO learning. --local-logs points the DSSAT worker logs at a container-local folder instead of the
bind-mounted project folder, to test whether log writing limits throughput.
"""
import argparse
from functools import partial
import os
from pathlib import Path
import sys
import tempfile
import time

import torch
import yaml
from stable_baselines3.common.vec_env import SubprocVecEnv

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
from mars_env.artifacts import new_run, write_json
from mars_env.comparison import training_plan
from mars_env.training_env import ChannelCycler
from pilot_learning_curve import make_model


def measure(config, fit, n_envs, steps, local_logs, run):
    log_dir = Path(tempfile.mkdtemp(prefix="mars_logs_")) if local_logs else run / f"logs_{n_envs}"
    log_dir.mkdir(parents=True, exist_ok=True)
    os.environ["MARS_RUN_DIR"] = str(log_dir)
    env = SubprocVecEnv([partial(ChannelCycler, config, learn=fit.learn, rank=rank, n_envs=n_envs,
                                 reduction_probability=fit.reduction_probability) for rank in range(n_envs)],
                        start_method="spawn")
    try:
        model = make_model(config, env, fit, config["training"]["gae_lambda"])
        rollout = config["training"]["n_steps"] * n_envs
        model.learn(rollout, reset_num_timesteps=False)
        start = time.perf_counter()
        model.learn(steps, reset_num_timesteps=False)
        seconds = time.perf_counter() - start
    finally:
        env.close()
        os.environ["MARS_RUN_DIR"] = str(run)
    return {"n_envs": n_envs, "local_logs": local_logs, "steps": steps, "seconds": seconds,
            "steps_per_second": steps / seconds}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fit", default="b1_s0")
    parser.add_argument("--n-envs", type=int, nargs="+", default=[4, 8, 12])
    parser.add_argument("--steps", type=int, default=12288)
    args = parser.parse_args()
    config = yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8"))
    fit = {f.label: f for f in training_plan(config, steps=args.steps, seeds=[int(args.fit.split("_s")[1])])}[args.fit]
    run = new_run(ROOT, "throughput")
    os.environ["MARS_RUN_DIR"] = str(run)
    print("RUN_DIR=" + str(run), flush=True)
    torch.set_num_threads(1)
    results = []
    for local_logs in (False, True):
        for n_envs in args.n_envs:
            if args.steps % (config["training"]["n_steps"] * n_envs):
                raise ValueError(f"steps must be a multiple of the rollout for {n_envs} environments")
            results.append(measure(config, fit, n_envs, args.steps, local_logs, run))
            print(results[-1], flush=True)
            write_json(run / "verification.json", {"passed": True, "fit": args.fit, "results": results,
                                                   "cpu_count": os.cpu_count(), "research_ready": False})


if __name__ == "__main__":
    main()
