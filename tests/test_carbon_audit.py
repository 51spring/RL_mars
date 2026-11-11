import copy
import unittest
from mars_env.carbon_audit import carbon_runs,audit_soil_carbon,verify_soil_residue_carbon,carbon_coverage,INITIAL,FINAL,LOSSES,ADDITIONS,SENESCENCE


def row(day=1):
    r=dict(YEAR='1982',DOY=f'{day:03}',DAS=str(day))
    r.update({k:'0.00' for k in (*INITIAL,*FINAL,*LOSSES,*ADDITIONS,*SENESCENCE)})
    r.update(DAYBAL='0.0000',CUMBAL='0.0000')
    return r


class CarbonAuditTests(unittest.TestCase):
    def test_arithmetic_success_does_not_hide_terminal_or_run_coverage_gap(self):
        runs={1:[row()]}
        self.assertTrue(audit_soil_carbon(runs)['soil_output_arithmetic_passed'])
        self.assertFalse(carbon_coverage(runs,1982002)['complete'])
        self.assertEqual(carbon_coverage(runs,1982002)['missing_terminal_days'],1)
        self.assertTrue(carbon_coverage(runs,1982001)['complete'])
        with self.assertRaises(ValueError):carbon_coverage({1:[row()],2:[row(3)]},1982003)

    def test_co2_carbon_mass_and_missing_flux_detection(self):
        r=row();r.update(SOMCTi='100.00',SOMCT='99.00',CO2ED='1.00')
        self.assertTrue(audit_soil_carbon({1:[r]})['soil_output_arithmetic_passed'])
        r['CO2ED']='0.00'
        with self.assertRaises(ValueError):audit_soil_carbon({1:[r]})

    def test_previous_day_senescence_and_run_reset(self):
        a=row();a['SNCLD']='1.00';b=row(2);b['LC0D']='1.00'
        result=audit_soil_carbon({1:[a,b],2:[row()]})
        self.assertEqual(result['days'],3);self.assertFalse(result['whole_elemental_carbon_verified'])
        b['LC0D']='0.00'
        with self.assertRaises(ValueError):audit_soil_carbon({1:[a,b]})

    def test_separate_run_identity_and_nonconsecutive_dates(self):
        r=row();header=' '.join(r)
        text='*RUN 1\n@'+header+'\n'+' '.join(r.values())+'\n*RUN 2\n@'+header+'\n'+' '.join(r.values())
        self.assertEqual(set(carbon_runs(text)),{1,2})
        with self.assertRaises(ValueError):carbon_runs(text.replace('*RUN 2','*RUN 1'))
        with self.assertRaises(ValueError):carbon_runs(text.split('*RUN 2')[0]+'\n'+' '.join(row(3).values()))

    def test_residue_point_four_is_only_the_soil_interface(self):
        r=row();r['THRC0D']='4.00';r['THRC1D']='2.00'
        runs={1:[row()],2:[r,row(2)]};d={'soils':[dict(run=2,phase=1,surface_dm=10,root_dm=5)]}
        self.assertTrue(verify_soil_residue_carbon(runs,d)['passed'])
        bad=copy.deepcopy(runs);bad[2][1]['THRC0D']='4.00'
        with self.assertRaises(ValueError):verify_soil_residue_carbon(bad,d)
        r['THRC0D']='10.00'
        with self.assertRaises(ValueError):verify_soil_residue_carbon(runs,d)


if __name__=='__main__':unittest.main()
