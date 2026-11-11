"""Compare the terminal bridge to unmodified upstream on real DSSAT seasons."""
import json
from pathlib import Path
import sys

import gym
import numpy as np

sys.path.insert(0, "/workspace/src")
from mars_env.dssat_backend import DssatBackend


def normal(value):
    if isinstance(value, dict):
        return {k: normal(v) for k, v in value.items()}
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def action(state, managed):
    dap = state["dap"]
    return ((10 if dap in (10, 20, 30) else 0),
            ({40: 27, 45: 35, 80: 54}.get(dap, 0))) if managed else (0, 0)


def reference(seed, managed):
    env = gym.make("gym_dssat_pdi:GymDssatPdi-v0", mode="all", seed=seed, random_weather=True)
    trace = []
    try:
        obs = env.reset(seed=seed)
        for _ in range(400):
            trace.append(normal(obs))
            water, nitrogen = action(obs, managed)
            obs, _, done, _ = env.step({"amir": water, "anfer": nitrogen})
            if done:
                return trace
        raise RuntimeError("Reference season did not end")
    finally:
        env.close()


def main():
    reports = []
    backend = DssatBackend()
    try:
        for seed, managed in ((123456, False), (123456, True), (234567, False)):
            original = reference(seed, managed)
            state = backend.reset(seed)
            trace, outcome = [], None
            for _ in range(400):
                trace.append({k: normal(state[k]) for k in original[0]})
                water, nitrogen = action(state, managed)
                state, done, outcome = backend.step(water, nitrogen)
                if done:
                    break
            assert done and outcome is not None
            assert trace == original, "Nonterminal crop trajectory changed"
            # Default UFGA8201 harvest fraction is 1: end-of-season SDWT must
            # agree with rounded actual harvested dry grain in Summary.OUT.
            assert abs(state["grnwt"] - outcome.harvested_grain_kg_ha) <= 0.51
            reports.append({"seed": seed, "managed": managed, "steps": len(trace),
                            "upstream_trajectory_unchanged": True,
                            "terminal_state": normal(state),
                            "reason": outcome.reason,
                            "harvested_grain_kg_ha": outcome.harvested_grain_kg_ha,
                            "summary": outcome.summary})
        result = {"passed": True, "cases": reports,
                  "terminal_source": "current PDI callbacks after SEASEND plus Summary.OUT HWAH",
                  "actual_crop_failure_scenario_validated": False,
                  "agronomic_validation": False}
        Path("/workspace/outputs/dssat_backend_verification.json").write_text(json.dumps(result, indent=2))
        print(json.dumps({"passed": True, "cases": [{k: r[k] for k in (
            "seed", "managed", "steps", "reason", "harvested_grain_kg_ha")} for r in reports]}, indent=2))
    finally:
        backend.close()


if __name__ == "__main__":
    main()
