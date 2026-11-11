"""Real DSSAT reward telescoping on harvest, crop failure, and truncation."""
import json
import math
from pathlib import Path
import sys

import numpy as np
import yaml

sys.path.insert(0, "/workspace/src")
from mars_env.dssat_backend import DssatBackend
from mars_env.environment import CropManagementEnv
from mars_env.rewards import PotentialRewardWrapper
from verify_crop_failure import deep_planting


def run(eta, *, failure=False, max_days=240, shaped=True):
    factory = (lambda **kwargs: DssatBackend(filex_transform=deep_planting, **kwargs)) if failure else DssatBackend
    base = CropManagementEnv(pest_enabled=False, backend_factory=factory, max_days=max_days)
    env = PotentialRewardWrapper(base, eta_by_stage=eta) if shaped else base
    trace, total, raw_total = [], 0.0, 0.0
    try:
        obs, _ = env.reset(seed=123456)
        for day in range(240):
            trace.append(obs.tolist())
            obs, reward, terminated, truncated, info = env.step([1, 1, 0] if day == 0 else [0, 0, 0])
            total += reward
            raw_total += info["raw_reward"]
            if terminated or truncated:
                if shaped:
                    audit = info["reward_audit"]
                    assert math.isclose(audit["raw_return"], raw_total, abs_tol=1e-6)
                    assert abs(audit["telescoping_residual"]) < 1e-6
                    assert math.isclose(total * 1000, raw_total + audit["final_potential"] - audit["initial_potential"], abs_tol=1e-6)
                    assert (audit["final_potential"] == 0) if terminated else (audit["final_potential"] > 0)
                if terminated:
                    assert math.isclose(raw_total, info["episode_result"]["net_return"], abs_tol=1e-6)
                else:
                    assert "episode_result" not in info and info["revenue"] == 0
                return {"shaped": shaped, "failure_diagnostic": failure, "max_days": max_days,
                        "steps": day + 1, "terminated": terminated, "truncated": truncated,
                        "raw_return": raw_total, "returned_reward_sum": total,
                        "episode_result": info.get("episode_result"), "reward_audit": info.get("reward_audit")}, trace
        raise RuntimeError("Reward verification did not end")
    finally:
        env.close()


def main():
    config = yaml.safe_load(Path("/workspace/configs/proposal_v2.yaml").read_text())
    eta = config["reward_shaping"]["eta_by_stage"]
    harvest, shaped_trace = run(eta)
    raw, raw_trace = run(eta, shaped=False)
    assert shaped_trace == raw_trace and harvest["episode_result"] == raw["episode_result"]
    failure, _ = run(eta, failure=True)
    assert failure["episode_result"]["reason"] == "crop_failure" and failure["raw_return"] < 0
    truncation, _ = run(eta, max_days=20)
    result = {"passed": True, "real_dssat": True, "crop_trajectory_unchanged": True,
              "cases": [harvest, raw, failure, truncation], "gamma": 1.0, "scale": 1000.0,
              "eta_implementation_assumption": config["reward_shaping"]["eta_by_stage"]}
    Path("/workspace/outputs/real_reward_verification.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
