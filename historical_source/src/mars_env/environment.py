"""No-pest Gymnasium integration prototype; raw profit rewards only.

Pest-enabled research runs fail closed until live damage writing is implemented.
Do not use this phase's results to test the proposal's pest hypotheses.
"""
import math
import gymnasium as gym
import numpy as np

from .dssat_backend import BackendContractError, DssatBackend
from .exogenous import SeasonExogenous
from .observations import OBSERVATION_SIZE, ObservationHistory, frame
from .resources import Action, ResourceLedger, ResourceRules


class CropManagementEnv(gym.Env):
    metadata = {"render_modes": []}
    observation_schema = "mars-no-pest-v1"

    def __init__(self, *, rules=None, beta=1.0, shock=None, grain_price=0.158,
                 pest_enabled=True, max_days=240, backend_factory=DssatBackend):
        super().__init__()
        if pest_enabled:
            raise BackendContractError("Pest-enabled environment requires a validated live damage writer")
        if not math.isfinite(grain_price) or grain_price < 0 or max_days < 1:
            raise ValueError("Invalid economics/time limit")
        self.rules = rules or ResourceRules()
        self.beta, self.shock = beta, shock
        self.grain_price, self.max_days = grain_price, max_days
        self.backend = backend_factory(pest_enabled=False)
        self.observation_space = gym.spaces.Box(-np.inf, np.inf, shape=(OBSERVATION_SIZE,), dtype=np.float32)
        self.action_space = gym.spaces.MultiDiscrete([len(self.rules.water_grid), len(self.rules.nitrogen_grid), 2])
        self.history = ObservationHistory()
        self.ended, self.broken = True, False
        self.ledger = None
        self.exogenous = None  # Privileged input; never include tapes in policy observations.

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self.ended, self.broken = True, True
        actual_seed = int(seed) if seed is not None else int(self.np_random.integers(10001, 2**31 - 1))
        self.exogenous = (options or {}).get("season")
        active_beta, active_shock = self.beta, self.shock
        if self.exogenous is not None:
            if not isinstance(self.exogenous, SeasonExogenous) or self.exogenous.horizon < self.max_days + 1:
                raise ValueError("Expected an external season covering max_days plus the final morning")
            actual_seed = self.exogenous.backend_seed
            active_beta, active_shock = self.exogenous.beta, self.exogenous.shock
        wgen_seed = self.exogenous.wgen_seed if self.exogenous is not None else None
        if wgen_seed is None:
            state = self.backend.reset(actual_seed)
        else:
            state = self.backend.reset(actual_seed, wgen_seed=wgen_seed)
        preplant_days = 0
        # DAP is clamped to zero before planting; use the actual FileX date.
        while state["yrdoy"] < self.backend.planting_yrdoy:
            state, done, _ = self.backend.step(0, 0)
            preplant_days += 1
            if done or preplant_days > 400:
                raise BackendContractError("Season ended or stalled before planting")
        self.state = state
        self.day = 0
        self.ledger = ResourceLedger.create(self.rules, active_beta, active_shock).open_day(0, int(state["istage"]))
        self.previous_action = Action()
        observation = self.history.reset(self._frame())
        self.ended, self.broken = False, False
        return observation, {"preplant_days": preplant_days, **self._episode_flags(),
                             "observation_schema": self.observation_schema, "seed": actual_seed}

    def _episode_flags(self):
        return {"pest_enabled": False}

    def _advance_backend(self, action):
        return self.backend.step(action.water_mm, action.nitrogen_kg_ha)

    def _frame(self):
        return frame(self.state, self.ledger, self.previous_action, self.grain_price, self.day)

    def action_masks(self):
        if self.ended or self.broken:
            raise BackendContractError("Reset before requesting action masks")
        return self.ledger.action_masks()

    def step(self, action):
        if self.ended or self.broken:
            raise BackendContractError("Reset before stepping this environment")
        decoded = self.rules.decode(action)
        self.ledger.validate(decoded)  # Reject before touching the simulator.
        try:
            state, terminated, outcome = self._advance_backend(decoded)
            ledger, cost = self.ledger.commit(decoded)
            revenue = 0.0
            if terminated:
                if outcome is None:
                    raise BackendContractError("Missing actual terminal outcome")
                revenue = outcome.harvested_grain_kg_ha * self.grain_price
            self.day += 1
            truncated = not terminated and self.day >= self.max_days
            self.ledger = ledger if terminated else ledger.open_day(self.day, int(state["istage"]))
            self.state, self.previous_action = state, decoded
            self.ended = bool(terminated or truncated)
            obs = self.history.append(self._frame())
            reward = revenue - cost.total
            info = {"raw_reward": reward, "cost": cost.total, "revenue": revenue, **self._episode_flags()}
            if terminated:
                info["episode_result"] = {"net_return": revenue - self.ledger.total_cost,
                    "harvested_grain_kg_ha": outcome.harvested_grain_kg_ha, "reason": outcome.reason,
                    "total_cost": self.ledger.total_cost, "water_mm": self.ledger.water_used,
                    "nitrogen_kg_ha": self.ledger.nitrogen_used, "sprays": self.ledger.sprays,
                    "water_cut_mm": self.ledger.water_cut_mm, "water_cut_day": self.ledger.announcement_day}
            # No episode_result or fabricated harvest revenue on administrative truncation.
            return obs, reward, bool(terminated), bool(truncated), info
        except Exception:
            self.broken = True
            raise

    def close(self):
        self.backend.close()
        self.ended = True
