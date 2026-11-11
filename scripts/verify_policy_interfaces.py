"""Actual irrigation-only MaskablePPO and shared rule policy diagnostic."""
from functools import partial
import json
from pathlib import Path
import sys
import torch
import yaml
from sb3_contrib import MaskablePPO
from stable_baselines3.common.vec_env import SubprocVecEnv
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json
from mars_env.training_env import SeasonCycler
from mars_env.policies import RulePolicy,IrrigationOnly


def factory(config,rank):
    return IrrigationOnly(SeasonCycler(config,rank=rank,n_envs=4,mode='experimental_pest'),RulePolicy())


def main():
    config=yaml.safe_load((ROOT/'configs/proposal_v2.yaml').read_text())
    run=new_run(ROOT,'policy_interfaces');torch.set_num_threads(1)
    train=SubprocVecEnv([partial(factory,config,i) for i in range(4)],start_method='spawn')
    reports={}
    try:
        model=MaskablePPO('MlpPolicy',train,seed=42,n_steps=64,batch_size=64,n_epochs=2,gamma=1,
            policy_kwargs={'net_arch':{'pi':[256,256],'vf':[256,256]}},device='cpu',verbose=0)
        model.learn(1024);model.save(run/'irrigation_only')
        loaded=MaskablePPO.load(run/'irrigation_only.zip',device='cpu')
        for policy in ('no_input','rule','irrigation_only'):
            base=SeasonCycler(config,rank=0,n_envs=1,split='validation',mode='experimental_pest',shaping=False)
            env=IrrigationOnly(base,RulePolicy()) if policy=='irrigation_only' else base
            try:
                obs,info=env.reset();total=0
                for step in range(240):
                    mask=env.action_masks()
                    if policy=='irrigation_only':action,_=loaded.predict(obs,deterministic=True,action_masks=mask)
                    elif policy=='rule':action=RulePolicy().action(obs,mask)
                    else:action=[0,0,0]
                    obs,reward,terminated,truncated,info=env.step(action);total+=reward
                    if terminated or truncated:
                        assert terminated and not truncated
                        assert abs(total-info['episode_result']['net_return'])<1e-6
                        reports[policy]=info['episode_result'];break
                else:raise RuntimeError('Evaluation did not terminate')
            finally:env.close()
        write_json(run/'verification.json',{'passed':True,'diagnostic_only':True,'research_ready':False,
            'irrigation_action_n':6,'joint_action_nvec':[6,9,2],'steps':model.num_timesteps,
            'ppo_updates':model._n_updates,'raw_validation':reports,'thresholds_tuned':False,
            'note':'Fixed diagnostic rule settings; no claim of baseline strength or policy superiority'})
        print(run);print(json.dumps(reports))
    finally:train.close()


if __name__=='__main__':main()
