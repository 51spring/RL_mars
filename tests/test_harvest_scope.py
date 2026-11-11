import json
from pathlib import Path
import unittest
from jinja2 import Template
from mars_env.harvest_scope import actual_export_boundary
from mars_env.sequence_audit import sequence_filex,analyze_handoff
ROOT=Path(__file__).resolve().parents[1]


class HarvestScopeTests(unittest.TestCase):
    def snapshot(self):
        return json.loads((ROOT/'tests/fixtures/harvest_n_candidate.json').read_text())

    def test_actual_export_stock_match_qualified_and_missing_inventory_rejected(self):
        h=self.snapshot()['harvests'][0];r=actual_export_boundary(h)
        self.assertTrue(r['scope_qualified'])
        self.assertFalse(r['research_ready'])
        self.assertTrue(r['byproduct_n_is_external_allocation'])
        with self.assertRaises(ValueError):actual_export_boundary(dict(h,grain_fraction=0.))
        with self.assertRaises(ValueError):actual_export_boundary(dict(h,root_n=float('nan')))

    def test_actual_export_loss_is_not_hidden_by_population_partition(self):
        h=self.snapshot()['harvests'][0]
        h['grain_dm']*=.8;h['harvest_grain_n']*=.8
        r=actual_export_boundary(h)
        self.assertTrue(r['population_export_mismatch'])
        self.assertFalse(r['actual_export_boundary_passed'])
        self.assertFalse(r['scope_qualified'])
        self.assertAlmostEqual(r['inferred_ears_to_population_dm_ratio'],.8,places=6)

    def test_captured_low_input_run_stays_outside_candidate_scope(self):
        fixture=json.loads((ROOT/'tests/fixtures/harvest_scope_low_input.json').read_text())
        r=actual_export_boundary(fixture['harvest'])
        self.assertFalse(r['scope_qualified'])
        self.assertAlmostEqual(r['actual_export_boundary']['n']['residual'],-.0709381103515625)
        self.assertAlmostEqual(r['actual_export_boundary']['dm']['residual'],-13.881839752197266)
        self.assertTrue(r['ratio_is_inferred_not_direct_ears_observation'])

    def test_f_start_uses_measured_harvest_date_and_invalid_doy_refused(self):
        p=ROOT/'vendor/gym_dssat_pdi/gym-dssat-pdi/gym_dssat_pdi/envs/configs/maize/UFGA8201.jinja2'
        template=Template(p.read_text()).render(plant='R',irrig='L',ferti='L')
        lines=sequence_filex(template,100,0,'F',1982181).splitlines()
        generals=[lines[i+1] for i,l in enumerate(lines) if l.startswith('@N GENERAL')]
        self.assertEqual(generals[0][32:38].strip(),'82030')
        self.assertEqual(generals[1][32:38].strip(),'82181')
        with self.assertRaises(ValueError):sequence_filex(template,100,0,'F',1982366)

    def test_next_season_dates_roll_over_and_both_phases_must_match(self):
        r=self.snapshot();r['harvests'][0]['date']=1982365
        for s in r['soils']:
            if s['run']==2:s['date']=1983001
        self.assertTrue(analyze_handoff(r)['handoff_passed'])
        r['soils'][-1]['date']=1983002
        with self.assertRaises(ValueError):analyze_handoff(r)


if __name__=='__main__':unittest.main()
