import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import gymnasium as gym
import numpy as np
import yaml
from mars_env.artifacts import new_run,sha256
from mars_env.audits import shift_yrdoy,weather_rows,verify_completed_weather,management_events
from mars_env.observations import FIELDS,OBSERVATION_SIZE
from mars_env.policies import RulePolicy,IrrigationOnly
from mars_env.soil_audit import daily_table,precision,reconstruct_soil,preharvest_n_inventory
from mars_env.training_env import SeasonCycler


def observation(**values):
    frame=np.array([values.get(key,0)/scale for key,scale in FIELDS],dtype=np.float32)
    return np.tile(frame,7)


class AuditTests(unittest.TestCase):
    def test_calendar_year_and_leap_day(self):
        self.assertEqual(shift_yrdoy(2020366,1),2021001)
        self.assertEqual(shift_yrdoy(2021001,-1),2020366)
        with self.assertRaises(ValueError):shift_yrdoy(2021366,0)

    def test_weather_date_and_rounding_reject_shifted_day(self):
        rows=weather_rows('@YEAR DOY DAS PRED SRAD TMXD TMND\n 1982 030 1 1.2 10.3 20.4 15.2\n 1982 031 2 8.0 20.0 30.0 19.0\n')
        state={'rain':1.24,'srad':10.31,'tmax':20.4,'tmin':15.2}
        verify_completed_weather(state,1982030,rows)
        with self.assertRaises(AssertionError):verify_completed_weather(state,1982031,rows)
        with self.assertRaises(ValueError):weather_rows('@YEAR DOY DAS PRED\n 1982 030 1\n')

    def test_native_management_dates_and_quantities(self):
        text='   1 FEB 26, 1982 057 28 0 MZ Irrigation 10.0 mm\n   1 APR 7, 1982 097 68 40 MZ Fertilizer 27. kg[N]/ha'
        self.assertEqual(management_events(text),[(1982057,'Irrigation',10.),(1982097,'Fertilizer',27.)])

    def test_native_table_ends_before_legacy_restart(self):
        rows=daily_table('@YEAR DOY DAS X\n 1982 029 0 5.0\n 1982 030 1 4.0\n@YEAR DOY DAS X\n 1982 029 0 5.0\n')
        self.assertEqual(len(rows),2);self.assertEqual(precision('4.00'),.005)

    def test_unique_runs_snapshot_config_without_overwrite(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]/'tmp') as temp:
            root=Path(temp);(root/'configs').mkdir();(root/'configs/proposal_v2.yaml').write_text('a: 1')
            first=new_run(root,'check',image_id='sha256:test');second=new_run(root,'check')
            self.assertNotEqual(first,second)
            self.assertEqual(json.loads((first/'manifest.json').read_text())['source_sha256']['configs/proposal_v2.yaml'],sha256(root/'configs/proposal_v2.yaml'))


class PolicyTests(unittest.TestCase):
    def test_rule_inputs_and_feasible_downward_quantization(self):
        mask=np.ones(17,dtype=bool);mask[6+3]=False;mask[2]=False
        rule=RulePolicy(baseline_nitrogen=((40,27),(45,35),(80,54)))
        action=rule.action(observation(dap=40,swfac=.8,survey_available=1,survey_value=.8),mask)
        np.testing.assert_array_equal(action,[1,2,1])
        mask[16]=False
        self.assertEqual(rule.action(observation(dap=45),mask)[2],0)

    def test_irrigation_only_shares_nitrogen_and_spray_and_rejects_invalid(self):
        class Base(gym.Env):
            observation_space=gym.spaces.Box(-np.inf,np.inf,(OBSERVATION_SIZE,),np.float32)
            action_space=gym.spaces.MultiDiscrete([6,9,2])
            def reset(self,**kwargs):return observation(dap=40,survey_available=1,survey_value=.8),{}
            def action_masks(self):return np.ones(17,dtype=bool)
            def step(self,action):self.action=action;return observation(dap=41),0.,False,False,{}
        base=Base();env=IrrigationOnly(base,RulePolicy(baseline_nitrogen=((40,27),(45,35),(80,54))));env.reset();env.step(4)
        np.testing.assert_array_equal(base.action,[4,3,1]);self.assertEqual(env.action_masks().shape,(6,))
        with self.assertRaises(ValueError):env.step(6)

    def test_resume_keeps_next_unused_address_even_with_policy_seed(self):
        root=Path(__file__).resolve().parents[1]
        config=yaml.safe_load((root/'configs/proposal_v2.yaml').read_text(encoding='utf-8'))
        class Base:
            def __init__(self,**kwargs):pass
            def reset(self,**kwargs):return np.zeros(OBSERVATION_SIZE,dtype=np.float32),{}
            def close(self):pass
        env=SeasonCycler(config,rank=2,n_envs=4,shaping=False)
        with patch('mars_env.training_env.CropManagementEnv',Base):
            env.set_season_cursor(49)
            self.assertEqual(env.reset(seed=42)[1]['external_season_id'],198)
            self.assertEqual(env.reset()[1]['external_season_id'],202)
            env.restart_sequence()
            self.assertEqual(env.reset()[1]['external_season_id'],2)
            env.close()


class SoilAndEvidenceTests(unittest.TestCase):
    def test_preharvest_n_includes_damage_export_without_double_counting_grain(self):
        root=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=root/'tmp') as temp:
            folder=Path(temp)
            keys='SN0Di S1NTDi S2NTDi S3NTDi LNTDi NIADi SN0D S1NTD S2NTD S3NTD LNTD NIAD HRNH RESNC NICM SNNTC NLCM TDFC NGasC RNRO'.split()
            values={'SN0Di':'10.000','SN0D':'5.000','NICM':'1.000'}
            (folder/'SoilNBalSum.OUT').write_text('@Run FILEX TN CR '+' '.join(keys)+'\n 1 test.MZX 3 MZ '+' '.join(values.get(k,'0.000') for k in keys))
            audit={'canopy_n':.5,'rootn':0.,'population':7.2,'cum_n':.2,'seed_n':.1,'grainn':999}
            result=preharvest_n_inventory(folder,audit)
            self.assertAlmostEqual(result['residual_kg_n_ha'],0.)
            self.assertFalse(result['harvest_grain_n_added_again'])
            self.assertFalse(result['post_harvest_n_balance_validated'])
            with self.assertRaises(AssertionError):preharvest_n_inventory(folder,dict(audit,cum_n=0))

    def test_native_soil_reconstruction_keeps_lag_and_rejects_missing_emission(self):
        root=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=root/'tmp') as temp:
            folder=Path(temp)
            ckeys='YEAR DOY DAS SOMC0Ti SOMCTi LC0Di LCTDi CH4STDi SOMC0T SOMCT LC0D LCTD CH4STD RESC0D RESC1D SNCLD SNCSD THRC0D THRC1D CO2ED CH4ED CH4LCD CH4COD DAYBAL CUMBAL'.split()
            okeys='YEAR DOY DAS HUMN FON RESN ARESN ASENN AIMMOBN RMINERP DBAL CBAL'.split()
            ikeys='YEAR DOY DAS NO3 NH4 TUREA TNGAS FLOODN ALGFIX UNFERT AFERT AMINER RIMMOB RLCH RLTD RNUP RNRO RAML N2OED N2ED NOED DBAL CBAL'.split()
            def table(keys,records):
                lines=['@'+' '.join(keys)]
                for i,record in enumerate(records):
                    defaults={'YEAR':'1982','DOY':f'{29+i:03d}','DAS':str(i)}
                    lines.append(' '+' '.join(str(record.get(key,defaults.get(key,'0.0000'))) for key in keys))
                return '\n'.join(lines)
            carbon=table(ckeys,[{'SOMCTi':'10.0000','SOMCT':'9.0000','CO2ED':'1.0000'}])
            (folder/'SoilCBal.OUT').write_text(carbon)
            (folder/'SoilNoBal.OUT').write_text(table(okeys,[{'HUMN':'10.0000','FON':'1.0000'},
                {'HUMN':'9.8000','FON':'1.0000','RMINERP':'0.2000','ASENN':'0.4000'}]))
            (folder/'SoilNiBal.OUT').write_text(table(ikeys,[{'NO3':'2.0000'}, {'NO3':'2.1000','AFERT':'0.1000'}]))
            self.assertTrue(reconstruct_soil(folder)['soil_arithmetic_reconstruction_passed'])
            (folder/'SoilCBal.OUT').write_text(table(ckeys,[{'SOMCTi':'10.0000','SOMCT':'9.0000','CO2ED':'0.0000'}]))
            with self.assertRaises(AssertionError):reconstruct_soil(folder)

    def test_evidence_does_not_promote_aggregate_or_embargo_data_to_calibration(self):
        root=Path(__file__).resolve().parents[1]
        studies=json.loads((root/'configs/agronomic_sources.json').read_text(encoding='utf-8'))['studies']
        self.assertEqual(len({s['doi'] for s in studies}),len(studies))
        self.assertFalse(any(s['quantitative_fit_ready'] for s in studies))
        roles={s['id']:s['planned_role'] for s in studies}
        self.assertTrue(roles['santos2018'].startswith('calibration'))
        self.assertTrue(roles['oveysi2010'].startswith('independent'))


if __name__=='__main__':unittest.main()
