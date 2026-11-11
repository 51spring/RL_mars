"""Synthetic interface test, NOT a crop model or research benchmark."""
import argparse
import json
from pathlib import Path

import gymnasium as gym
import numpy as np
import torch
import yaml
from sb3_contrib import MaskablePPO
from sb3_contrib.common.maskable.evaluation import evaluate_policy
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import SubprocVecEnv

ROOT = Path(__file__).resolve().parents[1]


class InterfaceOnlyEnv(gym.Env):
    observation_space = gym.spaces.Box(0, 1, shape=(315,), dtype=np.float32)
    action_space = gym.spaces.MultiDiscrete([6, 9, 2])

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self.day = 0
        return self._obs(), {"synthetic": True}

    def _obs(self):
        return np.full(315, self.day / 32, dtype=np.float32)

    def action_masks(self):
        mask = np.ones(17, dtype=bool)
        mask[5] = False
        mask[14] = False
        mask[16] = self.day % 7 == 0
        return mask

    def step(self, action):
        assert self.action_space.contains(action)
        mask = self.action_masks()
        assert all(mask[offset + int(a)] for offset, a in zip([0, 6, 15], action))
        self.day += 1
        return self._obs(), -float(np.count_nonzero(action)), self.day == 32, False, {"synthetic": True}


def make_env():
    return Monitor(InterfaceOnlyEnv())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    args = parser.parse_args()
    torch.set_num_threads(1)
    cfg = yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8"))["training"]
    env = SubprocVecEnv([make_env for _ in range(cfg["n_envs"])], start_method="spawn")
    eval_env = make_env()
    try:
        model = MaskablePPO(
            "MlpPolicy", env, device=args.device, seed=42,
            gamma=cfg["gamma"], gae_lambda=cfg["gae_lambda"],
            n_steps=32, batch_size=64, n_epochs=2,
            policy_kwargs={"net_arch": {"pi": cfg["policy_layers"], "vf": cfg["value_layers"]}},
            verbose=0,
        )
        # Check the proposal's initial nonzero probability mass per action dimension.
        with torch.no_grad():
            offset = 0
            for count, mass in zip([6, 9, 2], [0.13, 0.03, 0.03]):
                model.policy.action_net.weight[offset:offset + count].zero_()
                probs = torch.tensor([1 - mass] + [mass / (count - 1)] * (count - 1))
                model.policy.action_net.bias[offset:offset + count].copy_(probs.log())
                offset += count
        model.learn(total_timesteps=512)
        mean, std = evaluate_policy(model, eval_env, n_eval_episodes=2)
        assert model._n_updates > 0
        model_path = ROOT / "outputs" / f"interface_smoke_{args.device}"
        model_path.parent.mkdir(exist_ok=True)
        model.save(model_path)
        loaded = MaskablePPO.load(model_path, device=args.device)
        obs, _ = eval_env.reset()
        action, _ = loaded.predict(obs, action_masks=eval_env.unwrapped.action_masks())
        eval_env.step(action)
        report = {"passed": True, "synthetic_only": True, "device": args.device,
                  "n_envs": env.num_envs, "steps": model.num_timesteps,
                  "updates": model._n_updates, "observation_size": 315, "action_nvec": [6, 9, 2],
                  "mask_size": 17, "evaluation_mean": mean, "evaluation_std": std,
                  "note": "Interface check only; no DSSAT, crop response, or agricultural performance validation."}
        (ROOT / "outputs" / f"smoke_{args.device}.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report, indent=2))
    finally:
        env.close()
        eval_env.close()


if __name__ == "__main__":
    main()
