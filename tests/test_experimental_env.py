import unittest
import numpy as np

from test_environment import FakeBackend
from mars_env.dssat_backend import BackendContractError
from mars_env.experimental_env import ExperimentalPestEnv
from mars_env.exogenous import SeasonExogenous
from mars_env.observations import FIELDS, FRAME_SIZE
from mars_env.pests import PestParameters


class SurveyFake(FakeBackend):
    def reset(self, seed):
        state = super().reset(seed)
        state['mars_pest_public'] = dict(survey_value=0.25, survey_age=0, survey_available=True)
        state['mars_pest_diagnostic'] = {'density': 0.99, 'future': [1, 2, 3]}
        return state

    def step_online(self, water, nitrogen, spray):
        self.received_spray = spray
        state, done, outcome = super().step(water, nitrogen)
        state['mars_pest_public'] = dict(survey_value=0.25, survey_age=1, survey_available=True)
        return state, done, outcome


class ExperimentalEnvironmentTests(unittest.TestCase):
    def make_env(self, backend=SurveyFake):
        season = SeasonExogenous('test', 33001, 0, 12345, 1, None, np.zeros(400), np.zeros(400))
        env = ExperimentalPestEnv(season=season, parameters=PestParameters(10, 30), noise_std=0.01,
                                  backend_factory=backend)
        self.addCleanup(env.close)
        return env

    def test_public_survey_only_and_experimental_status(self):
        env = self.make_env()
        obs, info = env.reset(seed=3)
        names = [k for k, _ in FIELDS]
        self.assertAlmostEqual(obs[-FRAME_SIZE:][names.index('survey_value')], 0.25)
        self.assertNotIn('density', names)
        self.assertTrue(info['experimental_only'])
        self.assertFalse(info['research_ready'])
        self.assertNotIn('mars_pest_diagnostic', info)

    def test_spray_reaches_backend_and_is_charged(self):
        env = self.make_env()
        env.reset()
        obs, reward, _, _, info = env.step([0, 0, 1])
        self.assertTrue(env.backend.received_spray)
        self.assertEqual(reward, -50)
        self.assertEqual(env.ledger.sprays, 1)
        self.assertTrue(info['pest_enabled'])

    def test_private_fields_in_public_survey_fail_closed_on_reset(self):
        class BadSurvey(SurveyFake):
            def reset(self, seed):
                state = super().reset(seed)
                state['mars_pest_public']['density'] = 0.9
                return state
        env = self.make_env(BadSurvey)
        with self.assertRaises(ValueError):
            env.reset()
        with self.assertRaises(BackendContractError):
            env.action_masks()


if __name__ == '__main__':
    unittest.main()
