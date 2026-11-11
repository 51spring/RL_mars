from copy import deepcopy
from pathlib import Path
import unittest
from jinja2 import Template
import yaml

from mars_env.dssat_backend import BackendContractError, terminal_template
from mars_env.leaf_diagnostics import LeafDiagnosticBackend, LeafProtocol, verify_leaf_accounting


class LeafDiagnosticsTests(unittest.TestCase):
    def test_protocol_adds_fresh_native_records_to_daily_and_terminal_states(self):
        root = Path(__file__).parents[1]
        original = (root / 'vendor/gym_dssat_pdi/gym-dssat-pdi/gym_dssat_pdi/envs/configs/maize/dssat_pdi.jinja2').read_text()
        patched = LeafProtocol().patch_template(terminal_template(original))
        self.assertEqual(patched.count("'mars_leaf_diagnostic': mars_leaf_diagnostic"), 2)
        self.assertIn("mars_leaf_before:", patched)
        self.assertIn("mars_leaf_after:", patched)
        self.assertIn("delta[()] = action.get('mars_leaf_fraction', 0.0)", patched)
        rendered = yaml.safe_load(Template(patched).render(port=12345, rseed1=123456))
        self.assertIn("MARS_DELTA", rendered["data"])
        self.assertNotIn("MARS_DELTA", rendered["metadata"])

    def test_experimental_writer_does_not_enable_research_capability(self):
        backend = LeafDiagnosticBackend()
        self.assertFalse(backend.supports_leaf_damage)
        for fraction in (-0.01, 1.01, float('nan')):
            with self.assertRaises(ValueError):
                backend.step_damage(0, 0, fraction)

    def test_mass_and_nitrogen_accounting_rejects_missing_export(self):
        before = dict(lfwt=2, pla=110, senla=10, stovn=0.3, stmwt=1,
                      xlai=0.1, topwt=4, wtncan=0.4, grainn=0.1, cls=1, cns=0.01)
        after = dict(lfwt=1.5, pla=85, senla=10, stovn=0.25, stmwt=1,
                     xlai=0.0075, topwt=3.5, wtncan=0.35, grainn=0.1, cls=1, cns=0.01)
        record = dict(before=before, after=after, population=1, fraction=0.25,
                      export_dm_g_m2=0.5, export_n_g_m2=0.05)
        verify_leaf_accounting(record)
        for key in ('export_dm_g_m2', 'export_n_g_m2'):
            broken = deepcopy(record)
            broken[key] = 0
            with self.assertRaises(BackendContractError):
                verify_leaf_accounting(broken)

    def test_consumed_tissue_cannot_appear_as_new_dead_litter(self):
        before = dict(lfwt=0, pla=10, senla=10, stovn=0.1, stmwt=1,
                      xlai=0, topwt=1, wtncan=0.1, grainn=0, cls=1, cns=0.01)
        after = dict(before, cls=2)
        record = dict(before=before, after=after, population=1, fraction=0,
                      export_dm_g_m2=0, export_n_g_m2=0)
        with self.assertRaises(BackendContractError):
            verify_leaf_accounting(record)


if __name__ == '__main__':
    unittest.main()
