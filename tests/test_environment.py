from dataclasses import replace
from pathlib import Path
import unittest

import numpy as np

from mars_env.dssat_backend import (BackendContractError, DssatBackend, TerminalOutcome,
                                    classify_terminal, terminal_template, read_summary)
from mars_env.environment import CropManagementEnv
from mars_env.observations import FIELDS, FRAME_SIZE, OBSERVATION_SIZE, root_zone_water
from mars_env.resources import WaterShock
from mars_env.exogenous import SeasonExogenous


def crop(day=0):
    state = dict(dap=day, istage=1, vstage=5, xlai=2, topwt=1000, grnwt=0,
                 rtdep=50, swfac=0.1, nstres=0.2, wtdep=100, ep=1,
                 rain=0, tmax=25, srad=20, dtt=10, yrdoy=1982057 + day,
                 sw=np.array([0.1, 0.3]), dlayr=np.array([10, 30]))
    return state


class FakeBackend:
    planting_yrdoy = 1982057

    def __init__(self, **kwargs):
        self.calls = 0
        self.crash = False

    def reset(self, seed):
        self.calls = 0
        return crop()

    def step(self, water, nitrogen):
        if self.crash:
            raise RuntimeError("simulator failed")
        self.calls += 1
        state = crop(self.calls)
        done = self.calls == 2
        if done:
            state.update(istage=10, grnwt=1000)
        return state, done, TerminalOutcome("harvest", 1000, {}) if done else None

    def close(self):
        pass


class EnvironmentTests(unittest.TestCase):
    def test_external_season_controls_backend_seed_and_initial_conditions(self):
        env = self.make_env(beta=1)
        season = SeasonExogenous("test", 33001, 1, 12345, 0,
                                 WaterShock(1, 0, 1), np.zeros(400), np.zeros(400))
        obs, info = env.reset(seed=999, options={"season": season})
        self.assertEqual(info["seed"], 12345)
        self.assertEqual(env.ledger.beta, 0)
        self.assertEqual(env.ledger.water_left, 0)
        self.assertEqual(env.action_masks().sum(), 3)
        self.assertNotIn("pest_arrivals", info)

    def make_env(self, **kwargs):
        env = CropManagementEnv(pest_enabled=False, backend_factory=FakeBackend, **kwargs)
        self.addCleanup(env.close)
        return env

    def test_harvest_net_return_matches_sum_of_raw_rewards(self):
        env = self.make_env()
        obs, _ = env.reset(seed=1)
        self.assertEqual(obs.shape, (OBSERVATION_SIZE,))
        self.assertEqual(OBSERVATION_SIZE, 196)
        self.assertTrue(env.observation_space.contains(obs))
        _, r1, terminated, truncated, _ = env.step([2, 3, 0])
        self.assertFalse(terminated or truncated)
        _, r2, terminated, truncated, info = env.step([0, 0, 0])
        self.assertTrue(terminated)
        self.assertFalse(truncated)
        self.assertAlmostEqual(r1 + r2, info["episode_result"]["net_return"])
        self.assertAlmostEqual(info["episode_result"]["total_cost"], 10 * 1.17 + 27 * 1.83 + 2.04 + 34.8)
        self.assertEqual(info["revenue"], 158)

    def test_time_limit_has_no_harvest_and_no_episode_result(self):
        env = self.make_env(max_days=1)
        env.reset(seed=2)
        _, reward, terminated, truncated, info = env.step([1, 0, 0])
        self.assertFalse(terminated)
        self.assertTrue(truncated)
        self.assertAlmostEqual(reward, -(5 * 1.17 + 2.04))
        self.assertEqual(info["revenue"], 0)
        self.assertNotIn("episode_result", info)
        with self.assertRaises(BackendContractError):
            env.step([0, 0, 0])

    def test_invalid_action_never_touches_backend(self):
        env = self.make_env(beta=0)
        env.reset(seed=1)
        ledger = env.ledger
        with self.assertRaises(ValueError):
            env.step([0, 1, 0])
        self.assertEqual(env.backend.calls, 0)
        self.assertEqual(env.ledger, ledger)
        env.step([0, 0, 0])

    def test_backend_failure_invalidates_episode_without_debit(self):
        env = self.make_env()
        env.reset(seed=1)
        ledger = env.ledger
        env.backend.crash = True
        with self.assertRaises(RuntimeError):
            env.step([1, 0, 0])
        self.assertEqual(env.ledger, ledger)
        with self.assertRaises(BackendContractError):
            env.action_masks()

    def test_history_reset_does_not_mix_seasons(self):
        env = self.make_env()
        initial, _ = env.reset(seed=1)
        self.assertTrue(all(np.array_equal(initial[:FRAME_SIZE], v) for v in initial.reshape(7, FRAME_SIZE)))
        env.step([1, 0, 0])
        again, _ = env.reset(seed=1)
        np.testing.assert_array_equal(initial, again)

    def test_hidden_shock_does_not_change_preannouncement_observation(self):
        a = self.make_env(shock=WaterShock(2, 0, 0.2))
        b = self.make_env(shock=WaterShock(2, 0, 0.6))
        np.testing.assert_array_equal(a.reset(seed=1)[0], b.reset(seed=1)[0])

    def test_observation_has_no_constant_or_duplicate_fields(self):
        names = [name for name, _ in FIELDS]
        for removed in ("initial_water", "initial_water_budget", "initial_nitrogen_budget", "initial_spray_budget",
                        "grain_price", "water_price", "nitrogen_price", "spray_price", "irrigation_labor",
                        "nitrogen_labor", "survey_available", "season_day", "water_budget_ratio",
                        "nitrogen_budget_ratio", "spray_budget_ratio", "has_sprayed", "wtdep"):
            self.assertNotIn(removed, names)
        self.assertEqual(len(set(names)), FRAME_SIZE)

    def test_layer_water_is_root_zone_thickness_weighted(self):
        env = self.make_env()
        obs, _ = env.reset(seed=1)
        index, scale = next((i, s) for i, (name, s) in enumerate(FIELDS) if name == "sw")
        self.assertAlmostEqual(float(obs[-FRAME_SIZE:][index]) * scale, 0.25, places=6)  # roots 50 cm reach both layers
        self.assertAlmostEqual(root_zone_water([0.1, 0.3], [10, 30], 20), (0.1 * 10 + 0.3 * 10) / 20)
        self.assertAlmostEqual(root_zone_water([0.1, 0.3], [10, 30], 0), 0.1)  # before rooting: top layer

    def test_preplant_is_automatic_and_uncharged(self):
        class Preplant(FakeBackend):
            def reset(self, seed):
                state = super().reset(seed)
                state["yrdoy"] -= 1
                return state
            def step(self, water, nitrogen):
                state, done, outcome = super().step(water, nitrogen)
                state["yrdoy"] = self.planting_yrdoy
                return state, done, outcome
        env = CropManagementEnv(pest_enabled=False, backend_factory=Preplant)
        self.addCleanup(env.close)
        _, info = env.reset(seed=1)
        self.assertEqual(info["preplant_days"], 1)
        self.assertEqual(env.day, 0)
        self.assertEqual(env.ledger.total_cost, 0)

    def test_pest_execution_is_rejected(self):
        with self.assertRaises(BackendContractError):
            CropManagementEnv(backend_factory=FakeBackend)
        with self.assertRaises(BackendContractError):
            DssatBackend(pest_enabled=True)


class TerminalContractTests(unittest.TestCase):
    def test_stage_six_alone_does_not_prove_crop_failure(self):
        with self.assertRaises(BackendContractError):
            classify_terminal({"istage": 6}, {"MDAT": 1982100, "HDAT": 1982100, "HWAH": 500}, "")

    def test_explicit_crop_failure_has_zero_revenue_yield(self):
        result = classify_terminal({"istage": 6}, {}, "Crop failure growth program terminated")
        self.assertEqual(result.reason, "crop_failure")
        self.assertEqual(result.harvested_grain_kg_ha, 0)

    def test_actual_harvest_comes_from_summary_not_previous_grain(self):
        result = classify_terminal({"istage": 10, "grnwt": 9999},
                                   {"MDAT": 1982100, "HDAT": 1982100, "HWAH": 2345}, "")
        self.assertEqual(result.harvested_grain_kg_ha, 2345)
        for grain in (-99, float("nan")):
            with self.assertRaises(BackendContractError):
                classify_terminal({"istage": 10}, {"MDAT": 1982100, "HDAT": 1982100, "HWAH": grain}, "")

    def test_terminal_template_rebuilds_state_from_current_callbacks(self):
        path = Path(__file__).parents[1] / "vendor/gym_dssat_pdi/gym-dssat-pdi/gym_dssat_pdi/envs/configs/maize/dssat_pdi.jinja2"
        original = path.read_text(encoding="utf-8")
        patched = terminal_template(original)
        self.assertIn("message = {'done': done, 'state': state}", patched)
        self.assertEqual(patched.count("state = {'yrdoy': yrdoy,"), 2)
        self.assertIn("message = {'done': done, 'state': {}}", original)

    def test_missing_or_multiple_summary_rows_are_rejected(self):
        with self.assertRaises(BackendContractError):
            read_summary("truncated output")
        with self.assertRaises(BackendContractError):
            read_summary("@ MDAT HDAT HWAH\n 1 1 3\n 2 2 4")


if __name__ == "__main__":
    unittest.main()
