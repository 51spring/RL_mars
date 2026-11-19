"""Immutable resource accounting at the morning decision boundary.

Call open_day -> decode/validate -> advance backend -> commit. Keep the returned
ledger only after backend success; discard the episode on simulator failure.
The ledger includes hidden scenario state and must never be used as observation.
"""
from dataclasses import dataclass, replace
import math
import operator
from typing import Mapping

import numpy as np

EPS = 1e-8


def _integer(value, name):
    if isinstance(value, (bool, np.bool_)):
        raise ValueError(f"{name} must be an integer")
    try:
        return operator.index(value)
    except TypeError as exc:
        raise ValueError(f"{name} must be an integer") from exc


@dataclass(frozen=True)
class Action:
    water_mm: float = 0
    nitrogen_kg_ha: float = 0
    spray: int = 0


@dataclass(frozen=True)
class ResourceRules:
    water_grid: tuple = (0, 5, 10, 15, 20, 25)
    nitrogen_grid: tuple = (0, 10, 20, 27, 35, 40, 54, 60, 80)
    water_price: float = 1.17
    nitrogen_price: float = 1.83
    spray_price: float = 49.4
    irrigation_labor: float = 2.04
    nitrogen_labor: float = 34.8
    # No separate water money budget: it equalled supply x price and never bound first (decision_project.md 23).
    nitrogen_budget: float = 402.6
    spray_budget: float = 150
    initial_water: float = 200
    spray_interval: int = 7
    spray_stage_limit: int = 5
    input_closed_stage: int = 6  # physiological maturity to harvest: irrigation and nitrogen masked

    def __post_init__(self):
        for grid in (self.water_grid, self.nitrogen_grid):
            if not grid or grid[0] != 0 or any(not math.isfinite(x) or x < 0 for x in grid):
                raise ValueError("Grids must start with zero and contain finite nonnegative values")
            if any(b <= a for a, b in zip(grid, grid[1:])):
                raise ValueError("Grids must be strictly increasing")
        for name in ("water_price", "nitrogen_price", "spray_price", "irrigation_labor",
                     "nitrogen_labor", "nitrogen_budget", "spray_budget", "initial_water"):
            value = getattr(self, name)
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"Invalid {name}")
        for name in ("spray_interval", "spray_stage_limit", "input_closed_stage"):
            if _integer(getattr(self, name), name) < 0:
                raise ValueError(f"Invalid {name}")

    @classmethod
    def from_config(cls, config: Mapping):
        env, eco, mgmt = (config[k] for k in ("environment", "economics", "management"))
        budgets = eco["budgets_usd_ha"]
        rules = cls(
            water_grid=tuple(env["irrigation_grid_mm"]),
            nitrogen_grid=tuple(env["nitrogen_grid_kg_ha"]),
            water_price=eco["water_usd_mm_ha"], nitrogen_price=eco["nitrogen_usd_kg"],
            spray_price=eco["spray_product_usd_ha"] + eco["spray_labor_usd_ha"],
            irrigation_labor=eco["irrigation_labor_usd_event_ha"],
            nitrogen_labor=eco["nitrogen_labor_usd_event_ha"],
            nitrogen_budget=budgets["nitrogen"],
            spray_budget=budgets["spray"], initial_water=env["initial_water_mm"],
            spray_interval=mgmt["spray_interval_days"],
            spray_stage_limit=mgmt["spray_istage_exclusive_upper"],
            input_closed_stage=mgmt["input_closed_istage"],
        )
        if "water" in budgets:
            raise ValueError("Water is limited by the physical supply only; remove budgets_usd_ha.water")
        if config["environment"]["action_nvec"] != [len(rules.water_grid), len(rules.nitrogen_grid), 2]:
            raise ValueError("Action dimensions do not match configured grids")
        return rules

    def decode(self, indices):
        try:
            values = tuple(indices)
        except TypeError as exc:
            raise ValueError("Expected three action indices") from exc
        if len(values) != 3:
            raise ValueError("Expected three action indices")
        ids = tuple(_integer(v, "action index") for v in values)
        if any(i < 0 or i >= n for i, n in zip(ids, (len(self.water_grid), len(self.nitrogen_grid), 2))):
            raise ValueError("Action index out of range")
        return Action(self.water_grid[ids[0]], self.nitrogen_grid[ids[1]], ids[2])


@dataclass(frozen=True)
class WaterShock:
    """At most one reduction per season, with no advance notice.

    Main design: a fixed day after planting (``day`` set, ``stage`` None), so every
    policy in a season is cut on the same date. Auxiliary option: first entry into a
    growth stage plus a delay (``day`` None), whose date can differ between policies.
    """
    stage: int | None
    delay_days: int
    fraction: float
    contract: str = "remaining_fraction"
    day: int | None = None

    def __post_init__(self):
        if self.day is None:
            if _integer(self.stage, "shock stage") not in (1, 2, 4):
                raise ValueError("Shock stage must be 1, 2, or 4")
            if _integer(self.delay_days, "shock delay") < 0:
                raise ValueError("Negative announcement delay")
        else:
            if self.stage is not None or _integer(self.delay_days, "shock delay") != 0:
                raise ValueError("A calendar-day shock takes no stage or delay")
            if _integer(self.day, "shock day") < 0:
                raise ValueError("Negative shock day")
        if not math.isfinite(self.fraction) or not 0 <= self.fraction <= 1:
            raise ValueError("Shock fraction must be between zero and one")
        if self.contract not in ("remaining_fraction", "total_entitlement"):
            raise ValueError("Unknown reduction contract")

    @classmethod
    def on_day(cls, day, fraction, contract="remaining_fraction"):
        return cls(None, 0, fraction, contract, day)


@dataclass(frozen=True)
class Cost:
    water: float
    nitrogen: float
    spray: float
    labor: float

    @property
    def total(self):
        return self.water + self.nitrogen + self.spray + self.labor


@dataclass(frozen=True)
class ResourceLedger:
    rules: ResourceRules
    beta: float
    nitrogen_budget_left: float
    spray_budget_left: float
    water_left: float
    shock: WaterShock | None = None
    water_used: float = 0
    nitrogen_used: float = 0
    sprays: int = 0
    last_spray_day: int | None = None
    total_cost: float = 0
    stage_entry_day: int | None = None
    announcement_day: int | None = None
    water_cut_mm: float = 0
    day: int = -1
    stage: int = 7
    committed: bool = True

    @classmethod
    def create(cls, rules=None, beta=1.0, shock=None):
        rules = rules or ResourceRules()
        if not math.isfinite(beta) or beta < 0:
            raise ValueError("Invalid budget multiplier")
        return cls(rules, beta, beta * rules.nitrogen_budget,
                   beta * rules.spray_budget, rules.initial_water, shock)

    def open_day(self, day, stage):
        day, stage = _integer(day, "day"), _integer(stage, "stage")
        if day <= self.day or not self.committed:
            raise ValueError("Days must advance after committing the previous decision")
        if stage not in range(1, 10):
            raise ValueError("Invalid DSSAT stage")
        entry, announced, water = self.stage_entry_day, self.announcement_day, self.water_left
        cut = self.water_cut_mm
        if self.shock:
            if self.shock.day is not None:
                due = day >= self.shock.day
            else:
                if entry is None and stage == self.shock.stage:
                    entry = day
                due = entry is not None and day >= entry + self.shock.delay_days
            if due and announced is None:
                reduced = ((1 - self.shock.fraction) * water if self.shock.contract == "remaining_fraction"
                           else max(0, (1 - self.shock.fraction) * self.rules.initial_water - self.water_used))
                cut, water, announced = water - reduced, reduced, day
        return replace(self, day=day, stage=stage, committed=False, stage_entry_day=entry,
                       announcement_day=announced, water_left=water, water_cut_mm=cut)

    def _require_open(self):
        if self.day < 0 or self.committed:
            raise ValueError("Open a decision day before using actions")

    def action_masks(self):
        self._require_open()
        r = self.rules
        closed = self.stage == r.input_closed_stage
        water = [x <= self.water_left + EPS and not (closed and x > 0) for x in r.water_grid]
        nitrogen = [x * r.nitrogen_price <= self.nitrogen_budget_left + EPS and not (closed and x > 0)
                    for x in r.nitrogen_grid]
        spray = (r.spray_price <= self.spray_budget_left + EPS
                 and self.stage < r.spray_stage_limit
                 and (self.last_spray_day is None or self.day - self.last_spray_day >= r.spray_interval))
        return np.asarray(water + nitrogen + [True, spray], dtype=bool)

    def validate(self, action):
        self._require_open()
        if (not isinstance(action, Action) or action.water_mm not in self.rules.water_grid
                or action.nitrogen_kg_ha not in self.rules.nitrogen_grid
                or isinstance(action.spray, (bool, np.bool_))):
            raise ValueError("Action must belong to the common grid")
        spray = _integer(action.spray, "spray")
        if spray not in (0, 1):
            raise ValueError("Spray must be zero or one")
        indices = (self.rules.water_grid.index(action.water_mm),
                   self.rules.nitrogen_grid.index(action.nitrogen_kg_ha), spray)
        mask = self.action_masks()
        if not all(mask[offset + i] for offset, i in zip((0, len(self.rules.water_grid),
                     len(self.rules.water_grid) + len(self.rules.nitrogen_grid)), indices)):
            raise ValueError("Action violates budget, physical inventory, or spray rules")
        return action

    def commit(self, action):
        self.validate(action)
        r = self.rules
        cost = Cost(action.water_mm * r.water_price, action.nitrogen_kg_ha * r.nitrogen_price,
                    action.spray * r.spray_price,
                    (r.irrigation_labor if action.water_mm > 0 else 0)
                    + (r.nitrogen_labor if action.nitrogen_kg_ha > 0 else 0))
        result = replace(
            self, nitrogen_budget_left=max(0, self.nitrogen_budget_left - cost.nitrogen),
            spray_budget_left=max(0, self.spray_budget_left - cost.spray),
            water_left=max(0, self.water_left - action.water_mm),
            water_used=self.water_used + action.water_mm,
            nitrogen_used=self.nitrogen_used + action.nitrogen_kg_ha,
            sprays=self.sprays + action.spray,
            last_spray_day=self.day if action.spray else self.last_spray_day,
            total_cost=self.total_cost + cost.total, committed=True,
        )
        return result, cost

    def announcement(self):
        """Only this public bulletin may enter observations; never expose shock."""
        if self.announcement_day is None:
            return {"announced": False, "fraction": 0.0, "days_since": 0}
        return {"announced": True, "fraction": self.shock.fraction,
                "days_since": self.day - self.announcement_day}
