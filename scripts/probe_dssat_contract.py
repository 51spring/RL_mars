"""Read-only diagnostics against the real upstream DSSAT/PDI container.

Captures raw received states without substituting the previous day's grain yield.
This is a backend contract probe, not the research Gymnasium adapter.
"""
import copy
import json
import math
from pathlib import Path

import gym
import numpy as np


def normalize(value):
    if isinstance(value, dict):
        return {key: normalize(v) for key, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [normalize(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def run_season(pulse_mm):
    env = gym.make("gym_dssat_pdi:GymDssatPdi-v0", mode="all", cultivar="maize",
                   seed=123456, random_weather=True)
    backend = env.unwrapped
    original = backend._get_state
    received = []

    def capture():
        result = original()
        received.append(normalize(copy.deepcopy(result)))
        return result

    backend._get_state = capture
    trace, pulse = [], None
    try:
        obs = env.reset(seed=123456)
        done = False
        for day in range(400):
            trace.append(normalize(copy.deepcopy(obs)))
            apply_pulse = pulse is None and obs["dap"] >= 1
            action = {"amir": pulse_mm if apply_pulse else 0, "anfer": 0}
            before = float(obs["totir"])
            obs, reward, done, info = env.step(action)
            if apply_pulse:
                assert obs is not None, "Pulse unexpectedly coincided with season termination"
                pulse = {"input_amir": pulse_mm, "totir_before": before,
                         "totir_after": float(obs["totir"]),
                         "increment": float(obs["totir"]) - before}
            if done:
                break
        assert done, "Season did not terminate within 400 steps"
        raw_obs, raw_state, _, raw_context = received[-1]
        report = {
            "steps": day + 1, "pulse": pulse,
            "initial_observation_keys": sorted(trace[0]),
            "raw_state_keys": sorted(received[0][1] or {}),
            "terminal_raw_state": raw_state,
            "terminal_raw_observation": raw_obs,
            "terminal_raw_context": raw_context,
            "public_terminal_observation": obs,
            "public_terminal_reward": reward,
        }
        return trace, report
    finally:
        env.close()


def main():
    baseline, baseline_report = run_season(0)
    repeated, _ = run_season(0)
    pulse_trace, pulse_report = run_season(10)
    deterministic = baseline == repeated
    mm_passed = math.isclose(pulse_report["pulse"]["increment"], 10, rel_tol=0, abs_tol=1e-4)
    report = {
        "seed": 123456, "scenario": "UFGA8201", "mode": "all", "random_weather": True,
        "same_seed_replay_passed": deterministic,
        "irrigation_10mm_passed": mm_passed,
        "baseline": baseline_report, "pulse_10mm": pulse_report,
        "agronomic_validation_passed": False,
        "no_pest_wrapper_regression_passed": False,
        "note": "Only unmodified upstream startup, seeded replay, action units and raw message diagnostics.",
    }
    target = Path("/workspace/outputs/dssat_contract_probe.json")
    target.write_text(json.dumps(report, indent=2, allow_nan=False))
    print(json.dumps(report, indent=2, allow_nan=False))
    assert deterministic, "Same-seed baseline replay differed"
    assert mm_passed, "10mm action did not increase cumulative irrigation by 10mm"


if __name__ == "__main__":
    main()
