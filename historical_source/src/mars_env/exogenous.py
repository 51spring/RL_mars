"""Addressable independent streams; common season columns never use a policy seed."""
from dataclasses import dataclass, replace
import hashlib
from math import gcd
import operator

import numpy as np

from .resources import WaterShock

STREAM_IDS = {"weather": 11, "pest_arrival": 23, "survey_noise": 37, "reduction": 53, "budget": 71}
STREAM_VERSION = 1
WEATHER_SEED_VERSION = 1
WGEN_SEED_RANGES = {"train": (10001, 99998), "validation": (1, 4999), "test": (5000, 9999)}


def _index(value, name):
    if isinstance(value, (bool, np.bool_)):
        raise ValueError(f"Invalid {name}")
    try:
        result = operator.index(value)
    except TypeError as exc:
        raise ValueError(f"Invalid {name}") from exc
    if result < 0 or result > 2**32 - 1:
        raise ValueError(f"{name} outside uint32 range")
    return result


def allocate_weather_seed(split, base_seed, season_id):
    """Map season IDs bijectively onto one finite WGEN partition."""
    if split not in WGEN_SEED_RANGES:
        raise ValueError("Unknown WGEN split")
    low, high = WGEN_SEED_RANGES[split]
    size = high - low + 1
    season_id = _index(season_id, "season id")
    if season_id >= size:
        raise ValueError(f"WGEN {split} supports {size} unique seasons; got season_id {season_id}")
    root = _index(base_seed, "split seed")
    key = hashlib.sha256(f"mars-wgen-v{WEATHER_SEED_VERSION}:{split}:{root}".encode("ascii")).digest()
    offset = int.from_bytes(key[:8], "big") % size
    stride = 1 + int.from_bytes(key[8:16], "big") % (size - 1)
    while gcd(stride, size) != 1:
        stride += 1
    return low + (offset + stride * season_id) % size


def stream(base_seed, season_id, name):
    if name not in STREAM_IDS:
        raise ValueError("Unknown external stream")
    sequence = np.random.SeedSequence([_index(base_seed, "base seed"), _index(season_id, "season id"),
                                      STREAM_VERSION, STREAM_IDS[name]])
    return np.random.default_rng(sequence)


@dataclass(frozen=True)
class SeasonExogenous:
    split: str
    base_seed: int
    season_id: int
    backend_seed: int
    beta: float
    shock: WaterShock | None
    pest_arrivals: np.ndarray
    survey_standard_noise: np.ndarray
    weather_seed_version: int | None = None

    def __post_init__(self):
        _index(self.base_seed, "base seed")
        _index(self.season_id, "season id")
        _index(self.backend_seed, "backend seed")
        if self.weather_seed_version is not None:
            if type(self.weather_seed_version) is not int or self.weather_seed_version != WEATHER_SEED_VERSION:
                raise ValueError("Unsupported WGEN seed version")
            if self.backend_seed != allocate_weather_seed(self.split, self.base_seed, self.season_id):
                raise ValueError("Backend seed does not match the season's WGEN allocation")
        if not np.isfinite(self.beta) or self.beta < 0 or (self.shock is not None and not isinstance(self.shock, WaterShock)):
            raise ValueError("Invalid external season condition")
        arrivals = np.array(self.pest_arrivals, dtype=np.float64, copy=True)
        noise = np.array(self.survey_standard_noise, dtype=np.float64, copy=True)
        if (arrivals.ndim != 1 or arrivals.size == 0 or noise.shape != arrivals.shape
                or not np.isfinite(arrivals).all() or not np.isfinite(noise).all() or (arrivals < 0).any()):
            raise ValueError("Invalid external daily arrays")
        for name, array in (("pest_arrivals", arrivals), ("survey_standard_noise", noise)):
            array.setflags(write=False)
            object.__setattr__(self, name, array)

    @property
    def wgen_seed(self):
        return self.backend_seed if self.weather_seed_version is not None else None

    @property
    def horizon(self):
        return len(self.pest_arrivals)

    def paired_digest(self):
        digest = hashlib.sha256()
        digest.update(f"mars-exogenous-v{STREAM_VERSION}:{self.backend_seed}:".encode("ascii"))
        if self.weather_seed_version is not None:
            digest.update(f"wgen-v{self.weather_seed_version}:".encode("ascii"))
        for array in (self.pest_arrivals, self.survey_standard_noise):
            digest.update(np.asarray(array, dtype="<f8").tobytes())
        return digest.hexdigest()

    def with_condition(self, *, beta, shock):
        if not np.isfinite(beta) or beta < 0 or (shock is not None and not isinstance(shock, WaterShock)):
            raise ValueError("Invalid evaluation condition")
        return replace(self, beta=float(beta), shock=shock)

    def manifest(self):
        weather = {} if self.wgen_seed is None else {
            "weather_seed_version": self.weather_seed_version, "wgen_seed": self.wgen_seed}
        return {**weather, "stream_version": STREAM_VERSION, "numpy_version": np.__version__, "split": self.split,
                "base_seed": self.base_seed, "season_id": self.season_id, "backend_seed": self.backend_seed,
                "horizon": self.horizon, "beta": self.beta,
                "shock": None if self.shock is None else vars(self.shock), "paired_digest": self.paired_digest()}


def evaluation_conditions(config):
    """The fixed final-test grid: {name: shock or None}; ``none`` plus timing x rate.

    Calendar timing fixes the reduction day after planting, so the date is a property
    of the condition and never of a policy's own growth trajectory.
    """
    scenario = config["scenarios"]
    contract = scenario["reduction_contract"]
    conditions = {"none": None}
    if scenario["timing"] == "calendar_day":
        for timing, day in scenario["evaluation_days"].items():
            for rate in scenario["evaluation_reductions"]:
                conditions[f"{timing}_{round(100 * rate)}"] = WaterShock.on_day(day, rate, contract)
    elif scenario["timing"] == "stage_entry":
        for stage in scenario["announcement_istages"]:
            for rate in scenario["evaluation_reductions"]:
                conditions[f"stage{stage}_{round(100 * rate)}"] = WaterShock(
                    stage, scenario["evaluation_delay_days"], rate, contract)
    else:
        raise ValueError("Unknown reduction timing")
    return conditions


def generate_season(config, *, split, season_id, horizon=400, reduction_probability=None):
    """``reduction_probability`` overrides the config, e.g. 0 for the a-policy regime.

    The override changes only whether the sampled reduction is applied; weather, pests,
    budget and the sampled reduction itself stay identical for the same season address.
    """
    reproducibility = config["reproducibility"]
    version = reproducibility.get("weather_seed_version", WEATHER_SEED_VERSION)
    if type(version) is not int or version != WEATHER_SEED_VERSION:
        raise ValueError("Unsupported WGEN seed version in config")
    roots = reproducibility["split_seeds"]
    if split not in roots or len(set(roots.values())) != len(roots):
        raise ValueError("Unknown split or overlapping split root seeds")
    _index(season_id, "season id")
    if _index(horizon, "horizon") == 0:
        raise ValueError("Positive horizon required")
    root = _index(roots[split], "split seed")
    scenario, pest = config["scenarios"], config["pest"]
    arrival_probability, amplitude = pest["arrival_probability"], pest["arrival_amplitude"]
    if not 0 <= arrival_probability <= 1 or not np.isfinite(amplitude) or amplitude < 0:
        raise ValueError("Invalid pest arrival parameters")
    backend_seed = allocate_weather_seed(split, root, season_id)
    # Draw one value for every planting-relative day, independent of actions/survey schedules.
    arrivals = amplitude * (stream(root, season_id, "pest_arrival").random(horizon) < arrival_probability)
    noise = stream(root, season_id, "survey_noise").standard_normal(horizon)
    reduction = stream(root, season_id, "reduction")
    probability = scenario["reduction_probability"] if reduction_probability is None else reduction_probability
    low, high = scenario["training_reduction_range"]
    delay_low, delay_high = scenario["delay_days_inclusive"]
    day_low, day_high = scenario["training_day_range_inclusive"]
    if (not 0 <= probability <= 1 or not 0 <= low <= high <= 1 or not 0 <= delay_low <= delay_high
            or not 0 <= day_low <= day_high):
        raise ValueError("Invalid reduction distribution")
    # Sample all scenario components even when no reduction occurs. The calendar day is
    # drawn last so the stage-entry option reproduces its earlier draws exactly.
    occurs = reduction.random() < probability
    stage = int(reduction.choice(scenario["announcement_istages"]))
    delay = int(reduction.integers(delay_low, delay_high + 1))
    fraction = float(reduction.uniform(low, high))
    day = int(reduction.integers(day_low, day_high + 1))
    if scenario["timing"] == "calendar_day":
        sampled = WaterShock.on_day(day, fraction, scenario["reduction_contract"])
    elif scenario["timing"] == "stage_entry":
        sampled = WaterShock(stage, delay, fraction, scenario["reduction_contract"])
    else:
        raise ValueError("Unknown reduction timing")
    beta = float(stream(root, season_id, "budget").choice(config["economics"]["budget_multipliers"]))
    if not np.isfinite(beta) or beta < 0:
        raise ValueError("Invalid sampled budget")
    arrivals.setflags(write=False)
    noise.setflags(write=False)
    return SeasonExogenous(split, root, int(season_id), backend_seed, beta,
                           sampled if occurs else None, arrivals, noise, WEATHER_SEED_VERSION)
