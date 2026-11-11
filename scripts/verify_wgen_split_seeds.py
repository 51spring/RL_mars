"""Check the WGEN allocation through the pinned DSSAT image and process bridge."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from mars_env.dssat_backend import DssatBackend
from mars_env.exogenous import WGEN_SEED_RANGES, allocate_weather_seed, generate_season, stream
from mars_env.process_backend import LegacyProcessBackend

FIELDS = ("rain", "tmin", "tmax", "srad")


def weather_trace(backend, gym_seed, wgen_seed, irrigation=False):
    trace = {}
    rendered_seed = None
    try:
        state = backend.reset(gym_seed, wgen_seed=wgen_seed)
        if isinstance(backend, DssatBackend):
            match = re.search(r"^\s*rseed1_ = (\d+)\s*$", backend._env._pdi_yaml, re.M)
            rendered_seed = int(match[1])
        for _ in range(400):
            date = int(state["yrdoy"])
            assert date not in trace
            trace[date] = tuple(float(state[field]) for field in FIELDS)
            state, done, outcome = backend.step(5 if irrigation and date == 1982090 else 0, 0)
            if done:
                return trace, rendered_seed, outcome.harvested_grain_kg_ha
        raise AssertionError("DSSAT did not reach a terminal outcome")
    finally:
        backend.close()


def compare(a, b, identical):
    common = a.keys() & b.keys()
    assert common
    equal = sum(a[day] == b[day] for day in common)
    assert (equal == len(common)) if identical else (equal < len(common))
    return {"common_days": len(common), "matching_days": equal}


def native(output, config, probes):
    from gym.utils import seeding

    roots = config["reproducibility"]["split_seeds"]

    def legacy_seed(split, address):
        gym_seed = int(stream(roots[split], address, "weather").integers(10001, 2**31 - 1))
        generator, _ = seeding.np_random(gym_seed)
        return gym_seed, int(generator.randint(10001, 99999))

    legacy_train = {}
    for address in range(37594):
        gym_seed, drawn = legacy_seed("train", address)
        legacy_train.setdefault(drawn, (address, gym_seed))
    legacy_matches = {}
    collision = None
    for split in ("validation", "test"):
        matches = []
        for address in range(1000):
            gym_seed, drawn = legacy_seed(split, address)
            if drawn in legacy_train:
                matches.append((address, gym_seed, drawn))
        legacy_matches[split] = len(matches)
        assert matches
        if split == "test":
            address, gym_seed, drawn = matches[0]
            train_address, train_gym_seed = legacy_train[drawn]
            collision = (train_address, address, train_gym_seed, gym_seed, drawn)

    train_address, test_address, train_gym_seed, test_gym_seed, drawn = collision
    a, a_seed, a_grain = weather_trace(DssatBackend(), train_gym_seed, None)
    b, b_seed, b_grain = weather_trace(DssatBackend(), test_gym_seed, None)
    assert a_seed == b_seed == drawn and a_grain == b_grain
    repeated_legacy = compare(a, b, identical=True)
    seed_a = allocate_weather_seed("train", roots["train"], train_address)
    seed_b = allocate_weather_seed("test", roots["test"], test_address)
    a, used_a, _ = weather_trace(DssatBackend(), train_gym_seed, seed_a)
    b, used_b, _ = weather_trace(DssatBackend(), test_gym_seed, seed_b)
    assert (used_a, used_b) == (seed_a, seed_b) and seed_a != seed_b
    separated = compare(a, b, identical=False)
    native_cases = {}
    for name, seed in probes.items():
        trace, rendered, _ = weather_trace(DssatBackend(), 123456, seed)
        assert rendered == seed
        native_cases[name] = {"rendered_wgen_seed": rendered, "weather": trace}
    output.write_text(json.dumps({
        "legacy_matches": legacy_matches,
        "legacy_collision": {"train_address": train_address, "test_address": test_address,
                             "wgen_seed": drawn, "grain_kg_ha": a_grain, **repeated_legacy},
        "fixed_pair": {"train_wgen_seed": seed_a, "test_wgen_seed": seed_b, **separated},
        "native_cases": native_cases,
    }, indent=2), encoding="utf-8")


def main(output):
    from mars_env.environment import CropManagementEnv
    from mars_env.experimental_env import ExperimentalPestEnv
    from mars_env.pests import PestParameters

    config = yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8"))
    roots = config["reproducibility"]["split_seeds"]
    totals = {"train": 37594, "validation": 1000, "test": 1000}
    seed_sets = {split: {allocate_weather_seed(split, roots[split], address) for address in range(count)}
                 for split, count in totals.items()}
    assert all(len(seed_sets[split]) == count for split, count in totals.items())
    assert len(set().union(*seed_sets.values())) == sum(totals.values())
    validation = generate_season(config, split="validation", season_id=0)
    probes = {f"{split}_{edge}": seed for split, bounds in WGEN_SEED_RANGES.items()
              for edge, seed in zip(("first", "last"), bounds, strict=True)}
    probes["validation_address_0"] = validation.wgen_seed
    native_path = output.with_name("native.json")
    subprocess.run(["/opt/gym_dssat_pdi/bin/python", str(Path(__file__).resolve()),
                    str(native_path), json.dumps(probes)], check=True)
    native_result = json.loads(native_path.read_text())
    native_trace = {int(day): tuple(values) for day, values in
                    native_result["native_cases"]["validation_address_0"]["weather"].items()}
    params = PestParameters(10, 30, alpha=0)
    environments = {
        "no_pest": CropManagementEnv(pest_enabled=False, backend_factory=LegacyProcessBackend),
        "experimental_pest": ExperimentalPestEnv(
            season=validation, parameters=params, noise_std=0.01,
            backend_factory=lambda **kwargs: LegacyProcessBackend(
                mode="experimental_pest", season=validation, parameters=params, noise_std=0.01, **kwargs)),
    }
    traces = {}
    bridge_checks = {}
    for mode, env in environments.items():
        try:
            opts = {"season": validation} if mode == "no_pest" else None
            _, info = env.reset(seed=42 if mode == "no_pest" else 43, options=opts)
            assert info["seed"] == validation.wgen_seed
            trace = {}
            for day in range(240):
                trace[int(env.state["yrdoy"])] = tuple(float(env.state[field]) for field in FIELDS)
                water = int(mode == "experimental_pest" and day == 30 and env.action_masks()[1])
                _, _, done, truncated, _ = env.step([water, 0, 0])
                assert not truncated
                if done:
                    break
            assert done
            traces[mode] = trace
            bridge_checks[mode] = compare(trace, native_trace, identical=True)
        finally:
            env.close()
    output.write_text(json.dumps({
        "passed": True, "image": os.environ["MARS_IMAGE_ID"], "planned_seasons": totals,
        "allocated_unique_seeds": len(set().union(*seed_sets.values())),
        "split_ranges": WGEN_SEED_RANGES, "bridge_validation": bridge_checks,
        "legacy_matches": native_result["legacy_matches"], "legacy_collision": native_result["legacy_collision"],
        "fixed_pair": native_result["fixed_pair"],
        "rendered_boundary_seeds": {key: native_result["native_cases"][key]["rendered_wgen_seed"] for key in probes},
        "common_weather_with_changed_actions": compare(*traces.values(), identical=True),
        "final_policy_evaluation_run": False,
    }, indent=2), encoding="utf-8")


if __name__ == "__main__":
    target = Path(sys.argv[1])
    if len(sys.argv) == 3:
        config = yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8"))
        native(target, config, json.loads(sys.argv[2]))
    else:
        main(target)
