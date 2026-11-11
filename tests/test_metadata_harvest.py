import hashlib
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from jinja2 import Template
import yaml
from mars_env.input_metadata import canonical_ufga_metadata,field_metadata,summary_metadata
from mars_env.harvest_diagnostics import HarvestProtocol,HarvestBoundaryBackend,HARVEST_FIELDS
from mars_env.dssat_backend import terminal_template
from mars_env.dssat_backend import DssatBackend

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'docker'))
import patch_metadata_source
import patch_harvest_boundary


class MetadataTests(unittest.TestCase):
    def template(self):
        return (ROOT/'vendor/gym_dssat_pdi/gym-dssat-pdi/gym_dssat_pdi/envs/configs/maize/UFGA8201.jinja2').read_text()

    def test_coordinate_schema_explicit_and_other_input_unchanged(self):
        old=self.template();new=canonical_ufga_metadata(old)
        before=old.splitlines();after=new.splitlines()
        changed=[i for i,(a,b) in enumerate(zip(before,after)) if a!=b]
        self.assertEqual(len(changed),1)
        row=after[changed[0]]
        self.assertEqual(float(row[3:18]),-82.3689);self.assertEqual(float(row[19:34]),29.638)
        self.assertEqual(float(row[35:44]),40.)
        self.assertEqual(before[changed[0]][44:],row[44:])
        with self.assertRaises(ValueError):canonical_ufga_metadata(old.replace('UFGA0002','OTHER001'))
        with self.assertRaises(ValueError):field_metadata(old,longitude=float('nan'))

    def test_summary_metadata_reads_blanks_without_shifting_columns(self):
        header='@RUNNO'+'XLAT'.rjust(16)+'LONG'.rjust(16)+'ELEV'.rjust(10)+'HWAH'.rjust(8)
        row='     1'+'29.6380'.rjust(16)+'-82.3689'.rjust(16)+'40'.rjust(10)+'6861'.rjust(8)
        self.assertEqual(summary_metadata(header+'\n'+row),{'XLAT':29.638,'LONG':-82.3689,'ELEV':40.})
        blank='     1'+' '*42+'6861'.rjust(8)
        self.assertEqual(summary_metadata(header+'\n'+blank),{'XLAT':None,'LONG':None,'ELEV':None})

    def test_corrected_profile_is_explicit_and_does_not_enable_research(self):
        values={'MARS_DSSAT_RUN_LOCATION':'/opt/mars/run_metadata',
                'MARS_LEAF_RUN_LOCATION':'/opt/mars/run_metadata','MARS_CANONICAL_UFGA_METADATA':'1'}
        with patch.dict('os.environ',values):
            backend=DssatBackend();self.assertTrue(backend.canonical_metadata)
            self.assertEqual(backend.run_dssat_location,'/opt/mars/run_metadata')
            self.assertFalse(backend.supports_leaf_damage)
            with self.assertRaises(Exception):DssatBackend(pest_enabled=True)
        with patch.dict('os.environ',{'MARS_CANONICAL_UFGA_METADATA':'unknown'}):
            with self.assertRaises(ValueError):DssatBackend()

    def test_patch_refuses_source_drift_and_does_not_write_vendor(self):
        for relative,fn in [('InputModule/ipexp.for',patch_metadata_source.patch_ipfld),
            ('Utilities/ModuleDefs.for',patch_metadata_source.patch_module),
            ('InputModule/IPSOIL_Inp.for',patch_metadata_source.patch_conductivity_warning)]:
            p=ROOT/'vendor/dssat-pdi-source'/relative;digest=hashlib.sha256(p.read_bytes()).hexdigest()
            fixed=fn(p.read_text());self.assertNotEqual(fixed,p.read_text())
            with self.assertRaises((ValueError,AssertionError)):fn(fixed)
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),digest)

    def test_harvest_protocol_is_privileged_and_does_not_authorize_research(self):
        original=(ROOT/'vendor/gym_dssat_pdi/gym-dssat-pdi/gym_dssat_pdi/envs/configs/maize/dssat_pdi.jinja2').read_text()
        result=HarvestProtocol().patch_template(terminal_template(original))
        rendered=yaml.safe_load(Template(result).render(port=12345,rseed1=123456))
        for field in HARVEST_FIELDS:
            self.assertIn('MARS_H_'+field,rendered['data'])
            self.assertNotIn('MARS_H_'+field,rendered['metadata'])
        self.assertEqual(result.count("'mars_harvest_boundary': mars_harvest_record"),2)
        self.assertFalse(HarvestBoundaryBackend().supports_leaf_damage)

    def test_harvest_hook_follows_native_residues_and_precedes_senescence_clear(self):
        original=(ROOT/'vendor/dssat-pdi-source/Plant/CERES-Maize/MZ_CERES.for').read_text()
        fixed=patch_harvest_boundary.patch(original)
        event=fixed.index('CALL pdi_transaction_begin("mars_harvest_boundary")')
        self.assertLess(fixed.index('CALL HRes_Ceres(CONTROL,'),event)
        self.assertLess(event,fixed.index('!Set senescence variable to zero for next season'))
        self.assertEqual(fixed.count('CALL HRes_Ceres(CONTROL,'),original.count('CALL HRes_Ceres(CONTROL,'))


if __name__=='__main__':unittest.main()
