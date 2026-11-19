"""Versioned, explicit 28-field daily observation (7-day history -> 196 inputs).

2026-11-11 revision (decision_project.md 22-23): constant fields (initial supply and budgets, prices,
labour, survey availability), duplicates (season_day, budget ratios, has_sprayed) and wtdep removed;
sw is the volumetric water content averaged over the root zone instead of the whole profile.
"""
from collections import deque
import numpy as np

# Fixed scales do not depend on policy or training statistics.
FIELDS = (
    ("dap", 200), ("istage", 10), ("vstage", 30), ("xlai", 10),
    ("topwt", 20000), ("grnwt", 15000), ("rtdep", 300),
    ("swfac", 1), ("nstres", 1), ("sw", 0.15), ("ep", 20),
    ("rain", 100), ("tmax", 50), ("srad", 40), ("dtt", 50),
    ("water_used", 200), ("nitrogen_used", 220), ("sprays", 4), ("water_left", 200),
    ("announced", 1), ("reduction_fraction", 1), ("days_since_announcement", 200),
    ("survey_value", 1), ("survey_age", 7), ("days_since_spray", 200),
    ("previous_water", 25), ("previous_nitrogen", 80), ("previous_spray", 1),
)
FRAME_SIZE = len(FIELDS)
HISTORY_DAYS = 7
OBSERVATION_SIZE = FRAME_SIZE * HISTORY_DAYS
assert FRAME_SIZE == 28
DSSAT_FIELDS = ("dap", "istage", "vstage", "xlai", "topwt", "grnwt", "rtdep", "swfac", "nstres", "ep",
                "rain", "tmax", "srad", "dtt")


def root_zone_water(sw, thickness, root_depth):
    """Thickness-weighted volumetric water over the layers reached by roots (top layer before rooting)."""
    sw, thickness = np.asarray(sw, dtype=float), np.asarray(thickness, dtype=float)
    if sw.ndim != 1 or sw.shape != thickness.shape or not np.all(thickness > 0):
        raise ValueError("Invalid DSSAT layer water/thickness")
    top = np.concatenate(([0.0], np.cumsum(thickness)[:-1]))
    depth = max(float(root_depth), float(thickness[0]))
    weights = np.clip(depth - top, 0, thickness)
    return float(np.average(sw, weights=weights))


def frame(state, ledger, previous_action, grain_price, season_day, *, survey=None):
    values = {k: state[k] for k in DSSAT_FIELDS}
    values["sw"] = root_zone_water(state["sw"], state["dlayr"], state["rtdep"])
    bulletin = ledger.announcement()
    values.update(
        water_used=ledger.water_used, nitrogen_used=ledger.nitrogen_used, sprays=ledger.sprays,
        water_left=ledger.water_left,
        announced=bulletin["announced"], reduction_fraction=bulletin["fraction"],
        days_since_announcement=bulletin["days_since"],
        # No-pest prototype: no survey reading (value and age 0).
        survey_value=0, survey_age=0,
        days_since_spray=season_day - ledger.last_spray_day if ledger.last_spray_day is not None else 0,
        previous_water=previous_action.water_mm, previous_nitrogen=previous_action.nitrogen_kg_ha,
        previous_spray=previous_action.spray,
    )
    if survey is not None:
        if set(survey) != {"survey_value", "survey_age", "survey_available"}:
            raise ValueError("Only public survey fields may enter policy observations")
        if not 0 <= survey["survey_value"] <= 1 or survey["survey_age"] < 0 or survey["survey_available"] not in (False, True):
            raise ValueError("Invalid public survey reading")
        values.update(survey_value=survey["survey_value"], survey_age=survey["survey_age"])
    result = np.asarray([values[name] / scale for name, scale in FIELDS], dtype=np.float32)
    if not np.isfinite(result).all():
        raise ValueError("Non-finite policy observation")
    return result


class ObservationHistory:
    def __init__(self, days=HISTORY_DAYS):
        if days <= 0:
            raise ValueError("Positive history length required")
        self.days = days
        self.frames = deque(maxlen=days)

    def reset(self, initial):
        self.frames.clear()
        self.frames.extend(initial.copy() for _ in range(self.days))
        return self.value()

    def append(self, current):
        if not self.frames:
            raise ValueError("Reset history before appending")
        self.frames.append(current.copy())
        return self.value()

    def value(self):
        return np.concatenate(tuple(self.frames))
