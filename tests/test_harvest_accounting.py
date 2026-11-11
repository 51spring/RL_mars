import json
from pathlib import Path
import unittest
from mars_env.harvest_accounting import c_harvest_allocation,harvest_summary
from mars_env.dssat_backend import BackendContractError

ROOT=Path(__file__).resolve().parents[1]


class HarvestAccountingTests(unittest.TestCase):
    def native(self):
        h=json.loads((ROOT/'tests/fixtures/sequence_native_handoff.json').read_text())['harvests'][0]
        return dict(h,rnmode=float(ord('C')),residue_dm=0.,residue_n=0.)

    def test_c_exports_do_not_duplicate_standing_grain_or_leaf_n(self):
        h=self.native();r=c_harvest_allocation(h)
        self.assertAlmostEqual(r['before']['nitrogen_kg_ha'],140.8071746826172)
        self.assertAlmostEqual(r['retained']['nitrogen_kg_ha'],59.58806610107422)
        self.assertTrue(all(c['passed'] for c in r['checks'].values()))
        self.assertFalse(r['native_state_transition_executed'])
        self.assertFalse(r['elemental_carbon_verified'])
        self.assertEqual(h,self.native())

    def test_stressed_yield_uses_actual_exports_and_reports_stock_mismatch(self):
        h=self.native();h['grain_dm']*=.8;h['harvest_grain_n']*=.8
        r=c_harvest_allocation(h)
        self.assertEqual(r['grain_export']['dry_matter_kg_ha'],h['grain_dm'])
        self.assertFalse(r['requested_fraction_of_population_grain_stock']['dm']['passed'])
        self.assertFalse(r['requested_fraction_of_population_grain_stock']['n']['passed'])

    def test_invalid_native_mode_stock_and_unobserved_zero_grain_fraction_refused(self):
        for changes in ({'rnmode':float(ord('Q'))},{'residue_n':1.},{'grain_fraction':0.},
                        {'canopy_n':float('nan')},{'harvest_grain_n':10000.}):
            with self.assertRaises(BackendContractError):c_harvest_allocation(dict(self.native(),**changes))

    def test_summary_reads_fixed_columns_and_refuses_multiple_seasons(self):
        names=['RUNNO','HWAH','BWAH','CWAM','CNAM','GNAM']
        header='@'+''.join(n.rjust(8) for n in names)
        row=' '+''.join(str(v).rjust(8) for v in [1,4707,0,10758,121,81])
        r=harvest_summary(header+'\n'+row)
        self.assertEqual(r['HWAH'],4707)
        with self.assertRaises(BackendContractError):harvest_summary(header+'\n'+row+'\n'+row)

    def test_observability_distinguishes_dry_matter_proxy_and_missing_elemental_c(self):
        data=json.loads((ROOT/'configs/balance_observability.json').read_text())
        items={i['id']:i for i in data['items']}
        self.assertFalse(data['whole_elemental_carbon_observed'])
        self.assertEqual(items['senesced_leaf_dry_matter']['unit'],'kg dry matter/ha')
        self.assertEqual(items['crop_assimilate_proxy']['status'],'biomass_proxy')
        self.assertEqual(items['crop_respiration_c']['status'],'not_separately_observed')
        self.assertEqual(items['native_qf_surface_n']['status'],'native_transfer_with_inventory_anomaly')


if __name__=='__main__':unittest.main()
