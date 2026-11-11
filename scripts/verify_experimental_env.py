import json
from pathlib import Path
import sys

import numpy as np
import yaml

sys.path.insert(0, "/workspace/src")
from mars_env.experimental_env import ExperimentalPestEnv
from mars_env.exogenous import generate_season
from mars_env.observations import FIELDS
from mars_env.pests import PestParameters


def main():
    config = yaml.safe_load(Path("/workspace/configs/proposal_v2.yaml").read_text())
    season = generate_season(config, split="validation", season_id=0).with_condition(beta=1, shock=None)
    indices = {name: i for i, (name, _) in enumerate(FIELDS)}
    cases = []
    for allow_spray in (False, True):
        env = ExperimentalPestEnv(season=season, parameters=PestParameters(10, 30), noise_std=0.01)
        try:
            obs, info = env.reset(seed=99)
            assert info["experimental_only"] and not info["research_ready"]
            rewards, surveys = 0, []
            rng = np.random.default_rng(42)
            for day in range(240):
                public = env.state["mars_pest_public"]
                frame = obs[-len(FIELDS):]
                assert np.isclose(frame[indices["survey_value"]], public["survey_value"], atol=1e-7)
                assert np.isclose(frame[indices["survey_age"]] * 7, public["survey_age"], atol=1e-6)
                surveys.append(dict(public))
                masks = env.action_masks()
                ids = [int(rng.choice(np.flatnonzero(group))) for group in np.split(masks, (6, 15))]
                ids[2] = int(allow_spray and day in (20, 27) and masks[-1])
                obs, reward, terminated, truncated, info = env.step(ids)
                assert env.observation_space.contains(obs) and obs.shape == env.observation_space.shape
                assert "mars_pest_diagnostic" not in info and "density" not in info
                rewards += reward
                if terminated or truncated:
                    break
            assert terminated and not truncated
            assert abs(rewards - info["episode_result"]["net_return"]) < 1e-6
            assert all(0 <= s["survey_value"] <= 1 for s in surveys)
            cases.append({"allow_spray": allow_spray, "days": day + 1,
                          "episode_result": info["episode_result"], "survey_observations": surveys,
                          "policy_observation_shape": list(obs.shape), "private_density_excluded_from_info": True})
        finally:
            env.close()
    report = {"passed": True, "experimental_only": True, "research_ready": False, "cases": cases,
              "calibrated_parameters": False, "carbon_balance_validated": False}
    Path("/workspace/outputs/experimental_pest_env_verification.json").write_text(json.dumps(report, indent=2))
    print(json.dumps({"passed": True, "cases": [{k: c[k] for k in ("allow_spray", "days", "episode_result")} for c in cases]}, indent=2))


if __name__ == "__main__":
    main()
