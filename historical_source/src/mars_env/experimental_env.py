"""Explicit experimental pest environment; uncalibrated, never a research-ready alias."""
from .environment import CropManagementEnv
from .observations import frame
from .online_pests import ExperimentalOnlineBackend


class ExperimentalPestEnv(CropManagementEnv):
    observation_schema = "mars-experimental-pest-v1"

    def __init__(self, *, season, parameters, noise_std, rules=None, grain_price=0.158,
                 max_days=240, backend_factory=None):
        self.fixed_season = season
        factory = backend_factory or (lambda **kwargs: ExperimentalOnlineBackend(
            parameters=parameters, noise_std=noise_std, season=season))
        super().__init__(rules=rules, grain_price=grain_price, max_days=max_days,
                         pest_enabled=False, backend_factory=factory)

    def reset(self, *, seed=None, options=None):
        if options:
            raise ValueError("Set the external season at construction; tapes and weather must stay paired")
        return super().reset(seed=seed, options={"season": self.fixed_season})

    def _episode_flags(self):
        return {"pest_enabled": True, "experimental_only": True, "research_ready": False}

    def _advance_backend(self, action):
        return self.backend.step_online(action.water_mm, action.nitrogen_kg_ha, bool(action.spray))

    def _frame(self):
        return frame(self.state, self.ledger, self.previous_action, self.grain_price, self.day,
                     survey=self.state["mars_pest_public"])
