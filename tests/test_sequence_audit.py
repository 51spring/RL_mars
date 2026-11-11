"""Native snapshot regressions for the private maize harvest handoff audit."""
import copy
import json
from pathlib import Path
import sys
import unittest
from jinja2 import Template
import yaml
from mars_env.sequence_audit import (sequence_filex, SequenceProtocol,
    SequenceAuditBackend, analyze_handoff, rounded_balance, Q_FIELDS, S_FIELDS)
from mars_env.dssat_backend import terminal_template

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'docker'))
import patch_sequence_units
import patch_sequence_audit
import patch_harvest_boundary


class SequenceTests(unittest.TestCase):
    def snapshot(self):
        return json.loads((ROOT/'tests/fixtures/sequence_native_handoff.json').read_text())

    def test_native_snapshot_has_correct_dm_but_duplicate_leaf_n(self):
        fixed = self.snapshot()
        report = analyze_handoff(fixed)
        self.assertTrue(report['handoff_passed'])
        self.assertTrue(report['partition']['residue_dm']['passed'])
        self.assertFalse(report['partition']['residue_n']['passed'])
        self.assertAlmostEqual(report['partition']['residue_n']['residual'],
                               report['predicted_native_duplicate_n'],places=4)
        self.assertFalse(report['whole_elemental_carbon_balance_verified'])
        self.assertFalse(report['research_ready'])
        # The withdrawn x10 candidate must fail against producer units/inventory.
        original = copy.deepcopy(fixed)
        original['harvests'][0]['residue_dm'] = 8605.5966796875
        original['harvests'][0]['residue_n'] = 73.72406005859375
        self.assertFalse(analyze_handoff(original)['partition_passed'])

    def test_missing_soil_flux_is_detected_and_missing_event_refused(self):
        result = self.snapshot()
        result['soils'][-1]['mulch_n'] -= .1
        self.assertFalse(analyze_handoff(result)['handoff_passed'])
        result['soils'].pop()
        with self.assertRaises(ValueError): analyze_handoff(result)
        with self.assertRaises(ValueError): rounded_balance(float('nan'), 1, 1)

    def test_sequence_calendar_and_crop_mismatch_refused(self):
        for field in ('date','crop1'):
            result=self.snapshot()
            result['soils'][-2][field] += 1
            with self.assertRaises(ValueError): analyze_handoff(result)

    def test_q_and_f_have_distinct_native_treatment_and_calendar_input(self):
        template=(ROOT/'vendor/gym_dssat_pdi/gym-dssat-pdi/gym_dssat_pdi/envs/configs/maize/UFGA8201.jinja2').read_text()
        template=Template(template).render(plant='R',irrig='L',ferti='L')
        q,f=[sequence_filex(template,50,50,mode) for mode in ('Q','F')]
        self.assertIn(' 1 2 1 0',q)
        self.assertIn(' 2 1 1 0',f)
        self.assertNotIn('82192',q)
        self.assertIn('82192',f)
        self.assertEqual(q.count('*SIMULATION CONTROLS'),1)
        self.assertEqual(q.count('@N GENERAL'),2)
        for text in (q,f):
            lines=text.splitlines()
            row=lines[next(i for i,l in enumerate(lines) if l.startswith('@N HARVEST'))+1]
            self.assertEqual(row[26:32].strip(),'50')
            self.assertEqual(row[32:38].strip(),'50')
            full=sequence_filex(template,100,100,'Q').splitlines()
            full_row=full[next(i for i,l in enumerate(full) if l.startswith('@N HARVEST'))+1]
            self.assertEqual(full_row[32:38].strip(),'100')
            self.assertEqual(len(full_row),38)
        for args in [(101,0,'Q'),(100,0,'C')]:
            with self.assertRaises(ValueError): sequence_filex(template,*args)

    def test_private_schema_does_not_enable_research_writer(self):
        template=(ROOT/'vendor/gym_dssat_pdi/gym-dssat-pdi/gym_dssat_pdi/envs/configs/maize/dssat_pdi.jinja2').read_text()
        patched=SequenceProtocol().patch_template(terminal_template(template))
        rendered=yaml.safe_load(Template(patched).render(port=12345,rseed1=123456))
        for prefix,fields in [('Q',Q_FIELDS),('S',S_FIELDS)]:
            for field in fields:
                name=f'MARS_{prefix}_{field}'
                self.assertIn(name,rendered['data'])
                self.assertNotIn(name,rendered['metadata'])
        self.assertFalse(SequenceAuditBackend().supports_leaf_damage)

    def test_withdrawn_unit_adapter_cannot_be_applied(self):
        source=(ROOT/'vendor/dssat-pdi-source/Plant/CERES-Maize/MZ_CERES.for').read_text()
        with self.assertRaises(ValueError):patch_sequence_units.patch(source)

    def test_read_only_hooks_reject_duplicate_instrumentation(self):
        source=(ROOT/'vendor/dssat-pdi-source/Plant/CERES-Maize/MZ_CERES.for').read_text()
        fixed=patch_sequence_audit.patch_crop(patch_harvest_boundary.patch(source))
        with self.assertRaises(ValueError): patch_sequence_audit.patch_crop(fixed)
        soil=(ROOT/'vendor/dssat-pdi-source/Soil/CERES_OrganicMatter/SoilOrg_init.for').read_text(encoding='latin-1')
        instrumented=patch_sequence_audit.patch_soil(soil)
        self.assertIn('IF (RUN > 1)',instrumented)
        with self.assertRaises(ValueError): patch_sequence_audit.patch_soil(instrumented)


if __name__=='__main__': unittest.main()
