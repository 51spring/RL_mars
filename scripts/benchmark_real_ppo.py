"""Long diagnostic PPO benchmark, with final-update checkpoints and explicit resume."""
import argparse
from functools import partial
import json
import math
import os
from pathlib import Path
import sys
import time
import torch
import yaml
from sb3_contrib import MaskablePPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.vec_env import SubprocVecEnv

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run, write_json, sha256
from mars_env.exogenous import WEATHER_SEED_VERSION
from mars_env.training_env import SeasonCycler
from smoke_real_ppo import manual_raw_eval


def process_tree():
    entries={}
    for path in Path('/proc').glob('[0-9]*/status'):
        try:
            fields={x.split(':',1)[0]:x.split(':',1)[1].strip() for x in path.read_text().splitlines() if ':' in x}
            entries[int(path.parent.name)]=(int(fields['PPid']),int(fields.get('VmRSS','0 kB').split()[0]))
        except (OSError,KeyError,ValueError): pass
    tree={os.getpid()}
    while True:
        expanded=tree|{pid for pid,(ppid,_) in entries.items() if ppid in tree}
        if expanded==tree: break
        tree=expanded
    return tree,sum(entries.get(pid,(0,0))[1] for pid in tree)


class Audit(BaseCallback):
    def __init__(self):
        super().__init__();self.completed=0;self.max_residual=0.;self.peak_rss_kib=0;self.truncations=0;self.first_season_ids=None
        self.status_path=None;self.start_time=None
    def _on_training_start(self):
        if self.first_season_ids is None:
            self.first_season_ids=[info['external_season_id'] for info in self.training_env.reset_infos]
    def _on_step(self):
        for info in self.locals['infos']:
            if 'reward_audit' in info:
                audit=info['reward_audit']
                assert abs(audit['telescoping_residual'])<1e-5
                self.max_residual=max(self.max_residual,abs(audit['telescoping_residual']))
                self.truncations+=int(audit['administrative_truncation'])
                if audit['complete_episode']:
                    assert math.isclose(audit['raw_return'],info['episode_result']['net_return'],abs_tol=1e-5)
                    self.completed+=1
        if self.n_calls%64==0:
            _,rss=process_tree();self.peak_rss_kib=max(self.peak_rss_kib,rss)
        if self.status_path and self.n_calls%256==0:
            write_json(self.status_path,{'status':'running','model_steps':self.num_timesteps,
                'completed_train_episodes':self.completed,'seconds_since_training_start':time.perf_counter()-self.start_time,
                'peak_tree_rss_mib':self.peak_rss_kib/1024})
        return True


def factory(config,rank,mode,cursor):
    env=SeasonCycler(config,rank=rank,n_envs=4,mode=mode)
    env.set_season_cursor(cursor)
    return env


def main():
    p=argparse.ArgumentParser();p.add_argument('--steps',type=int,default=102400)
    p.add_argument('--mode',choices=['no_pest','experimental_pest'],default='experimental_pest')
    p.add_argument('--device',choices=['cpu','cuda'],default='cpu');p.add_argument('--image-id')
    p.add_argument('--distribution-validation',choices=['enabled','disabled'],default='enabled')
    p.add_argument('--resume',type=Path);args=p.parse_args()
    if args.steps<256 or args.steps%256:p.error('Steps must be positive rollout multiples of 256')
    config_source=args.resume.parent/'config.yaml' if args.resume else ROOT/'configs/proposal_v2.yaml'
    config=yaml.safe_load(config_source.read_text())
    run=new_run(ROOT,f'benchmark_{args.mode}_{args.device}',image_id=args.image_id,config_source=config_source)
    os.environ['MARS_RUN_DIR']=str(run)
    print(f'RUN_DIR={run}',flush=True)
    write_json(run/'status.json',{'status':'starting','target_steps':args.steps})
    cursors=[0]*4;resume=None
    if args.resume:
        resume=json.loads((args.resume/'checkpoint.json').read_text())
        if resume.get('weather_seed_version') != WEATHER_SEED_VERSION:
            raise ValueError('Checkpoint predates the current WGEN allocation; start a new run')
        assert resume['config_sha256']==sha256(config_source),'Checkpoint config snapshot changed'
        assert resume['mode']==args.mode
        previous_report=args.resume.parent/'verification.json'
        previous_options=json.loads(previous_report.read_text()) if previous_report.exists() else {}
        validation=resume.get('distribution_validation',previous_options.get('distribution_validation','enabled'))
        if validation!=args.distribution_validation:
            failure={'passed':False,'error':'Resume must preserve distribution-validation setting',
                     'checkpoint_setting':validation,'requested_setting':args.distribution_validation}
            write_json(run/'failure.json',failure);write_json(run/'status.json',dict(failure,status='failed'))
            raise ValueError(failure['error'])
        cursors=resume['next_season_cursors']
    torch.set_num_threads(1)
    torch.distributions.Distribution.set_default_validate_args(args.distribution_validation=='enabled')
    use_cuda = args.device == 'cuda'
    if use_cuda:
        if not torch.cuda.is_available():
            raise RuntimeError('CUDA inaccessible in learner container')
        torch.cuda.reset_peak_memory_stats()
    train=None;evaluation=None;owned=set();init_start=time.perf_counter();audit=Audit()
    try:
        train=SubprocVecEnv([partial(factory,config,rank,args.mode,cursors[rank]) for rank in range(4)],start_method='spawn')
        cfg=config['training']
        if resume:
            model=MaskablePPO.load(args.resume/'checkpoint.zip',env=train,device=args.device)
            # Policy/optimizer continuation, not bitwise simulator/RNG continuation.
            # Force-reset skips incomplete seasons without replaying their addresses.
        else:
            model=MaskablePPO('MlpPolicy',train,device=args.device,seed=42,gamma=cfg['gamma'],gae_lambda=cfg['gae_lambda'],
                n_steps=64,batch_size=64,n_epochs=2,
                policy_kwargs={'net_arch':{'pi':cfg['policy_layers'],'vf':cfg['value_layers']}},verbose=0)
            with torch.no_grad():
                offset=0
                masses=cfg['sparse_nonzero_mass']
                for count,mass in zip((6,9,2),(masses['irrigation'],masses['nitrogen'],masses['spray'])):
                    model.policy.action_net.weight[offset:offset+count].zero_()
                    model.policy.action_net.bias[offset:offset+count].copy_(torch.tensor([1-mass]+[mass/(count-1)]*(count-1)).log())
                    offset+=count
        initial_steps=model.num_timesteps
        initial_updates=model._n_updates
        initialized=time.perf_counter()-init_start
        learning=0.;checkpoint_seconds=0.;chunks=[]
        audit.status_path=run/'status.json';audit.start_time=time.perf_counter()
        remaining=args.steps
        while remaining:
            chunk=min(25600,remaining)
            if use_cuda:
                torch.cuda.synchronize()
            start=time.perf_counter()
            model.learn(chunk,reset_num_timesteps=False,callback=audit)
            if use_cuda:
                torch.cuda.synchronize()
            learning+=time.perf_counter()-start
            assert all(torch.isfinite(x).all() for x in model.policy.parameters())
            next_cursors=train.env_method('season_cursor')
            start=time.perf_counter()
            # Every checkpoint is written after PPO updates; immutable numbered folder.
            checkpoint=run/f'checkpoint_{model.num_timesteps:09d}';checkpoint.mkdir()
            model.save(checkpoint/'checkpoint')
            write_json(checkpoint/'checkpoint.json',{'mode':args.mode,'config_sha256':sha256(config_source),
                'distribution_validation':args.distribution_validation,
                'weather_seed_version':WEATHER_SEED_VERSION,
                'num_timesteps':model.num_timesteps,'next_season_cursors':next_cursors,
                'resume_semantics':'policy/optimizer continuation; skip incomplete seasons; not bitwise replay'})
            checkpoint_seconds+=time.perf_counter()-start
            remaining-=chunk
            owned.update(process_tree()[0]-{os.getpid()})
            status={'status':'running','steps':model.num_timesteps-initial_steps,'target_steps':args.steps,
                'completed_train_episodes':audit.completed,'learning_seconds':learning,'peak_tree_rss_mib':audit.peak_rss_kib/1024,
                'checkpoint':str(checkpoint),'next_season_cursors':next_cursors}
            chunks.append(status);write_json(run/'status.json',status);print(json.dumps(status),flush=True)
        start=time.perf_counter()
        loaded=MaskablePPO.load(checkpoint/'checkpoint.zip',device=args.device)
        evaluation=SeasonCycler(config,rank=0,n_envs=1,split='validation',mode=args.mode,shaping=False)
        evaluation_results=manual_raw_eval(loaded,evaluation)
        eval_seconds=time.perf_counter()-start
        assert audit.completed>0 and audit.truncations==0
        report={'passed':True,'diagnostic_only':True,'research_ready':False,'mode':args.mode,'device':args.device,
            'distribution_validation':args.distribution_validation,
            'steps':model.num_timesteps-initial_steps,'n_envs':4,'ppo_updates':model._n_updates-initial_updates,
            'cumulative_ppo_updates':model._n_updates,'first_season_ids':audit.first_season_ids,
            'initialization_seconds':initialized,'learning_seconds':learning,'checkpoint_seconds':checkpoint_seconds,
            'evaluation_seconds':eval_seconds,'steps_per_second':args.steps/learning,
            'peak_process_tree_rss_mib':audit.peak_rss_kib/1024,'completed_train_episodes':audit.completed,
            'peak_learner_cuda_allocated_mib':torch.cuda.max_memory_allocated()/2**20 if use_cuda else None,
            'peak_learner_cuda_reserved_mib':torch.cuda.max_memory_reserved()/2**20 if use_cuda else None,
            'truncations':audit.truncations,'max_reward_residual':audit.max_residual,
            'invalid_action_exceptions':0,'backend_errors':0,'raw_validation_results':evaluation_results,
            'resumed_from':str(args.resume) if args.resume else None,'chunks':chunks}
    except BaseException as exc:
        failure={'passed':False,'error':repr(exc),'completed_train_episodes':audit.completed,
                 'model_steps':model.num_timesteps if 'model' in locals() else 0}
        write_json(run/'failure.json',failure)
        write_json(run/'status.json',dict(failure,status='failed'))
        raise
    finally:
        if train is not None:train.close()
        if evaluation is not None:evaluation.close()
        deadline=time.monotonic()+5
        while any(Path(f'/proc/{pid}').exists() for pid in owned) and time.monotonic()<deadline:time.sleep(.05)
    # multiprocessing's shared resource_tracker lives until interpreter exit;
    # remaining process names identify it explicitly rather than claiming all children vanished.
    surviving={pid:Path(f'/proc/{pid}/cmdline').read_bytes().decode(errors='replace').replace('\0',' ')
               for pid in owned if Path(f'/proc/{pid}/cmdline').exists()}
    forbidden={pid:cmd for pid,cmd in surviving.items() if 'resource_tracker' not in cmd}
    report['simulator_workers_cleaned_up']=not forbidden
    report['remaining_infrastructure_children']=surviving
    assert not forbidden,forbidden
    write_json(run/'verification.json',report);write_json(run/'status.json',{'status':'complete','steps':args.steps})
    print(json.dumps({k:report[k] for k in ('passed','steps','steps_per_second','completed_train_episodes','simulator_workers_cleaned_up')}),flush=True)


if __name__=='__main__':main()
