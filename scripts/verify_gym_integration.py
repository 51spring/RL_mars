"""Real DSSAT no-pest Gymnasium accounting and trajectory regression."""
import json
from pathlib import Path
import sys

import gym
import numpy as np

sys.path.insert(0, "/workspace/src")
from mars_env.environment import CropManagementEnv
from mars_env.resources import WaterShock


def normal(value):
    return value.tolist() if hasattr(value, "tolist") else value


def reference_replay(seed, preplant_days, actions, snapshots):
    env = gym.make("gym_dssat_pdi:GymDssatPdi-v0", mode="all", seed=seed, random_weather=True)
    try:
        obs = env.reset(seed=seed)
        for _ in range(preplant_days):
            obs, _, done, _ = env.step({"amir": 0, "anfer": 0})
            assert not done
        for applied, snapshot in zip(actions, snapshots):
            assert all(normal(obs[k]) == normal(snapshot[k]) for k in obs), "Wrapper changed crop observations"
            obs, _, done, _ = env.step({"amir": applied.water_mm, "anfer": applied.nitrogen_kg_ha})
        assert done, "Replayed original season did not end"
    finally:
        env.close()


def main():
    results = []
    for managed in (False, True):
        env = CropManagementEnv(pest_enabled=False, beta=0.6 if managed else 1,
                                shock=WaterShock(1, 2, 0.4) if managed else None)
        rng = np.random.default_rng(42)
        try:
            obs, reset_info = env.reset(seed=123456)
            assert reset_info["preplant_days"] == 27
            assert obs.shape == env.observation_space.shape and env.observation_space.contains(obs)
            total_reward, actions, snapshots = 0, [], []
            for _ in range(240):
                mask = env.action_masks()
                ids = [int(rng.choice(np.flatnonzero(m))) for m in np.split(mask, (6, 15))] if managed else [0, 0, 0]
                actions.append(env.rules.decode(ids))
                snapshots.append(dict(env.state))
                obs, reward, terminated, truncated, info = env.step(ids)
                assert env.observation_space.contains(obs)
                total_reward += reward
                if terminated or truncated:
                    break
            assert terminated and not truncated
            result = info["episode_result"]
            assert abs(total_reward - result["net_return"]) < 1e-6
            assert abs(env.state["totir"] - env.ledger.water_used) < 1e-4
            assert abs(env.state["cumsumfert"] - env.ledger.nitrogen_used) < 1e-4
            assert env.ledger.water_left >= 0 and env.ledger.nitrogen_budget_left >= 0
            reference_replay(123456, reset_info["preplant_days"], actions, snapshots)
            results.append({"managed": managed, "preplant_days": reset_info["preplant_days"],
                            "policy_steps": len(actions), "original_trajectory_unchanged": True,
                            "observation_shape": list(obs.shape), "mask_shape": [17],
                            "accounting_passed": True, "episode_result": result,
                            "announcement": env.ledger.announcement()})
        finally:
            env.close()
    env = CropManagementEnv(pest_enabled=False, max_days=3)
    try:
        env.reset(seed=123456)
        for _ in range(3):
            _, _, terminated, truncated, info = env.step([0, 0, 0])
        assert truncated and not terminated and "episode_result" not in info and info["revenue"] == 0
    finally:
        env.close()
    report = {"passed": True, "pest_enabled": False, "cases": results,
              "truncation_without_harvest_passed": True, "agronomic_validation": False}
    Path("/workspace/outputs/gym_integration_verification.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
