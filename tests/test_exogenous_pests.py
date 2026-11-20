from copy import deepcopy
from dataclasses import replace
from pathlib import Path
import unittest

import numpy as np
import yaml

from mars_env.exogenous import WEATHER_SEED_VERSION, allocate_weather_seed, generate_season, stream
from mars_env.pests import DamageSurvey, PestParameters, PestState
from mars_env.resources import WaterShock


def config():
    return yaml.safe_load((Path(__file__).parents[1] / "configs/proposal_v2.yaml").read_text(encoding="utf-8"))


class ExogenousTests(unittest.TestCase):
    def test_same_season_reproducible_and_readonly(self):
        a = generate_season(config(), split="test", season_id=11)
        b = generate_season(config(), split="test", season_id=11)
        self.assertEqual(a.manifest(), b.manifest())
        np.testing.assert_array_equal(a.pest_arrivals, b.pest_arrivals)
        with self.assertRaises(ValueError):
            a.pest_arrivals[0] = 1

    def test_splits_and_season_columns_are_separate(self):
        hashes = {generate_season(config(), split=split, season_id=i).paired_digest()
                  for split in ("train", "validation", "test") for i in range(4)}
        self.assertEqual(len(hashes), 12)

    def test_wgen_partitions_are_exhaustive_and_never_wrap(self):
        roots = config()["reproducibility"]["split_seeds"]
        allocated = set()
        for split, lo, hi in (("train", 10001, 99998), ("validation", 1, 4999), ("test", 5000, 9999)):
            size = hi - lo + 1
            values = {allocate_weather_seed(split, roots[split], i) for i in range(size)}
            self.assertEqual(values, set(range(lo, hi + 1)))
            self.assertTrue(allocated.isdisjoint(values))
            allocated.update(values)
            with self.assertRaisesRegex(ValueError, "unique seasons"):
                generate_season(config(), split=split, season_id=size)

    def test_allocated_wgen_seed_is_reported_and_checked(self):
        season = generate_season(config(), split="test", season_id=0)
        self.assertEqual(season.manifest()["weather_seed_version"], WEATHER_SEED_VERSION)
        self.assertEqual(season.manifest()["wgen_seed"], season.backend_seed)
        self.assertEqual(season.with_condition(beta=0.6, shock=None).wgen_seed, season.wgen_seed)
        with self.assertRaisesRegex(ValueError, "does not match"):
            replace(season, backend_seed=10001)

    def test_policy_condition_changes_do_not_change_external_tapes(self):
        base = generate_season(config(), split="test", season_id=10)
        for beta in (0.6, 1, 1.4):
            for rate in (0.2, 0.4, 0.6):
                paired = base.with_condition(beta=beta, shock=WaterShock(2, 3, rate))
                self.assertEqual(paired.paired_digest(), base.paired_digest())
                self.assertEqual(paired.backend_seed, base.backend_seed)

    def test_change_in_one_sampling_distribution_leaves_others_unchanged(self):
        c1, c2 = config(), config()
        c2["pest"]["arrival_probability"] = 1
        c2["economics"]["budget_multipliers"] = [2]
        a = generate_season(c1, split="train", season_id=5)
        b = generate_season(c2, split="train", season_id=5)
        self.assertEqual(a.backend_seed, b.backend_seed)
        self.assertEqual(a.shock, b.shock)
        np.testing.assert_array_equal(a.survey_standard_noise, b.survey_standard_noise)
        self.assertTrue(np.all(b.pest_arrivals == 0.05))

    def test_longer_horizon_preserves_all_existing_dates(self):
        a = generate_season(config(), split="test", season_id=0, horizon=50)
        b = generate_season(config(), split="test", season_id=0, horizon=400)
        np.testing.assert_array_equal(a.pest_arrivals, b.pest_arrivals[:50])
        np.testing.assert_array_equal(a.survey_standard_noise, b.survey_standard_noise[:50])
        self.assertEqual(a.shock, b.shock)
        self.assertEqual(a.beta, b.beta)

    def test_invalid_sampling_keys_and_overlapping_split_seeds(self):
        with self.assertRaises(ValueError):
            stream(1, 0, "new-name-without-id")
        with self.assertRaises(ValueError):
            generate_season(config(), split="test", season_id=-1)
        c = config()
        c["reproducibility"]["split_seeds"]["test"] = c["reproducibility"]["split_seeds"]["train"]
        with self.assertRaises(ValueError):
            generate_season(c, split="test", season_id=0)


class PestTests(unittest.TestCase):
    def test_unset_calibration_parameters_are_rejected(self):
        unset = config()
        unset["pest"].update(temperature_low_c=None, temperature_high_c=None, survey_noise_std=None)
        with self.assertRaises(ValueError):
            PestParameters.from_config(unset)
        with self.assertRaises(ValueError):
            DamageSurvey.from_config(unset)

    def test_configured_settings_match_the_literature_anchors(self):
        from mars_env.pests import pest_settings
        parameters, noise = pest_settings(config())
        # Du Plessis 2020 egg-to-adult lower threshold 12.57 C, Adan 2024 rm peak (decision_project.md 28).
        self.assertEqual(parameters, PestParameters(12.57, 28, growth_low=0.0, growth_high=0.211,
                                                    alpha=config()["pest"]["alpha"]))
        self.assertAlmostEqual(parameters.growth(12.57), 0.0)
        self.assertAlmostEqual(parameters.growth(28), 0.211)
        self.assertAlmostEqual(parameters.growth(35), 0.211)
        self.assertEqual(noise, 0.01)
        changed = config()
        changed["management"]["survey_interval_days"] = 5
        with self.assertRaises(ValueError):
            pest_settings(changed)

    def params(self, **kwargs):
        # Explicit test-only temperature anchors, not calibrated biological values.
        return PestParameters(temperature_low_c=10, temperature_high_c=30, **kwargs)

    def test_daily_formula_and_same_day_spray(self):
        params = self.params()
        state = PestState(density=0.5)
        untreated, loss, effect = state.advance(0, 20, 0.05, False, params)
        treated, treated_loss, treated_effect = state.advance(0, 20, 0.05, True, params)
        expected = 0.5 + 0.1 * 0.5 * 0.5 + 0.05
        self.assertAlmostEqual(untreated.density, expected)
        self.assertAlmostEqual(loss, expected * 0.03)
        self.assertEqual(effect, 0)
        self.assertAlmostEqual(treated.density, expected * 0.2)
        self.assertAlmostEqual(treated_effect, 0.8)
        self.assertLess(treated_loss, loss)

    def test_residual_resets_instead_of_accumulating(self):
        params = self.params()
        state, _, _ = PestState().advance(0, 20, 0.05, True, params)
        state, _, residual = state.advance(1, 20, 0, False, params)
        self.assertAlmostEqual(residual, 0.8 * np.exp(-1 / 5))
        _, _, reset = state.advance(2, 20, 0, True, params)
        self.assertEqual(reset, 0.8)

    def test_zero_alpha_zero_damage_and_no_stage_suppression(self):
        _, damage, _ = PestState(density=0.5).advance(0, 20, 0, False, self.params(alpha=0))
        self.assertEqual(damage, 0)
        _, early_damage, _ = PestState(density=0.5).advance(0, 20, 0, False, self.params())
        self.assertGreater(early_damage, 0)  # No V7/stage multiplier exists in physical damage.

    def test_action_histories_share_future_arrivals_and_noise(self):
        season = generate_season(config(), split="test", season_id=0)
        untreated, treated = PestState(), PestState()
        for day in range(40):
            untreated, _, _ = untreated.advance(day, 20, float(season.pest_arrivals[day]), False, self.params())
            treated, _, _ = treated.advance(day, 20, float(season.pest_arrivals[day]), day % 7 == 0, self.params())
        self.assertLessEqual(treated.density, untreated.density)
        self.assertEqual(season.paired_digest(), generate_season(config(), split="test", season_id=0).paired_digest())

    def test_density_bounds_and_invalid_chronology(self):
        state, loss, _ = PestState(density=1).advance(0, 100, 100, False, self.params())
        self.assertEqual(state.density, 1)
        self.assertEqual(loss, 0.03)
        with self.assertRaises(ValueError):
            state.advance(0, 20, 0, False, self.params())


class SurveyTests(unittest.TestCase):
    def test_partial_history_uses_existing_days_only(self):
        survey = DamageSurvey(alpha=0.03, noise_std=0, interval_days=1)
        survey = survey.morning(0, 0)
        self.assertEqual(survey.observation()["survey_value"], 0)
        survey = survey.complete_day(0, 0.015).morning(1, 0)
        self.assertAlmostEqual(survey.observation()["survey_value"], 0.5)
        survey = survey.complete_day(1, 0.03).morning(2, 0)
        self.assertAlmostEqual(survey.observation()["survey_value"], 0.75)

    def test_seven_day_mean_not_cumulative_loss_and_held_between_surveys(self):
        survey = DamageSurvey(alpha=0.03, noise_std=0).morning(0, 0)
        for day in range(7):
            survey = survey.complete_day(day, 0.015).morning(day + 1, 0)
        self.assertAlmostEqual(survey.observation()["survey_value"], 0.5)
        survey = survey.complete_day(7, 0).morning(8, 5)
        self.assertAlmostEqual(survey.observation()["survey_value"], 0.5)
        self.assertEqual(survey.observation()["survey_age"], 1)

    def test_old_damage_ages_out_and_zero_alpha_has_zero_pre_noise_proxy(self):
        survey = DamageSurvey(alpha=0.03, noise_std=0, interval_days=1).morning(0, 0)
        for day in range(8):
            survey = survey.complete_day(day, 0.03 if day == 0 else 0).morning(day + 1, 0)
        self.assertEqual(survey.observation()["survey_value"], 0)
        zero_alpha = DamageSurvey(alpha=0, noise_std=0.1).morning(0, 1)
        self.assertAlmostEqual(zero_alpha.observation()["survey_value"], 0.1)

    def test_noise_clipped_and_future_or_duplicate_day_rejected(self):
        survey = DamageSurvey(alpha=0.03, noise_std=0.1).morning(0, 100)
        self.assertEqual(survey.observation()["survey_value"], 1)
        with self.assertRaises(ValueError):
            survey.morning(1, 0)
        completed = survey.complete_day(0, 0)
        with self.assertRaises(ValueError):
            completed.complete_day(0, 0)


if __name__ == "__main__":
    unittest.main()
