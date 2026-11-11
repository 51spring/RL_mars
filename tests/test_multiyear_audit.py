import copy
from pathlib import Path
import unittest
from jinja2 import Template
from mars_env.multiyear_audit import two_year_filex,audit_boundaries
ROOT=Path(__file__).resolve().parents[1]


class MultiyearAuditTests(unittest.TestCase):
    def test_explicit_four_rotations_and_single_two_year_horizon(self):
        source=ROOT/'vendor/gym_dssat_pdi/gym-dssat-pdi/gym_dssat_pdi/envs/configs/maize/UFGA8201.jinja2'
        text=two_year_filex(Template(source.read_text()).render(plant='R',irrig='L',ferti='L'),50,50)
        lines=text.splitlines();i=next(i for i,l in enumerate(lines) if l.startswith('@N R O C '))
        self.assertEqual([int(l[3]) for l in lines[i+1:i+5]],[1,2,3,4])
        self.assertEqual([int(l.split()[-1]) for l in lines[i+1:i+5]],[1,2,3,4])
        self.assertEqual([int(l.split()[-10]) for l in lines[i+3:i+5]],[0,0])
        generals=[lines[i+1].split() for i,l in enumerate(lines) if l.startswith('@N GENERAL')]
        self.assertEqual([int(r[0]) for r in generals],[1,2,3,4])
        self.assertEqual([int(r[2]) for r in generals],[2,1,1,1])

    def fixture(self):
        h=[dict(run=1,date=1982200,residue_dm=30,residue_n=3),dict(run=3,date=1983200,residue_dm=30,residue_n=3)]
        soils=[]
        for run,date,crop in ((1,1982030,'MZ'),(2,1982201,'FA'),(3,1983030,'MZ'),(4,1983201,'FA')):
            incoming=0 if run in (1,3) else 1
            for phase in (1,2):
                soils.append(dict(run=run,date=date,crop1=ord(crop[0]),crop2=ord(crop[1]),rnmode=ord('Q'),phase=phase,
                    root_dm=10*incoming,surface_dm=20*incoming,root_n=incoming,surface_n=2*incoming,
                    soil_dm=100+(phase-1)*10*incoming,mulch_dm=200+(phase-1)*20*incoming,
                    soil_n=10+(phase-1)*incoming,mulch_n=20+(phase-1)*2*incoming))
        return dict(harvests=h,soils=soils)

    def test_three_boundaries_and_no_whole_n_promotion(self):
        r=audit_boundaries(self.fixture())
        self.assertTrue(r['passed']);self.assertEqual(len(r['boundaries']),3)
        self.assertFalse(r['multiyear_full_n_balance_verified'])

    def test_repeated_residue_wrong_dates_and_missing_boundary_refused(self):
        for defect in ('repeat','date','mode','missing'):
            d=copy.deepcopy(self.fixture())
            if defect=='repeat':d['soils'][4]['surface_n']=2
            elif defect=='date':d['soils'][4]['date']+=1
            elif defect=='mode':d['soils'][4]['rnmode']=ord('F')
            else:d['soils'].pop()
            with self.assertRaises(ValueError):audit_boundaries(d)


if __name__=='__main__':unittest.main()
