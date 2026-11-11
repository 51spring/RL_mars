from pathlib import Path
import unittest

import numpy as np
import yaml

from test_environment import FakeBackend
from mars_env.environment import CropManagementEnv
from mars_env.dssat_backend import TerminalOutcome
from mars_env.observations import FIELDS, FRAME_SIZE, OBSERVATION_SIZE
from mars_env.rewards import ObservationPotential, PotentialRewardWrapper


class RewardTests(unittest.TestCase):
    def create(self, **kwargs):
        env = PotentialRewardWrapper(CropManagementEnv(pest_enabled=False, backend_factory=FakeBackend, **kwargs),
                                     eta_by_stage={stage: 0.45 for stage in range(1, 11)})
        self.addCleanup(env.close)
        return env

    def test_completed_shaped_return_preserves_raw_economic_result(self):
        env = self.create()
        env.reset(seed=1)
        _, a, _, _, info = env.step([2, 3, 0])
        self.assertNotIn('reward_audit', info)  # A rollout boundary is not episode termination.
        _, b, terminated, truncated, info = env.step([0, 0, 0])
        self.assertTrue(terminated)
        self.assertFalse(truncated)
        audit = info['reward_audit']
        self.assertEqual(audit['final_potential'], 0)
        self.assertAlmostEqual((a + b) * 1000, info['episode_result']['net_return'] - audit['initial_potential'])
        self.assertAlmostEqual(audit['raw_return'], info['episode_result']['net_return'])
        self.assertEqual(env.action_space.nvec.tolist(), [6, 9, 2])

    def test_administrative_truncation_retains_potential_and_has_no_fake_harvest(self):
        env = self.create(max_days=1)
        env.reset()
        _, _, terminated, truncated, info = env.step([1, 0, 0])
        self.assertFalse(terminated)
        self.assertTrue(truncated)
        self.assertGreater(info['reward_audit']['final_potential'], 0)
        self.assertNotIn('episode_result', info)
        self.assertEqual(info['revenue'], 0)

    def test_failure_forces_zero_terminal_potential_and_keeps_cost(self):
        class Failure(FakeBackend):
            def step(self, water, nitrogen):
                state, done, outcome = super().step(water, nitrogen)
                if done:
                    outcome = TerminalOutcome('crop_failure', 0, {})
                return state, done, outcome
        base = CropManagementEnv(pest_enabled=False, backend_factory=Failure)
        env = PotentialRewardWrapper(base, eta_by_stage={1: 0.45})
        self.addCleanup(env.close)
        env.reset()
        env.step([1, 0, 0])
        _, _, _, _, info = env.step([0, 0, 0])
        self.assertLess(info['episode_result']['net_return'], 0)
        self.assertEqual(info['reward_audit']['final_potential'], 0)

    def test_initial_history_and_masks_are_forwarded(self):
        env = self.create()
        obs, _ = env.reset()
        self.assertEqual(obs.shape, (OBSERVATION_SIZE,))
        np.testing.assert_array_equal(env.action_masks(), env.unwrapped.action_masks())

    def test_unknown_stage_and_bad_discount_are_rejected(self):
        with self.assertRaises(ValueError):
            PotentialRewardWrapper(CropManagementEnv(pest_enabled=False, backend_factory=FakeBackend),
                                   eta_by_stage={1: 0.45}, gamma=0.99)
        env = self.create()
        obs, _ = env.reset()
        obs = obs.copy()
        obs[-FRAME_SIZE + [name for name, _ in FIELDS].index('istage')] = 0.3
        with self.assertRaises(ValueError):
            ObservationPotential({1: 0.45}, 0.158)(obs)

    def test_potential_uses_the_environment_grain_price(self):
        env = self.create()
        obs, _ = env.reset()
        topwt = obs[-FRAME_SIZE + [name for name, _ in FIELDS].index('topwt')] * 20000
        self.assertAlmostEqual(env.potential(obs), 0.158 * 0.45 * topwt, places=4)

    def test_project_config_has_no_duplicate_mapping_keys(self):
        class UniqueLoader(yaml.SafeLoader):
            pass
        def mapping(loader, node, deep=False):
            keys = [loader.construct_object(key, deep=deep) for key, _ in node.value]
            if len(set(keys)) != len(keys):
                raise ValueError('Duplicate project configuration key')
            return yaml.SafeLoader.construct_mapping(loader, node, deep=deep)
        UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
        source = Path(__file__).parents[1] / 'configs/proposal_v2.yaml'
        config = yaml.load(source.read_text(), Loader=UniqueLoader)
        self.assertEqual(config['training']['gamma'], config['reward_shaping']['gamma'])


if __name__ == '__main__':
    unittest.main()
