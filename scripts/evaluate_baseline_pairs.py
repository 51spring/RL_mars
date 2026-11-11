"""Short no-pest baseline pipeline diagnostic, never threshold selection."""
import argparse
from dataclasses import asdict
import os
from pathlib import Path
import sys
import time
import yaml
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.baseline_evaluation import evaluate_episode,verify_pairs,summarize
from mars_env.environment import CropManagementEnv
from mars_env.exogenous import generate_season
from mars_env.policies import RulePolicy,NoInputPolicy
from mars_env.process_backend import LegacyProcessBackend
from mars_env.resources import ResourceRules


def live_children():
    entries={}
    for path in Path('/proc').glob('[0-9]*/status'):
        try:
            fields={line.split(':',1)[0]:line.split(':',1)[1].strip()
                    for line in path.read_text().splitlines() if ':' in line}
            entries[int(path.parent.name)]=(int(fields['PPid']),fields['State'],fields['Name'])
        except (OSError,KeyError,ValueError):pass
    owned={os.getpid()}
    while True:
        expanded=owned|{pid for pid,(parent,_,_) in entries.items() if parent in owned}
        if expanded==owned:break
        owned=expanded
    return [{'pid':pid,'name':entries[pid][2]} for pid in sorted(owned-{os.getpid()})
            if not entries[pid][1].startswith('Z')]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--seasons',type=int,default=4)
    args=parser.parse_args()
    if not 1<=args.seasons<=16:parser.error('Diagnostic requires 1..16 validation seasons')
    config=yaml.safe_load((ROOT/'configs/proposal_v2.yaml').read_text())
    if os.environ.get('MARS_CANONICAL_UFGA_METADATA')!='1':
        raise RuntimeError('Use the corrected metadata image')
    run=new_run(ROOT,'baseline_pairs_no_pest');os.environ['MARS_RUN_DIR']=str(run)
    print('RUN_DIR='+str(run),flush=True)
    rules=ResourceRules.from_config(config);records=[];start=time.perf_counter()
    policies={'no_input':NoInputPolicy(),'rule':RulePolicy(baseline_nitrogen=tuple(
        sorted(config['management']['baseline_nitrogen'].items())))}
    write_json(run/'policies.json',{name:asdict(policy) for name,policy in policies.items()})
    try:
        for season_id in range(args.seasons):
            season=generate_season(config,split='validation',season_id=season_id)
            for name,policy in policies.items():
                env=CropManagementEnv(pest_enabled=False,rules=rules,
                    grain_price=config['economics']['grain_usd_kg'],backend_factory=LegacyProcessBackend)
                try:
                    record=evaluate_episode(env,policy,season,rules,config['economics']['grain_usd_kg'])
                    record['policy']=name
                    write_json(run/f'{name}_season_{season_id}.json',record);records.append(record)
                finally:env.close()
            write_json(run/'status.json',{'status':'running','completed_pairs':season_id+1})
        checks=verify_pairs(records)
        alive=live_children()
        if alive:raise RuntimeError('Owned child processes remain: '+str(alive))
        report={'passed':True,'scope':'no-pest paired baseline technical diagnostic only',
            'mode':'no_pest','validation_pairs':len(checks),'native_seasons':len(records),
            'weather_pairing':checks,'summary':summarize(records),
            'constraint_violations':sum(r['constraint_violations'] for r in records),
            'episode_files':{f'{r["policy"]}_season_{r["season"]["season_id"]}.json':sha256(
                run/f'{r["policy"]}_season_{r["season"]["season_id"]}.json') for r in records},
            'policy_config_sha256':sha256(run/'policies.json'),'seconds':time.perf_counter()-start,
            'owned_live_children_after_close':alive,'thresholds_tuned':False,
            'final_test_split_used':False,'policy_superiority_tested':False,
            'research_ready':False,'main_training_allowed':False}
        write_json(run/'verification.json',report)
        write_json(run/'status.json',{'status':'passed','completed_pairs':len(checks)})
        print(run,flush=True)
    except Exception as exc:
        write_json(run/'failure.json',{'passed':False,'error':str(exc),'completed_episodes':len(records)})
        write_json(run/'status.json',{'status':'failed','error':str(exc)})
        raise


if __name__=='__main__':main()
