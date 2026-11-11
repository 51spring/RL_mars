"""Short real-DSSAT CPU PPO integration check; not research training/performance."""
import argparse
from functools import partial
import importlib.metadata as metadata
import json
import math
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
import torch
import yaml
from sb3_contrib import MaskablePPO
from sb3_contrib.common.maskable.callbacks import MaskableEvalCallback
from stable_baselines3.common.callbacks import BaseCallback, CallbackList
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import SubprocVecEnv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from mars_env.training_env import SeasonCycler


def create_env(config, rank, n_envs, mode):
    return Monitor(SeasonCycler(config, rank=rank, n_envs=n_envs, mode=mode, shaping=True))


class CompletedRawAudit(BaseCallback):
    def __init__(self):
        super().__init__()
        self.completed = []

    def _on_step(self):
        for info in self.locals["infos"]:
            if "episode_result" in info:
                result, audit = info["episode_result"], info["reward_audit"]
                assert audit["complete_episode"]
                assert math.isclose(audit["raw_return"], result["net_return"], abs_tol=1e-5)
                assert abs(audit["telescoping_residual"]) < 1e-5
                self.completed.append({"result": result, "reward_audit": audit})
        return True


class TimedRawEvaluation(MaskableEvalCallback):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.evaluation_seconds = 0.0

    def _on_step(self):
        scheduled = self.eval_freq > 0 and self.n_calls % self.eval_freq == 0
        start = time.perf_counter()
        result = super()._on_step()
        if scheduled:
            self.evaluation_seconds += time.perf_counter() - start
        return result

    def _on_training_end(self):
        # Rollout-end evaluation precedes that rollout's optimizer update.
        # Evaluate once after the final PPO update on a rewound validation set.
        self.eval_env.env_method("restart_sequence")
        frequency = self.eval_freq
        self.eval_freq = 1
        try:
            self._on_step()
        finally:
            self.eval_freq = frequency


def manual_raw_eval(model, env):
    results = []
    for episode in range(2):
        obs, info = env.reset(seed=123 if episode == 0 else None)
        total = 0
        for _ in range(240):
            action, _ = model.predict(obs, deterministic=True,
                action_masks=env.get_wrapper_attr("action_masks")())
            obs, reward, terminated, truncated, info = env.step(action)
            total += reward
            assert math.isclose(reward, info["raw_reward"], abs_tol=1e-10)
            if terminated or truncated:
                assert terminated and not truncated
                assert math.isclose(total, info["episode_result"]["net_return"], abs_tol=1e-6)
                results.append(info["episode_result"])
                break
        else:
            raise RuntimeError("Raw evaluation did not terminate")
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("no_pest", "experimental_pest"), default="no_pest")
    parser.add_argument("--steps", type=int, default=1024)
    args = parser.parse_args()
    if args.steps < 512 or args.steps % 256:
        parser.error("diagnostic steps must be a multiple of 256, at least 512")
    config = yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text())
    cfg = config["training"]
    assert cfg["gamma"] == config["reward_shaping"]["gamma"] == 1
    torch.set_num_threads(1)
    output = ROOT / "outputs" / f"real_ppo_{args.mode}_cpu"
    output.mkdir(parents=True, exist_ok=True)
    train = SubprocVecEnv([partial(create_env, config, rank, 4, args.mode) for rank in range(4)], start_method="spawn")
    evaluation = Monitor(SeasonCycler(config, rank=0, n_envs=1, split="validation", mode=args.mode, shaping=False))
    try:
        raw_audit = CompletedRawAudit()
        evaluation_callback = TimedRawEvaluation(evaluation, n_eval_episodes=2, deterministic=True,
            eval_freq=0, best_model_save_path=str(output / "best"),
            log_path=str(output / "eval"), verbose=0)
        model = MaskablePPO("MlpPolicy", train, device="cpu", seed=42,
            gamma=cfg["gamma"], gae_lambda=cfg["gae_lambda"], n_steps=64, batch_size=64, n_epochs=2,
            policy_kwargs={"net_arch": {"pi": cfg["policy_layers"], "vf": cfg["value_layers"]}},
            tensorboard_log=str(output / "tensorboard"), verbose=0)
        with torch.no_grad():
            offset = 0
            masses = cfg["sparse_nonzero_mass"]
            for count, mass in zip((6, 9, 2), (masses["irrigation"], masses["nitrogen"], masses["spray"])):
                model.policy.action_net.weight[offset:offset + count].zero_()
                probs = torch.tensor([1 - mass] + [mass / (count - 1)] * (count - 1))
                model.policy.action_net.bias[offset:offset + count].copy_(probs.log())
                offset += count
        start = time.perf_counter()
        model.learn(args.steps, callback=CallbackList([raw_audit, evaluation_callback]))
        elapsed = time.perf_counter() - start
        assert raw_audit.completed and model._n_updates > 0
        assert all(torch.isfinite(p).all() for p in model.policy.parameters())
        model.save(output / "model")
        loaded = MaskablePPO.load(output / "model", device="cpu")
        raw_evaluation = manual_raw_eval(loaded, evaluation)
        mean_raw = float(np.mean([r["net_return"] for r in raw_evaluation]))
        assert math.isclose(mean_raw, evaluation_callback.last_mean_reward, abs_tol=1e-5)
        training_seconds = max(1e-9, elapsed - evaluation_callback.evaluation_seconds)
        report = {"passed": True, "real_dssat": True, "diagnostic_only": True, "mode": args.mode,
            "device": "cpu", "n_envs": 4, "timesteps": model.num_timesteps, "ppo_updates": model._n_updates,
            "elapsed_learning_seconds_including_callback": elapsed,
            "raw_evaluation_callback_seconds": evaluation_callback.evaluation_seconds,
            "learning_seconds_excluding_callback": training_seconds,
            "preliminary_steps_per_second": model.num_timesteps / training_seconds,
            "timing_note": "Short CPU integration run includes rollout and PPO updates; not 100k-200k benchmark or GPU comparison.",
            "completed_train_episodes": len(raw_audit.completed), "training_episodes": raw_audit.completed,
            "raw_validation_results": raw_evaluation, "raw_validation_mean": mean_raw,
            "masked_raw_eval_callback_mean": evaluation_callback.last_mean_reward,
            "evaluation_uses_final_updated_policy": True,
            "evaluation_split": "validation", "final_test_split_used": False,
            "shaping": config["reward_shaping"], "model_reload_passed": True,
            "legacy_python": "/opt/gym_dssat_pdi/bin/python", "learner_python": sys.executable,
            "packages": {name: metadata.version(name) for name in ("torch", "numpy", "gymnasium", "stable-baselines3", "sb3-contrib")},
            "agronomic_validation": False, "research_ready": False}
        (output / "verification.json").write_text(json.dumps(report, indent=2))
        freeze = subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True)
        (ROOT / "outputs/requirements-lock-linux-ppo.txt").write_text(freeze)
        print(json.dumps({k: report[k] for k in ("passed", "mode", "timesteps", "ppo_updates", "completed_train_episodes", "preliminary_steps_per_second", "raw_validation_mean")}, indent=2))
    finally:
        train.close()
        evaluation.close()


if __name__ == "__main__":
    main()
