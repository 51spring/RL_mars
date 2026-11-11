from pathlib import Path
import unittest
from jinja2 import Template
from mars_env.f_mode_calendar import f_filex,launcher_text
from mars_env.multiyear_audit import audit_boundaries
import test_multiyear_audit as fixtures
ROOT=Path(__file__).resolve().parents[1]


class FCalendarTests(unittest.TestCase):
    def template(self):
        p=ROOT/'vendor/gym_dssat_pdi/gym-dssat-pdi/gym_dssat_pdi/envs/configs/maize/UFGA8201.jinja2'
        return Template(p.read_text()).render(plant='R',irrig='L',ferti='L')

    def test_f_explicit_treatments_controls_and_second_year_factors(self):
        lines=f_filex(self.template(),50,50,{1:1982192,3:1983185}).splitlines()
        i=next(i for i,l in enumerate(lines) if l.startswith('@N R O C '))
        self.assertEqual([int(l[1]) for l in lines[i+1:i+5]],[1,2,3,4])
        self.assertEqual([int(l[3]) for l in lines[i+1:i+5]],[1,1,1,1])
        generals=[dict(zip(l.split()[2:],lines[i+1].split()[2:])) for i,l in enumerate(lines) if l.startswith('@N GENERAL')]
        self.assertEqual([g['SDATE'] for g in generals],['82030','82192','83029','83185'])
        self.assertIn('83057','\n'.join(lines));self.assertIn('84029','\n'.join(lines))
        self.assertEqual(launcher_text(4).count("'MARS8201.SQX'"),4)

    def test_missing_or_wrong_year_dates_and_unsupported_launcher_refused(self):
        for dates in ({1:1982192},{1:1982192,3:1982185}):
            with self.assertRaises(ValueError):f_filex(self.template(),100,0,dates)
        with self.assertRaises(ValueError):launcher_text(3)

    def test_mode_is_explicit_in_boundary_checks(self):
        d=fixtures.MultiyearAuditTests().fixture()
        for s in d['soils']:s['rnmode']=ord('F')
        with self.assertRaises(ValueError):audit_boundaries(d)
        self.assertTrue(audit_boundaries(d,expected_mode='F')['passed'])
