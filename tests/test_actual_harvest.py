import copy
import json
from pathlib import Path
import re
import sys
import unittest
from jinja2 import Template
import yaml
from mars_env.ear_diagnostics import EarProtocol,verify_organ_record,EAR_FIELDS,BAR_FIELDS
from mars_env.actual_harvest_contract import check_actual_contract
from mars_env.dssat_backend import terminal_template
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'docker'))
import patch_ear_audit,patch_harvest_n_inventory,patch_harvest_actual_exports


class ActualHarvestTests(unittest.TestCase):
    def fixture(self):
        return json.loads((ROOT/'tests/fixtures/actual_harvest.json').read_text())

    def test_ear_protocol_private_and_history_sent_only_at_terminal(self):
        p=ROOT/'vendor/gym_dssat_pdi/gym-dssat-pdi/gym_dssat_pdi/envs/configs/maize/dssat_pdi.jinja2'
        patched=EarProtocol().patch_template(terminal_template(p.read_text()))
        parsed=yaml.safe_load(Template(patched).render(port=12345,rseed1=123456))
        for prefix,fields in [('E',EAR_FIELDS),('B',BAR_FIELDS)]:
            for field in fields:
                name=f'MARS_{prefix}_{field}'
                self.assertIn(name,parsed['data']);self.assertNotIn(name,parsed['metadata'])
        self.assertEqual(patched.count('mars_ear_records if done else mars_ear_records[-1:]'),2)

    def test_read_only_hooks_follow_native_values_and_reject_duplicate(self):
        base=ROOT/'vendor/dssat-pdi-source/Plant/CERES-Maize'
        for name,fn in [('MZ_GROSUB.for',patch_ear_audit.patch_growth),('MZ_PHENOL.for',patch_ear_audit.patch_phenology)]:
            old=(base/name).read_text();new=fn(old)
            for line in old.splitlines():
                self.assertIn(line,new.splitlines())
            with self.assertRaises(ValueError):fn(new)

    def test_direct_organ_values_detect_wrong_ear_basis(self):
        r=self.fixture()['ear'];self.assertTrue(verify_organ_record(r)['passed'])
        changed=dict(r,podwt=r['earwt']*r['population'])
        self.assertFalse(verify_organ_record(changed)['passed'])

    def test_adapter_changes_only_local_harvest_arguments(self):
        p=ROOT/'vendor/dssat-pdi-source/Plant/CERES-Maize/MZ_CERES.for'
        old=patch_harvest_n_inventory.patch(p.read_text())
        new=patch_harvest_actual_exports.patch(old)
        self.assertIn('MARS_A_POD = TOPWT - STOVWT * PLTPOP',new)
        self.assertIn('MARS_A_SEEDN = GNUP / 10.0',new)
        self.assertNotRegex(new,r'(?m)^ +(?:GRNWT|PODWT|STOVN|WTNSD)\s*=')
        for name in ('MZ_GROSUB','MZ_OPHARV','MZ_OPGROW','MZ_OPNIT'):
            calls=lambda s:[name+c.split('!Output',1)[0] for c in s.split('CALL '+name)[1:]]
            self.assertEqual(calls(old),calls(new))

    def test_actual_export_contract_closes_native_low_input_snapshot(self):
        f=self.fixture();r=check_actual_contract(f['harvest'],f['ear'])
        self.assertTrue(r['passed']);self.assertFalse(r['research_ready'])
        self.assertTrue(r['byproduct_n_is_defined_allocation_not_native_measurement'])
        h=dict(f['harvest'],residue_n=f['harvest']['residue_n']+.1)
        self.assertFalse(check_actual_contract(h,f['ear'])['passed'])

    def test_contract_refuses_wrong_date_or_unvalidated_zero_population(self):
        f=self.fixture()
        for changes in ({'date':f['ear']['date']+1},{'population':0},{'stovwt':0}):
            with self.assertRaises(ValueError):check_actual_contract(f['harvest'],dict(f['ear'],**changes))

    def test_actual_adapter_refuses_source_drift_or_reapplication(self):
        p=ROOT/'vendor/dssat-pdi-source/Plant/CERES-Maize/MZ_CERES.for'
        old=patch_harvest_n_inventory.patch(p.read_text());new=patch_harvest_actual_exports.patch(old)
        with self.assertRaises(ValueError):patch_harvest_actual_exports.patch(new)
        with self.assertRaises(ValueError):patch_harvest_actual_exports.patch(p.read_text())


if __name__=='__main__':unittest.main()
