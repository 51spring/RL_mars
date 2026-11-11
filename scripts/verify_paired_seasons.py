"""Real DSSAT weather pairing across conditions/policies; no pest crop writing."""
import json
from pathlib import Path
import sys

import numpy as np
import yaml

sys.path.insert(0, "/workspace/src")
from mars_env.environment import CropManagementEnv
from mars_env.exogenous import generate_season
from mars_env.resources import WaterShock


def main():
    config = yaml.safe_load(Path("/workspace/configs/proposal_v2.yaml").read_text())
    season = generate_season(config, split="validation", season_id=0)
    tapes, results = [], []
    for managed in (False, True):
        condition = season.with_condition(beta=0.6 if managed else 1,
                                         shock=WaterShock(1, 0, 0.6) if managed else None)
        env = CropManagementEnv(pest_enabled=False)
        weather, total = {}, 0
        rng = np.random.default_rng(42)
        try:
            env.reset(options={"season": condition})
            for day in range(240):
                state = env.state
                weather[int(state["yrdoy"])] = [float(state[k]) for k in ("rain", "tmax", "srad")]
                masks = env.action_masks()
                action = [int(rng.choice(np.flatnonzero(group))) for group in np.split(masks, (6, 15))] if managed else [0, 0, 0]
                _, reward, terminated, truncated, info = env.step(action)
                total += reward
                if terminated or truncated:
                    break
            assert terminated and not truncated
            assert abs(total - info["episode_result"]["net_return"]) < 1e-6
            assert condition.paired_digest() == season.paired_digest()
            tapes.append(weather)
            results.append({"managed": managed, "backend_seed": condition.backend_seed, "beta": condition.beta,
                            "shock": condition.manifest()["shock"], "steps": day + 1,
                            "episode_result": info["episode_result"], "paired_digest": condition.paired_digest()})
        finally:
            env.close()
    common = sorted(set(tapes[0]) & set(tapes[1]))
    assert len(common) > 0 and all(tapes[0][date] == tapes[1][date] for date in common)
    host = json.loads(Path("/workspace/outputs/exogenous_manifest.json").read_text())
    host_case = next(x for x in host["seasons"] if x["split"] == "validation" and x["season_id"] == 0)
    assert host_case["paired_digest"] == season.paired_digest(), "Windows/Linux external stream mismatch"
    report = {"passed": True, "common_dates_weather_equal": len(common),
              "windows_linux_tapes_equal": True, "cases": results,
              "note": "Pairing uses common planting-relative external inputs; no policy seed in season generation."}
    Path("/workspace/outputs/paired_seasons_verification.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
