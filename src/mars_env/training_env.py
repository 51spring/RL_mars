"""Addressed training seasons and deterministic unshaped held-out evaluation."""
import gymnasium as gym
import numpy as np

from .environment import CropManagementEnv
from .experimental_env import ExperimentalPestEnv
from .exogenous import WGEN_SEED_RANGES, generate_season
from .observations import OBSERVATION_SIZE
from .pests import pest_settings
from .policies import CHANNEL_SIZES, CompositePolicy, FrozenChannels, RulePolicy, channel_mask
from .resources import ResourceRules
from .rewards import PotentialRewardWrapper
from .process_backend import LegacyProcessBackend


class SeasonCycler(gym.Env):
    """Policy seeds do not enter common exogenous season addresses."""
    metadata = {"render_modes": []}

    def __init__(self, config, *, rank=0, n_envs=4, split="train", mode="no_pest", shaping=True,
                 reduction_probability=None):
        super().__init__()
        self.reduction_probability = reduction_probability
        if split not in ("train", "validation") or mode not in ("no_pest", "experimental_pest"):
            raise ValueError("Smoke learning/evaluation uses train or validation, never final test")
        if type(rank) is not int or type(n_envs) is not int or not 0 <= rank < n_envs:
            raise ValueError("Invalid training worker rank")
        self.config, self.rank, self.n_envs, self.split, self.mode = config, rank, n_envs, split, mode
        self.shaping = bool(shaping and config["reward_shaping"]["enabled"])
        self.rules = ResourceRules.from_config(config)
        self.action_space = gym.spaces.MultiDiscrete([6, 9, 2])
        self.observation_space = gym.spaces.Box(-np.inf, np.inf, shape=(OBSERVATION_SIZE,), dtype=np.float32)
        self.count = 0
        self.current = None
        self._resume_cursor = None

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        if options:
            raise ValueError("Season addresses are controlled by worker/split")
        if seed is not None:
            self.count = 0
        if self._resume_cursor is not None:
            self.count, self._resume_cursor = self._resume_cursor, None
        self.close()
        season_id = self.rank + self.count * self.n_envs
        if self.split == "train":
            # A long joint fit outruns the finite WGEN training partition; repeat it in order.
            low, high = WGEN_SEED_RANGES["train"]
            season_id %= high - low + 1
        self.count += 1
        season = generate_season(self.config, split=self.split, season_id=season_id,
                                 reduction_probability=self.reduction_probability)
        if self.mode == "no_pest":
            base = CropManagementEnv(pest_enabled=False, rules=self.rules,
                                     grain_price=self.config["economics"]["grain_usd_kg"],
                                     backend_factory=LegacyProcessBackend)
            reset_options = {"season": season}
        else:
            # Explicit integration-test assumptions; default research config stays uncalibrated.
            parameters, noise = pest_settings(self.config)
            base = ExperimentalPestEnv(season=season, parameters=parameters, noise_std=noise,
                                       rules=self.rules, grain_price=self.config["economics"]["grain_usd_kg"],
                                       backend_factory=lambda **kwargs: LegacyProcessBackend(mode="experimental_pest",
                                           parameters=parameters, noise_std=noise, season=season))
            reset_options = None
        reward_config = self.config["reward_shaping"]
        self.current = PotentialRewardWrapper(base, eta_by_stage=reward_config["eta_by_stage"],
                       scale=reward_config["scale"], gamma=reward_config["gamma"]) if self.shaping else base
        obs, info = self.current.reset(seed=None, options=reset_options)
        return obs, dict(info, external_split=self.split, external_season_id=season_id)

    def step(self, action):
        if self.current is None:
            raise ValueError("Reset training environment first")
        return self.current.step(action)

    def action_masks(self):
        if self.current is None:
            raise ValueError("Reset training environment first")
        return self.current.get_wrapper_attr("action_masks")()

    def restart_sequence(self):
        """Reuse the same validation columns when comparing checkpoints."""
        self.count = 0
        self._resume_cursor = None

    def season_cursor(self):
        return self.count

    def set_season_cursor(self, count):
        """Resume on the next unused season, discarding an incomplete season."""
        if type(count) is not int or count < 0:
            raise ValueError('Nonnegative season cursor required')
        self.close()
        self.count = count
        self._resume_cursor = count

    def close(self):
        if self.current is not None:
            self.current.close()
            self.current = None


class ChannelCycler(SeasonCycler):
    """Learn some action channels; the others come from the rule or frozen networks."""

    def __init__(self, config, *, learn, frozen=(), rank=0, n_envs=4, mode="experimental_pest",
                 reduction_probability=None):
        super().__init__(config, rank=rank, n_envs=n_envs, split="train", mode=mode,
                         reduction_probability=reduction_probability)
        self.learn = tuple(learn)
        sizes = [CHANNEL_SIZES[channel] for channel in self.learn]
        self.action_space = gym.spaces.Discrete(sizes[0]) if len(sizes) == 1 else gym.spaces.MultiDiscrete(sizes)
        self.frozen_specs = tuple(frozen)
        self.base_policy = None
        self.observation = None

    def _policy(self):
        if self.base_policy is None:  # Loaded inside the worker process, once.
            import torch
            from sb3_contrib import MaskablePPO
            torch.set_num_threads(1)
            deterministic = self.config["training"]["deterministic_policy"]
            self.base_policy = CompositePolicy(RulePolicy.from_config(self.config), tuple(
                FrozenChannels(MaskablePPO.load(path, device="cpu"), channels, deterministic)
                for path, channels in self.frozen_specs))
        return self.base_policy

    def reset(self, **kwargs):
        self.observation, info = super().reset(**kwargs)
        return self.observation, info

    def action_masks(self):
        return channel_mask(super().action_masks(), self.learn)

    def step(self, action):
        full_mask = super().action_masks()
        combined = self._policy().action(self.observation, full_mask, self.rules)
        for channel, value in zip(self.learn, np.atleast_1d(action), strict=True):
            combined[channel] = int(value)
        result = super().step(combined)
        self.observation = result[0]
        return result
