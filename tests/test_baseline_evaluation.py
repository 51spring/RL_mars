import copy
import unittest
import numpy as np
from mars_env.baseline_evaluation import evaluate_episode,verify_pairs,summarize
from mars_env.environment import CropManagementEnv
from mars_env.exogenous import SeasonExogenous
from mars_env.observations import OBSERVATION_SIZE
from mars_env.policies import NoInputPolicy,RulePolicy
from mars_env.resources import ResourceRules
from test_environment import FakeBackend


class BaselineEvaluationTests(unittest.TestCase):
    def run_policy(self,name='rule',**kwargs):
        season=SeasonExogenous('validation',22001,0,12345,1,None,np.zeros(400),np.zeros(400))
        rules=ResourceRules()
        env=CropManagementEnv(pest_enabled=False,rules=rules,backend_factory=FakeBackend,**kwargs)
        self.addCleanup(env.close)
        policy=NoInputPolicy() if name=='no_input' else RulePolicy(water_stress_threshold=0,baseline_nitrogen=((0,27),(1,35)))
        record=evaluate_episode(env,policy,season,rules,.158);record['policy']=name
        return record

    def test_independent_action_economics_and_raw_rewards(self):
        record=self.run_policy();r=record['episode_result']
        self.assertEqual(r['water_mm'],20);self.assertEqual(r['nitrogen_kg_ha'],62)
        self.assertAlmostEqual(r['total_cost'],22+62*.79+6+10)
        self.assertAlmostEqual(record['raw_return'],158-r['total_cost'])
        self.assertEqual(record['constraint_violations'],0)

    def test_no_input_baseline_shares_feasible_contract(self):
        r=self.run_policy('no_input')['episode_result']
        self.assertEqual((r['water_mm'],r['nitrogen_kg_ha'],r['sprays'],r['total_cost']),(0,0,0,0))
        mask=np.ones(17,dtype=bool);mask[0]=False
        with self.assertRaises(ValueError):NoInputPolicy().action(np.zeros(OBSERVATION_SIZE),mask)

    def test_pairing_rejects_duplicate_missing_or_different_conditions(self):
        a=self.run_policy('no_input');b=self.run_policy()
        self.assertEqual(verify_pairs([a,b])[0]['common_weather_dates'],2)
        for records in ([a],[a,b,b],[]):
            with self.assertRaises(ValueError):verify_pairs(records)
        wrong=copy.deepcopy(b);wrong['season']['beta']=.6
        with self.assertRaises(ValueError):verify_pairs([a,wrong])

    def test_common_date_weather_and_date_uniqueness_checked(self):
        a=self.run_policy('no_input');b=self.run_policy()
        b['daily_tape'][0]['weather']['rain']=99
        with self.assertRaises(ValueError):verify_pairs([a,b])
        b=copy.deepcopy(a);b['policy']='rule';b['daily_tape'][1]['yrdoy']=b['daily_tape'][0]['yrdoy']
        with self.assertRaises(ValueError):verify_pairs([a,b])

    def test_final_test_split_and_administrative_truncation_refused(self):
        env=CropManagementEnv(pest_enabled=False,backend_factory=FakeBackend)
        self.addCleanup(env.close)
        season=SeasonExogenous('test',33001,0,12345,1,None,np.zeros(400),np.zeros(400))
        with self.assertRaises(ValueError):evaluate_episode(env,NoInputPolicy(),season,ResourceRules(),.158)
        with self.assertRaises(ValueError):self.run_policy(max_days=1)

    def test_corrupt_cost_is_not_hidden_in_successful_summary(self):
        class BadCostEnv(CropManagementEnv):
            def step(self,action):
                o,r,t,x,i=super().step(action);i['cost']+=1;return o,r,t,x,i
        env=BadCostEnv(pest_enabled=False,backend_factory=FakeBackend)
        self.addCleanup(env.close)
        season=SeasonExogenous('validation',22001,0,12345,1,None,np.zeros(400),np.zeros(400))
        with self.assertRaises(ValueError):evaluate_episode(env,NoInputPolicy(),season,ResourceRules(),.158)
        rows=[self.run_policy('no_input'),self.run_policy()]
        self.assertEqual(summarize(rows)['no_input']['failure_rate'],0)


if __name__=='__main__':unittest.main()
