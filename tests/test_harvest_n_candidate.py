import json
import hashlib
from pathlib import Path
import sys
import unittest
from mars_env.sequence_audit import analyze_handoff
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'docker'))
import patch_harvest_n_inventory


class HarvestNCandidateTests(unittest.TestCase):
    def test_only_local_surface_n_is_removed_and_other_consumers_preserved(self):
        p=ROOT/'vendor/dssat-pdi-source/Plant/CERES-Maize/MZ_CERES.for'
        digest=hashlib.sha256(p.read_bytes()).hexdigest();source=p.read_text()
        fixed=patch_harvest_n_inventory.patch(source)
        self.assertIn('MARS_N_HARV_SEN = SENESCE',fixed)
        self.assertIn('MARS_N_HARV_SEN % ResE(0,N) = 0.0',fixed)
        self.assertNotIn('MARS_N_HARV_SEN % ResWt',fixed)
        self.assertNotIn('MARS_N_HARV_SEN % ResLig',fixed)
        for name in ('MZ_GROSUB','MZ_OPHARV','MZ_OPNIT','MZ_OPGROW'):
            calls=lambda s:[name+t.split('!Output',1)[0] for t in s.split('CALL '+name)[1:]]
            self.assertEqual(calls(source),calls(fixed))
        self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),digest)

    def test_source_drift_and_duplicate_patch_refused(self):
        source=(ROOT/'vendor/dssat-pdi-source/Plant/CERES-Maize/MZ_CERES.for').read_text()
        with self.assertRaises(ValueError):patch_harvest_n_inventory.patch(patch_harvest_n_inventory.patch(source))
        with self.assertRaises(ValueError):patch_harvest_n_inventory.patch(source.replace('CALL HRes_Ceres','CALL Different_HRes'))

    def test_captured_native_candidate_passes_independent_inventory_but_stays_experimental(self):
        r=json.loads((ROOT/'tests/fixtures/harvest_n_candidate.json').read_text())
        a=analyze_handoff(r)
        self.assertTrue(a['handoff_passed']);self.assertTrue(a['partition_passed'])
        self.assertFalse(a['whole_postharvest_system_balance_verified'])
        self.assertFalse(a['research_ready'])
        r['harvests'][0]['residue_n']+=r['harvests'][0]['dead_leaf_n_raw']
        self.assertFalse(analyze_handoff(r)['partition_passed'])


if __name__=='__main__':unittest.main()
