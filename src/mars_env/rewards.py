"""Observation-only potential shaping with separately audited raw returns."""
import math

import gymnasium as gym
import numpy as np

from .observations import FIELDS, FRAME_SIZE, OBSERVATION_SIZE


class ObservationPotential:
    """Phi = grain price x eta(stage) x observed topwt. The price is a fixed environment constant."""
    def __init__(self, eta_by_stage, grain_price):
        if not eta_by_stage:
            raise ValueError("Explicit eta(stage) mapping required")
        if not math.isfinite(grain_price) or grain_price < 0:
            raise ValueError("Invalid grain price")
        self.grain_price = float(grain_price)
        self.eta_by_stage = dict(eta_by_stage)
        for stage, eta in self.eta_by_stage.items():
            if type(stage) is not int or not math.isfinite(eta) or eta < 0:
                raise ValueError("Invalid potential coefficient")
        self.indices = {name: (i, scale) for i, (name, scale) in enumerate(FIELDS)}

    def __call__(self, observation):
        observation = np.asarray(observation)
        if observation.shape != (OBSERVATION_SIZE,) or not np.isfinite(observation).all():
            raise ValueError(f"Expected finite {OBSERVATION_SIZE}-dimensional policy observation")
        latest = observation[-FRAME_SIZE:]
        def value(name):
            index, scale = self.indices[name]
            return float(latest[index]) * scale
        raw_stage = value("istage")
        stage = round(raw_stage)
        if abs(raw_stage - stage) > 1e-5 or stage not in self.eta_by_stage:
            raise ValueError("Missing eta for observed growth stage")
        phi = self.grain_price * self.eta_by_stage[stage] * value("topwt")
        if not math.isfinite(phi) or phi < 0:
            raise ValueError("Invalid observation-based potential")
        return phi


class PotentialRewardWrapper(gym.Wrapper):
    def __init__(self, env, *, eta_by_stage, scale=1000.0, gamma=1.0):
        super().__init__(env)
        if gamma != 1.0 or not math.isfinite(scale) or scale <= 0:
            raise ValueError("Proposal shaping requires gamma=1 and a positive finite reward scale")
        self.potential = ObservationPotential(eta_by_stage, env.unwrapped.grain_price)
        self.scale, self.gamma = scale, gamma
        self._ready = False

    def reset(self, **kwargs):
        self._ready = False
        obs, info = self.env.reset(**kwargs)
        self._initial_phi = self._phi = self.potential(obs)
        self._raw_sum = self._training_sum = 0.0
        self._ready = True
        return obs, info

    def action_masks(self):
        return self.env.get_wrapper_attr("action_masks")()

    def step(self, action):
        if not self._ready:
            raise ValueError("Reset before stepping a shaped episode")
        obs, reward, terminated, truncated, info = self.env.step(action)
        self._ready = False
        raw = float(info.get("raw_reward", reward))
        if not math.isfinite(raw) or not math.isclose(float(reward), raw, abs_tol=1e-10):
            raise ValueError("Potential wrapper requires an unshaped raw-reward environment")
        before = self._phi
        after = 0.0 if terminated else self.potential(obs)
        training_reward = (raw + after - before) / self.scale
        self._raw_sum += raw
        self._training_sum += training_reward
        self._phi = after
        info = dict(info, raw_reward=raw, training_reward=training_reward,
                    shaping_potential_before=before, shaping_potential_after=after)
        if terminated or truncated:
            residual = self.scale * self._training_sum - (self._raw_sum + after - self._initial_phi)
            info["reward_audit"] = {"raw_return": self._raw_sum, "training_return": self._training_sum,
                "initial_potential": self._initial_phi, "final_potential": after,
                "telescoping_residual": residual, "complete_episode": bool(terminated),
                "administrative_truncation": bool(truncated)}
            if abs(residual) > 1e-6 * max(1.0, abs(self._raw_sum), abs(self._initial_phi), abs(after)):
                raise ValueError("Potential reward telescoping identity failed")
        self._ready = not (terminated or truncated)
        return obs, training_reward, terminated, truncated, info
