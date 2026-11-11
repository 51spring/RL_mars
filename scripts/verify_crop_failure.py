"""Trigger a model-native failure using diagnostic deep planting, not an RL action."""
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, "/workspace/src")
from mars_env.dssat_backend import DssatBackend
from mars_env.environment import CropManagementEnv


def deep_planting(template):
    lines = template.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("@P PDATE"):
            row = lines[i + 1]
            spans = list(re.finditer(r"\S+", row))
            depth = line.split().index("PLDP")
            assert spans[depth].group() == "7", "Expected original UFGA8201 7cm planting depth"
            # Fixed five-character PLDP column, 100 cm diagnostic stress only.
            left, right = spans[depth - 1].end(), spans[depth].end()
            lines[i + 1] = row[:left] + "100".rjust(right - left) + row[right:]
            return "\n".join(lines) + "\n"
    raise RuntimeError("Missing planting row")


def factory(**kwargs):
    return DssatBackend(filex_transform=deep_planting, **kwargs)


def main():
    env = CropManagementEnv(pest_enabled=False, backend_factory=factory)
    try:
        _, info = env.reset(seed=123456)
        rewards = 0
        final = None
        for day in range(240):
            # One paid intervention, then no input: failure must preserve cost.
            _, reward, terminated, truncated, info = env.step([1, 1, 0] if day == 0 else [0, 0, 0])
            rewards += reward
            if terminated or truncated:
                final = info["episode_result"]
                break
        assert terminated and not truncated and final is not None
        assert final["reason"] == "crop_failure" and final["harvested_grain_kg_ha"] == 0
        assert info["revenue"] == 0 and final["total_cost"] > 0
        assert abs(rewards + final["total_cost"]) < 1e-8
        folder = Path(env.backend._env._tmp_folder)
        warning = (folder / "WARNING.OUT").read_text()
        report = {"passed": True, "diagnostic_only": True,
                  "scenario_change": "UFGA8201 planting depth 7cm -> 100cm; model equations unchanged",
                  "steps": day + 1, "terminal_stage": env.state["istage"],
                  "episode_result": final, "sum_raw_rewards": rewards,
                  "warning": warning, "agronomic_validation": False}
        Path("/workspace/outputs/crop_failure_verification.json").write_text(json.dumps(report, indent=2))
        print(json.dumps(report, indent=2))
    finally:
        env.close()


if __name__ == "__main__":
    main()
