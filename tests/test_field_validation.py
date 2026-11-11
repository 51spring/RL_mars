import copy
import hashlib
import json
from pathlib import Path
import unittest
from mars_env.field_validation import classify_nrmse, relative_yield_verdict, tier_gate_status, yield_agreement
ROOT = Path(__file__).resolve().parents[1]
TIERS = json.loads((ROOT / 'configs/field_validation_tiers.json').read_text(encoding='utf-8'))
CRITERION = TIERS['tiers']['A_undamaged_water_response']['criterion']
PRIMARY = TIERS['tiers']['A_undamaged_water_response']['primary']


class YieldAgreementTests(unittest.TestCase):
    def test_perfect_agreement(self):
        m = yield_agreement([1, 2, 4], [1, 2, 4])
        self.assertEqual(m['rmse'], 0)
        self.assertAlmostEqual(m['willmott_d'], 1)
        self.assertAlmostEqual(m['slope_simulated_on_observed'], 1)
        self.assertAlmostEqual(m['range_ratio'], 1)

    def test_known_values(self):
        m = yield_agreement([100, 200, 300], [110, 190, 250])
        self.assertAlmostEqual(m['bias'], -50 / 3)
        self.assertAlmostEqual(m['rmse'], (2700 / 3) ** .5)
        self.assertAlmostEqual(m['nrmse_pct'], 15.0)
        self.assertAlmostEqual(m['slope_simulated_on_observed'], .7)
        self.assertAlmostEqual(m['range_ratio'], .7)
        self.assertAlmostEqual(m['spearman_rho'], 1)

    def test_tied_ranks_and_bad_input(self):
        self.assertAlmostEqual(yield_agreement([1, 2, 2, 3], [1, 2, 2, 3])['spearman_rho'], 1)
        with self.assertRaises(ValueError):
            yield_agreement([1, 2], [1, 2])
        with self.assertRaises(ValueError):
            yield_agreement([1, 2, 3], [1, 2])
        with self.assertRaises(ValueError):
            yield_agreement([2, 2, 2], [1, 2, 3])


class TierGateTests(unittest.TestCase):
    def judgment(self, **changes):
        return {'passed': True, 'case_id': PRIMARY['id'], 'source_run_sha256': PRIMARY['source_run_sha256'],
                'criterion': copy.deepcopy(CRITERION), **changes}

    def test_classes_follow_frozen_thresholds(self):
        self.assertEqual(classify_nrmse(9.9, CRITERION)['class'], 'excellent')
        self.assertEqual(classify_nrmse(20.0, CRITERION)['class'], 'good')
        self.assertEqual(classify_nrmse(20.01, CRITERION)['class'], 'fair')
        result = classify_nrmse(30.01, CRITERION)
        self.assertEqual(result['class'], 'poor')
        self.assertFalse(result['passed'])
        self.assertIsNone(result['margin_to_next_worse_class_pct'])

    def test_tier_a_fails_closed(self):
        gate = TIERS['tiers']['A_undamaged_water_response']['gate']
        self.assertIn(gate, tier_gate_status(TIERS)['pending'])
        self.assertIn(gate, tier_gate_status(TIERS, self.judgment(passed=False))['pending'])
        self.assertIn(gate, tier_gate_status(TIERS, self.judgment(passed='true'))['pending'])
        self.assertIn(gate, tier_gate_status(TIERS, self.judgment(case_id='other'))['pending'])
        self.assertIn(gate, tier_gate_status(TIERS, self.judgment(source_run_sha256='0' * 64))['pending'])
        relaxed = copy.deepcopy(CRITERION)
        relaxed['pass_max_pct'] = 50.0
        self.assertIn(gate, tier_gate_status(TIERS, self.judgment(criterion=relaxed))['pending'])
        self.assertIn(gate, tier_gate_status(TIERS, self.judgment())['satisfied'])

    def test_tier_b_pending_and_tier_c_limitations(self):
        status = tier_gate_status(TIERS, self.judgment())
        self.assertIn('independent_agronomic_recovery', status['pending'])
        self.assertEqual(status['documented_limitations'],
                         ['calibrated_new_damage_survey', 'water_nitrogen_damage_interaction'])
        claimed = copy.deepcopy(TIERS)
        claimed['tiers']['B_damage_recovery_relative_yield']['status'] = 'passed'
        self.assertIn('independent_agronomic_recovery', tier_gate_status(claimed)['pending'])
        sha = TIERS['tiers']['B_damage_recovery_relative_yield']['criterion']['frozen_config_sha256']
        for damage in ({'passed': True, 'frozen_config_sha256': '0' * 64},
                       {'passed': False, 'frozen_config_sha256': sha}, {'passed': 'true', 'frozen_config_sha256': sha}):
            self.assertIn('independent_agronomic_recovery',
                          tier_gate_status(TIERS, self.judgment(), damage)['pending'])
        self.assertIn('independent_agronomic_recovery',
                      tier_gate_status(TIERS, self.judgment(), {'passed': True, 'frozen_config_sha256': sha})['satisfied'])


class DamageTierTests(unittest.TestCase):
    def setUp(self):
        self.path = ROOT / 'configs/damage_recovery_tier_b.json'
        self.frozen = json.loads(self.path.read_text(encoding='utf-8'))
        check = self.frozen['reference']['no_injury_check_yield']
        self.observed = {(c['stage'], c['defoliation_pct']): c['yield'] / check for c in self.frozen['reference']['cells']}

    def test_frozen_config_bytes_match_pinned_hash(self):
        pinned = TIERS['tiers']['B_damage_recovery_relative_yield']['criterion']
        self.assertEqual(hashlib.sha256(self.path.read_bytes()).hexdigest(), pinned['frozen_config_sha256'])
        self.assertEqual(self.frozen['status'], 'frozen_before_any_comparison')
        self.assertEqual(len(self.observed), 9)
        self.assertEqual(self.frozen['simulation']['runs'], 10 * len(self.frozen['simulation']['wgen_seeds']))
        self.assertTrue(all(1 <= seed <= 4999 for seed in self.frozen['simulation']['wgen_seeds']))

    def test_exact_reproduction_passes_and_observed_ratios(self):
        verdict = relative_yield_verdict(self.frozen, self.observed, 160)
        self.assertTrue(verdict['passed'])
        self.assertEqual(verdict['cells_outside_tolerance'], [])
        self.assertAlmostEqual(self.observed['R1', 99], 39.6 / 257.7)
        self.assertAlmostEqual(self.observed['V13', 99], 185.7 / 257.7)

    def test_fails_on_error_order_or_missing_runs(self):
        self.assertFalse(relative_yield_verdict(self.frozen, self.observed, 159)['passed'])
        flat = {key: 1.0 for key in self.observed}
        verdict = relative_yield_verdict(self.frozen, flat, 160)
        self.assertFalse(verdict['passed'])
        self.assertFalse(verdict['timing_order_at_99pct'])
        self.assertIn(['R1', 99], verdict['cells_outside_tolerance'])
        swapped = dict(self.observed)
        swapped['V8', 99], swapped['V13', 99] = .70, .72
        verdict = relative_yield_verdict(self.frozen, swapped, 160)
        self.assertLessEqual(verdict['rmse_ratio'], .10)
        self.assertFalse(verdict['passed'])
        with self.assertRaises(ValueError):
            relative_yield_verdict(self.frozen, {('V8', 33): 1.0}, 160)

    def test_config_keeps_scope_statements(self):
        self.assertTrue(TIERS['does_not_grant_research_readiness'])
        self.assertEqual(CRITERION['timing'], 'post_hoc_conventional')
        self.assertEqual(PRIMARY['fixed_inputs']['row_spacing_cm'], 75)


if __name__ == '__main__':
    unittest.main()
