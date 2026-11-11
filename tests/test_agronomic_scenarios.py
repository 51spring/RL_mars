import copy
from pathlib import Path
import unittest
from mars_env.agronomic_scenarios import (build_registry,readiness,source_contrasts,
                                        descriptive_prediction_comparison,require_calibration_role)
ROOT=Path(__file__).resolve().parents[1]


class AgronomicScenarioTests(unittest.TestCase):
    def rows(self):return build_registry(ROOT)

    def test_study_cells_and_matched_controls_do_not_promote_readiness(self):
        rows=self.rows();self.assertEqual(len(rows),28)
        self.assertEqual(len({r['scenario_id'] for r in rows}),28)
        self.assertEqual(len(source_contrasts(rows)),16)
        self.assertFalse(any(readiness(r)['ready_for_quantitative_validation'] for r in rows))

    def test_early_cut_and_basal_n_are_not_replaced_by_uniform_leaf_loss_or_zero_n(self):
        rows=self.rows();pots=[r for r in rows if r['study_id']=='oliveira2026']
        self.assertEqual(sorted({r['factors']['total_n_kg_ha_equivalent'] for r in pots}),[40,120])
        self.assertEqual({r['damage_kind'] for r in pots if not r['is_control']},{'shoot_cut_5cm'})
        self.assertFalse(any(r['readiness']['damage_mapping'] for r in pots if not r['is_control']))

    def test_ear_endpoint_and_pot_units_cannot_be_silently_compared_to_native_grain(self):
        rows=self.rows();ear=next(r for r in rows if r['study_id']=='santos2018')
        pred={'endpoint':'oven_dry_grain_yield','unit':'kg/ha','value':10000}
        with self.assertRaises(ValueError):descriptive_prediction_comparison(ear,pred)
        pot=next(r for r in rows if r['study_id']=='oliveira2026')
        with self.assertRaises(ValueError):descriptive_prediction_comparison(pot,dict(pred,endpoint=pot['endpoint']))

    def test_mass_units_convert_but_do_not_imply_statistical_pass(self):
        s=next(r for r in self.rows() if r['scenario_id']=='oveysi2010_W1_D1')
        r=descriptive_prediction_comparison(s,{'endpoint':s['endpoint'],'unit':'kg/ha','value':10500})
        self.assertEqual(r['difference_kg_ha'],0)
        self.assertIsNone(r['statistical_validation_passed']);self.assertFalse(r['research_ready'])

    def test_independent_study_stays_out_of_calibration_even_with_ready_fields(self):
        s=next(r for r in self.rows() if r['study_id']=='oveysi2010')
        s['readiness']={k:True for k in s['readiness']};s['observed_standard_error']=.2
        with self.assertRaises(ValueError):require_calibration_role(s)
        for bad in (None,-.2,float('nan')):
            s['observed_standard_error']=bad
            self.assertFalse(readiness(s)['ready_for_quantitative_validation'])
        s['registered_acceptance_rule']={}
        self.assertFalse(readiness(s)['ready_for_quantitative_validation'])

    def test_response_direction_and_unknown_uncertainty_are_preserved(self):
        comparisons=source_contrasts(self.rows())
        r=next(c for c in comparisons if c['scenario_id']=='oveysi2010_W2_D4')
        self.assertGreater(r['ratio'],1.)
        self.assertTrue(all(c['confidence_interval'] is None and not c['standard_error_inferred'] for c in comparisons))


if __name__=='__main__':unittest.main()
