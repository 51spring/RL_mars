from pathlib import Path
from dataclasses import replace
import sys
import unittest

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from mars_env.comparison import (contrasts, cross_bootstrap, holm, inference, lower_tail_mean, resource_violations,
                                 results_table, supply_variant, table_cells, training_plan)
from mars_env.exogenous import evaluation_conditions, generate_season
from mars_env.policies import CompositePolicy, FrozenChannels, ReductionResponseRule, RulePolicy, channel_mask
from mars_env.observations import FIELDS, FRAME_SIZE, OBSERVATION_SIZE
from mars_env.resources import ResourceLedger, ResourceRules, WaterShock


def config():
    return yaml.safe_load((Path(__file__).parents[1] / "configs/proposal_v2.yaml").read_text(encoding="utf-8"))


def observation(**values):
    latest = np.zeros(FRAME_SIZE)
    for index, (name, scale) in enumerate(FIELDS):
        latest[index] = values.get(name, 0) / scale
    return np.concatenate((np.zeros(OBSERVATION_SIZE - FRAME_SIZE), latest))


class CalendarReduction(unittest.TestCase):
    def test_applies_once_on_the_day_regardless_of_stage(self):
        ledger = ResourceLedger.create(shock=WaterShock.on_day(2, 0.5))
        for day, expected in ((0, 200), (1, 200), (2, 100), (3, 100)):
            ledger = ledger.open_day(day, 3)
            self.assertEqual(ledger.water_left, expected)
            ledger, _ = ledger.commit(ledger.rules.decode((0, 0, 0)))
        self.assertEqual((ledger.announcement_day, ledger.water_cut_mm), (2, 100))

    def test_stage_option_is_kept(self):
        ledger = ResourceLedger.create(shock=WaterShock(1, 2, 0.5)).open_day(0, 1)
        ledger, _ = ledger.commit(ledger.rules.decode((0, 0, 0)))
        self.assertEqual(ledger.open_day(1, 1).water_left, 200)

    def test_invalid_shocks(self):
        for args in ((1, 0, 0.5, "remaining_fraction", 3), (None, 1, 0.5, "remaining_fraction", 3), (None, 0, 0.5)):
            with self.assertRaises(ValueError):
                WaterShock(*args)


class Sampling(unittest.TestCase):
    def test_training_day_window_and_zero_probability(self):
        c = config()
        low, high = c["scenarios"]["training_day_range_inclusive"]
        seasons = [generate_season(c, split="train", season_id=i) for i in range(300)]
        cut = [s.shock for s in seasons if s.shock is not None]
        self.assertTrue(0.65 < len(cut) / 300 < 0.85)
        self.assertTrue(all(low <= s.day <= high and s.stage is None for s in cut))
        self.assertFalse(any(generate_season(c, split="train", season_id=i, reduction_probability=0).shock for i in range(50)))

    def test_probability_override_keeps_the_exogenous_tapes(self):
        c = config()
        a, b = (generate_season(c, split="train", season_id=7, reduction_probability=p) for p in (0, None))
        self.assertEqual(a.paired_digest(), b.paired_digest())
        self.assertEqual(a.beta, b.beta)

    def test_ten_conditions(self):
        conditions = evaluation_conditions(config())
        self.assertEqual(len(conditions), 10)
        self.assertIsNone(conditions.pop("none"))
        self.assertEqual(len({(s.day, s.fraction) for s in conditions.values()}), 9)


class Plan(unittest.TestCase):
    def test_chains_stay_within_regime_and_seed(self):
        plan = {fit.label: fit for fit in training_plan(config(), steps=256, seeds=[3, 5])}
        self.assertEqual(len(plan), 16)
        self.assertEqual(plan["b2_s5"].frozen, (("b1_s5", (0,)),))
        self.assertEqual(plan["a3_s3"].frozen, (("a1_s3", (0,)), ("a2_s3", (1,))))
        self.assertEqual(plan["a4_s3"].steps, 768)
        self.assertEqual(plan["b4_s3"].learn, (0, 1, 2))
        self.assertEqual(plan["a1_s3"].reduction_probability, 0.0)
        self.assertIsNone(plan["b1_s3"].reduction_probability)

    def test_table_cells(self):
        cells = table_cells(evaluation_conditions(config()))
        self.assertEqual(len({c[:2] for c in cells}), 20)
        self.assertEqual(len({c[2] for c in cells}), 10)
        self.assertEqual({c[2] for c in cells if c[0] == "a_cut"}, {"a1", "a2", "a3", "a4"})
        self.assertEqual(sum(c[:2] == ("a_cut", "2") for c in cells), 9)
        self.assertEqual({c[0] for c in cells if c[1] == "b0p"}, {"b_cut"})
        self.assertEqual(sum(c[:2] == ("b_cut", "2") for c in cells), 9)

    def test_sensitivity_rows_drop_only_a_cut(self):
        scenario = config()["scenarios"]
        conditions = evaluation_conditions(config())
        full = table_cells(conditions)
        reduced = table_cells(conditions, tuple(scenario["sensitivity_rows"]))
        self.assertEqual(reduced, [c for c in full if c[0] != "a_cut"])
        self.assertEqual(len(full) - len(reduced), 36)
        self.assertEqual((scenario["sensitivity_seasons_per_condition"], scenario["evaluation_workers"]), (300, 8))
        with self.assertRaises(ValueError):
            table_cells(conditions, ("a", "unknown"))


class Sensitivity(unittest.TestCase):
    def test_supply_variant_moves_the_budget_and_leaves_the_base(self):
        base = config()
        variant = supply_variant(base, 120)
        rules = ResourceRules.from_config(variant)
        self.assertEqual(rules.initial_water, 120.0)
        self.assertEqual(ResourceLedger.create(rules).water_left, 120.0)
        self.assertEqual(base["environment"]["initial_water_mm"], 200.0)

    def test_survey_noise_variant_changes_only_the_noise(self):
        from mars_env.comparison import survey_noise_variant
        from mars_env.pests import pest_settings
        base = config()
        variant = survey_noise_variant(base, 0.05)
        self.assertEqual(pest_settings(variant)[1], 0.05)
        self.assertEqual(pest_settings(variant)[0], pest_settings(base)[0])
        self.assertEqual(base["pest"]["survey_noise_std"], 0.01)
        self.assertEqual(base["scenarios"]["evaluation_survey_noise_std"], [0.05])


class Statistics(unittest.TestCase):
    def returns(self):
        conditions = evaluation_conditions(config())
        rng, out = np.random.default_rng(1), {}
        for row, column, _, condition in table_cells(conditions):
            out[row, column, condition] = rng.normal(500, 5, (4, 30))
        out["b_none", "0", "none"] = out["a", "0", "none"].copy()
        return out

    def test_resource_violations_recount(self):
        rules = ResourceRules()
        fine = {"water_mm": 100, "nitrogen_kg_ha": 116, "sprays": 3}
        self.assertEqual(resource_violations(fine, 0, rules, 1.0), 0)
        self.assertEqual(resource_violations(fine, 200, rules, 1.0), 1)
        self.assertEqual(resource_violations({**fine, "nitrogen_kg_ha": 242, "sprays": 4}, 0, rules, 1.0), 2)

    def test_lower_tail(self):
        self.assertEqual(lower_tail_mean(range(1, 21)), 1.5)

    def test_holm(self):
        adjusted = holm({"a": 0.01, "b": 0.04, "c": 0.03})
        self.assertEqual(adjusted, {"a": 0.03, "c": 0.06, "b": 0.06})

    def test_table_and_contrasts(self):
        data = self.returns()
        table = results_table(data)
        self.assertEqual(len(table), 20)
        self.assertEqual(len(table["b_cut", "1"]["conditions"]), 9)
        c = config()["scenarios"]
        result = contrasts(data, list(c["evaluation_days"]), c["evaluation_reductions"])
        self.assertAlmostEqual(result["readiness_cost_2"][1].mean(),
                               data["a", "2", "none"].mean() - data["b_none", "2", "none"].mean())
        expected = data["b_cut", "1", "early_40"] - data["b_cut", "b0p", "early_40"]
        self.assertEqual(result["rule_response"][0], "effects")
        self.assertEqual(expected.shape, result["rule_response"][1].shape)
        self.assertEqual(len([v for v in result.values() if v[0] == "conditions"]), 9)
        self.assertEqual(len(result), 4 + 5 + 5 + 9 + 2 + 4)
        self.assertAlmostEqual(result["preparedness_gain_3"][1].mean(), np.mean(
            [data["b_cut", "3", c].mean() - data["a_cut", "3", c].mean() for c in evaluation_conditions(config()) if c != "none"]))

    def test_contrasts_without_a_cut_skip_only_preparedness(self):
        data = {key: value for key, value in self.returns().items() if key[0] != "a_cut"}
        c = config()["scenarios"]
        result = contrasts(data, list(c["evaluation_days"]), c["evaluation_reductions"])
        self.assertEqual(len(result), 4 + 5 + 5 + 9 + 2)
        self.assertFalse(any(name.startswith("preparedness_gain") for name in result))
        self.assertEqual(len(results_table(data)), 16)

    def test_bootstrap_detects_a_shift_and_centres_a_null(self):
        rng = np.random.default_rng(0)
        report = inference({"shift": ("f", rng.normal(30, 5, (10, 200)), "greater"),
                            "null": ("f", rng.normal(0, 5, (10, 200)), "two-sided")}, replicates=2000)
        self.assertLess(report["shift"]["p_holm"], 0.01)
        self.assertGreater(report["null"]["p_holm"], 0.05)
        self.assertLess(report["shift"]["ci95"][0], report["shift"]["estimate_usd_ha"])

    def test_bootstrap_preserves_the_row_structure(self):
        matrix = np.tile(np.array([[0.0], [10.0]]), (1, 50))
        draws = cross_bootstrap({"x": matrix}, replicates=2000)["x"]
        self.assertTrue(set(np.unique(draws)) <= {0.0, 5.0, 10.0})


class Policies(unittest.TestCase):
    rules = ResourceRules()

    def rule(self, reserve):
        return ReductionResponseRule(reserve_mm=reserve, flowering_day=60, maturity_day=120, event_interval_days=10)

    def water(self, policy, **values):
        return self.rules.water_grid[policy.action(observation(**values), np.ones(17, bool), self.rules)[0]]

    def test_matches_the_rule_before_any_reduction(self):
        self.assertEqual(self.water(self.rule(100), swfac=1, water_left=264, istage=2, dap=30), 10)

    def test_keeps_the_reserve_before_flowering(self):
        self.assertEqual(self.water(self.rule(100), announced=1, swfac=1, water_left=90, istage=2, dap=30), 0)

    def test_spends_only_above_the_reserve_before_flowering(self):
        self.assertEqual(self.water(self.rule(100), announced=1, swfac=1, water_left=112, istage=2, dap=45), 5)

    def test_reserve_opens_at_flowering_and_is_paced(self):
        self.assertEqual(self.water(self.rule(100), announced=1, swfac=1, water_left=90, istage=4, dap=70), 10)
        self.assertEqual(self.water(self.rule(100), announced=1, swfac=1, water_left=45, istage=4, dap=70), 5)

    def test_reserve_applies_only_below_remaining_demand(self):
        scarce = ReductionResponseRule(reserve_mm=100, flowering_day=60, maturity_day=120, event_interval_days=10,
                                       remaining_demand_mm=((0, 130), (42, 130), (130, 0)))
        self.assertEqual(self.water(scarce, announced=1, swfac=1, water_left=140, istage=2, dap=30), 10)
        self.assertEqual(self.water(scarce, announced=1, swfac=1, water_left=90, istage=2, dap=30), 0)
        self.assertEqual(self.water(scarce, announced=1, swfac=1, water_left=70, istage=3, dap=86), 10)

    def test_demand_margin_lowers_the_scarcity_threshold(self):
        strict = ReductionResponseRule(reserve_mm=110, flowering_day=60, maturity_day=120, event_interval_days=10,
                                       remaining_demand_mm=((0, 130), (130, 0)))
        relaxed = replace(strict, demand_margin=0.8)
        state = dict(announced=1, swfac=1, water_left=110, istage=2, dap=0)
        self.assertEqual(self.water(strict, **state), 0)
        self.assertEqual(self.water(relaxed, **state), 10)

    def test_stage_water_overrides_only_listed_stages(self):
        rule = RulePolicy(stage_water=((4, 0.1, 20),))
        self.assertEqual(self.water(rule, swfac=0.2, istage=4, dap=85), 20)
        self.assertEqual(self.water(rule, swfac=0.05, istage=4, dap=85), 0)
        self.assertEqual(self.water(rule, swfac=0.2, istage=3, dap=60), 0)
        self.assertEqual(self.water(rule, swfac=0.4, istage=3, dap=60), 10)

    def test_invalid_stage_water(self):
        with self.assertRaises(ValueError):
            RulePolicy(stage_water=((4, 1.5, 10),))

    def test_no_stress_no_water(self):
        self.assertEqual(self.water(self.rule(0), announced=1, swfac=0, water_left=200, istage=4, dap=70), 0)

    def test_frozen_channels_override_only_their_channels(self):
        seen = {}

        class Model:
            def predict(self, obs, deterministic, action_masks):
                seen["mask"], seen["deterministic"] = action_masks, deterministic
                return np.array(2), None

        policy = CompositePolicy(RulePolicy(baseline_nitrogen=((10, 27),)), (FrozenChannels(Model(), (1,)),))
        action = policy.action(observation(dap=10, swfac=1), np.ones(17, bool), self.rules)
        self.assertEqual(action.tolist(), [2, 2, 0])
        self.assertEqual(seen["mask"].shape, (9,))
        self.assertTrue(seen["deterministic"])
        self.assertEqual(channel_mask(np.ones(17, bool), (0, 2)).shape, (8,))


if __name__ == "__main__":
    unittest.main()
