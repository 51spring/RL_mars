"""Research-critical inventory, announcement timing, and feasibility regressions."""
from dataclasses import replace
from itertools import product
from pathlib import Path
import unittest

import numpy as np
import yaml

from mars_env.resources import Action, ResourceLedger, ResourceRules, WaterShock


class ResourceTests(unittest.TestCase):
    def test_proposal_config_and_beta(self):
        config = yaml.safe_load((Path(__file__).parents[1] / "configs/proposal_v2.yaml").read_text(encoding="utf-8"))
        rules = ResourceRules.from_config(config)
        for beta in (0.6, 1, 1.4):
            ledger = ResourceLedger.create(rules, beta)
            self.assertEqual(ledger.water_left, 200)  # water is limited by the supply, not by beta
            self.assertAlmostEqual(ledger.nitrogen_budget_left, 190.39 * beta)
            self.assertAlmostEqual(ledger.spray_budget_left, 150 * beta)

    def test_baseline_nitrogen_leaves_one_maximum_application(self):
        ledger = ResourceLedger.create()
        for day, amount in ((45, 80), (65, 54), (95, 27)):
            ledger, _ = ledger.open_day(day, 2).commit(Action(nitrogen_kg_ha=amount))
        self.assertEqual(ledger.nitrogen_used, 161)
        self.assertAlmostEqual(ledger.nitrogen_budget_left, 63.2)
        self.assertAlmostEqual(ledger.total_cost, 127.19 + 15)
        self.assertTrue(ledger.open_day(96, 2).action_masks()[7:15].all())
        ledger, _ = ledger.open_day(96, 2).commit(Action(nitrogen_kg_ha=80))
        self.assertFalse(ledger.open_day(97, 2).action_masks()[7:15].any())

    def test_water_remainder_below_smallest_grid_step_is_masked(self):
        ledger = ResourceLedger.create(ResourceRules(initial_water=264))
        for day in range(10):
            ledger, _ = ledger.open_day(day, 1).commit(Action(25))
        ledger, _ = ledger.open_day(10, 1).commit(Action(10))
        self.assertEqual(ledger.water_used, 260)
        self.assertEqual(ledger.water_left, 4)
        self.assertEqual(ledger.open_day(11, 1).action_masks()[:6].tolist(),
                         [True, False, False, False, False, False])

    def test_total_entitlement_cut_after_prior_usage_can_reach_zero(self):
        ledger = ResourceLedger.create(shock=WaterShock(2, 0, 0.9, "total_entitlement"))
        for day in range(2):
            ledger, _ = ledger.open_day(day, 1).commit(Action(25))
        ledger = ledger.open_day(2, 2)
        self.assertEqual(ledger.water_left, 0)
        self.assertEqual(ledger.water_used, 50)

    def test_cost_no_double_counting_and_labor_outside_budgets(self):
        initial = ResourceLedger.create().open_day(0, 1)
        ledger, cost = initial.commit(Action(10, 27, 1))
        self.assertAlmostEqual(cost.total, 11 + 21.33 + 50 + 3 + 5)
        self.assertAlmostEqual(ledger.nitrogen_budget_left, 169.06)
        self.assertEqual(ledger.spray_budget_left, 100)
        self.assertEqual(ledger.water_left, 190)
        self.assertEqual(initial.total_cost, 0)

    def test_remaining_water_cut_announced_before_action_only_once(self):
        ledger = ResourceLedger.create(shock=WaterShock(1, 2, 0.5))
        ledger, _ = ledger.open_day(0, 1).commit(Action(20))
        self.assertEqual(ledger.announcement(), {"announced": False, "fraction": 0.0, "days_since": 0})
        ledger, _ = ledger.open_day(1, 2).commit(Action(10))
        before = ledger
        ledger = ledger.open_day(2, 2)
        self.assertEqual(ledger.water_left, 85)
        self.assertEqual(ledger.announcement(), {"announced": True, "fraction": 0.5, "days_since": 0})
        self.assertEqual(ledger.total_cost, before.total_cost)
        self.assertEqual(ledger.water_used, 30)
        ledger, _ = ledger.commit(Action())
        ledger = ledger.open_day(3, 1)
        self.assertEqual(ledger.water_left, 85)
        self.assertEqual(ledger.announcement()["days_since"], 1)

    def test_total_entitlement_contract_is_distinct(self):
        ledger = ResourceLedger.create(shock=WaterShock(2, 0, 0.5, "total_entitlement"))
        ledger, _ = ledger.open_day(0, 1).commit(Action(20))
        ledger = ledger.open_day(1, 2)
        self.assertEqual(ledger.water_left, 80)
        self.assertEqual(ledger.water_used, 20)

    def test_full_cut_masks_all_water_and_preserves_noop(self):
        ledger = ResourceLedger.create(shock=WaterShock(1, 0, 1)).open_day(0, 1)
        self.assertEqual(ledger.water_left, 0)
        self.assertEqual(ledger.action_masks()[:6].tolist(), [True, False, False, False, False, False])
        ledger.validate(Action())

    def test_supply_is_the_only_water_limit(self):
        ledger = ResourceLedger.create(beta=0).open_day(0, 1)
        self.assertTrue(ledger.action_masks()[:6].all())  # beta scales money budgets only
        by_volume = replace(ledger, water_left=5)
        by_volume.validate(Action(5))
        with self.assertRaises(ValueError):
            by_volume.validate(Action(10))
        config = yaml.safe_load((Path(__file__).parents[1] / "configs/proposal_v2.yaml").read_text(encoding="utf-8"))
        config["economics"]["budgets_usd_ha"]["water"] = 220.0
        with self.assertRaises(ValueError):
            ResourceRules.from_config(config)

    def test_irrigation_and_nitrogen_close_at_maturity(self):
        ledger = ResourceLedger.create().open_day(0, 6)
        mask = ledger.action_masks()
        self.assertEqual(mask[:6].tolist(), [True] + [False] * 5)
        self.assertEqual(mask[6:15].tolist(), [True] + [False] * 8)
        for action in (Action(5), Action(nitrogen_kg_ha=10)):
            with self.assertRaises(ValueError):
                ledger.validate(action)
        ledger.validate(Action())
        for stage in (1, 5, 7, 9):
            self.assertTrue(ResourceLedger.create().open_day(0, stage).action_masks()[:15].all())

    def test_spray_first_application_interval_stage_and_budget(self):
        ledger = ResourceLedger.create(beta=1.4).open_day(0, 1)
        self.assertTrue(ledger.action_masks()[-1])
        ledger, _ = ledger.commit(Action(spray=1))
        self.assertFalse(ledger.open_day(6, 1).action_masks()[-1])
        self.assertTrue(ledger.open_day(7, 1).action_masks()[-1])
        self.assertFalse(ledger.open_day(7, 5).action_masks()[-1])
        for day in (7, 14, 21):
            ledger, _ = ledger.open_day(day, 1).commit(Action(spray=1))
        self.assertEqual(ledger.sprays, 4)
        self.assertEqual(ledger.spray_budget_left, 10)
        # No count cap: only the remaining budget blocks a fifth spray.
        self.assertFalse(ledger.open_day(28, 1).action_masks()[-1])
        funded = replace(ledger, spray_budget_left=1000).open_day(28, 1)
        self.assertTrue(funded.action_masks()[-1])

    def test_beta_one_allows_only_three_sprays(self):
        ledger = ResourceLedger.create()
        for day in (0, 7, 14):
            ledger, _ = ledger.open_day(day, 1).commit(Action(spray=1))
        self.assertEqual(ledger.sprays, 3)
        self.assertFalse(ledger.open_day(21, 1).action_masks()[-1])

    def test_invalid_action_does_not_change_ledger(self):
        ledger = ResourceLedger.create(beta=0).open_day(0, 1)
        before = repr(ledger)
        for action in (Action(1), Action(nitrogen_kg_ha=10), Action(spray=1), Action(spray=0.5)):
            with self.assertRaises(ValueError):
                ledger.commit(action)
            self.assertEqual(repr(ledger), before)
        ledger.validate(Action())

    def test_no_double_commit_or_skipped_commit(self):
        ledger = ResourceLedger.create()
        with self.assertRaises(ValueError):
            ledger.commit(Action())
        ready = ledger.open_day(0, 1)
        with self.assertRaises(ValueError):
            ready.open_day(1, 1)
        done, _ = ready.commit(Action())
        with self.assertRaises(ValueError):
            done.commit(Action())
        with self.assertRaises(ValueError):
            done.open_day(0, 1)

    def test_decode_rejects_malformed_indices(self):
        rules = ResourceRules()
        self.assertEqual(rules.decode(np.array([2, 3, 1])), Action(10, 27, 1))
        for indices in ((-1, 0, 0), (6, 0, 0), (0, 9, 0), (0, 0, 2),
                        (1.0, 0, 0), (True, 0, 0), (0, 0), 3):
            with self.assertRaises(ValueError):
                rules.decode(indices)

    def test_invalid_rules_and_scenarios(self):
        for kwargs in ({"water_price": float("nan")}, {"water_grid": (5, 10)},
                       {"nitrogen_grid": (0, 10, 10)}, {"spray_interval": -1}):
            with self.assertRaises(ValueError):
                ResourceRules(**kwargs)
        for args in ((3, 0, 0.5), (1, -1, 0.5), (1, 0, 1.1), (1, 0, float("nan"))):
            with self.assertRaises(ValueError):
                WaterShock(*args)

    def test_all_108_actions_mask_matches_feasibility(self):
        ledger = ResourceLedger.create(beta=0.6).open_day(0, 2)
        ledger = replace(ledger, water_left=12, nitrogen_budget_left=22)
        masks = ledger.action_masks()
        self.assertEqual(masks.shape, (17,))
        for indices in product(range(6), range(9), range(2)):
            action = ledger.rules.decode(indices)
            expected = all(masks[offset + i] for offset, i in zip((0, 6, 15), indices))
            if expected:
                ledger.validate(action)
            else:
                with self.assertRaises(ValueError):
                    ledger.validate(action)

    def test_random_seasons_never_overspend_and_always_allow_noop(self):
        rng = np.random.default_rng(20261105)
        for season in range(100):
            beta = float(rng.choice([0.6, 1, 1.4]))
            shock = WaterShock(1, int(rng.integers(0, 6)), float(rng.uniform(0.1, 0.7)))
            ledger = ResourceLedger.create(beta=beta, shock=shock)
            for day in range(120):
                stage = 1 if day < 30 else 4 if day < 80 else 5
                ledger = ledger.open_day(day, stage)
                mask = ledger.action_masks()
                self.assertTrue(all(mask[i] for i in (0, 6, 15)))
                indices = [rng.choice(np.flatnonzero(group)) for group in np.split(mask, (6, 15))]
                ledger, _ = ledger.commit(ledger.rules.decode(indices))
                self.assertTrue(all(x >= 0 for x in (ledger.water_left, ledger.nitrogen_budget_left,
                                                     ledger.spray_budget_left)))
                self.assertLessEqual(ledger.water_used, 200 + 1e-8)
                self.assertLessEqual(ledger.nitrogen_used * 0.79, 190.39 * beta + 1e-8)
                self.assertLessEqual(ledger.sprays * 50, 150 * beta + 1e-8)
                self.assertLessEqual(ledger.sprays, 4)


if __name__ == "__main__":
    unittest.main()
