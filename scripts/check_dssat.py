"""Run inside the upstream Linux container; verifies startup and one season only."""
import json
from pathlib import Path

import gym


def main():
    env = gym.make(
        "gym_dssat_pdi:GymDssatPdi-v0", mode="all", cultivar="maize",
        seed=123456, random_weather=True,
    )
    try:
        obs = env.reset(seed=123456)
        assert isinstance(obs, dict) and "dap" in obs
        initial_keys = sorted(obs)
        steps = 0
        done = False
        while not done and steps < 400:
            transition = env.step({"amir": 0, "anfer": 0})
            assert transition is not None and len(transition) == 4
            obs, _, done, _ = transition
            steps += 1
        assert done, "No end-of-season signal within 400 steps"
        report = {
            "startup_and_season_passed": True,
            "mode": "all", "cultivar": "maize", "scenario": "UFGA8201",
            "random_weather": True, "steps": steps,
            "observation_keys": initial_keys,
            "terminal_observation_available": obs is not None,
            "live_damage_writer_validated": False,
            "terminal_harvest_or_failure_classification_validated": False,
            "note": "Unmodified upstream smoke only; no crop-response or research-wrapper validation.",
        }
        print(json.dumps(report, indent=2))
        Path("/workspace/outputs/dssat_check.json").write_text(json.dumps(report, indent=2))
    finally:
        env.close()


if __name__ == "__main__":
    main()
