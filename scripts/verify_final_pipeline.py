"""Small real-DSSAT check of interrupted training, frozen chains and resumable validation."""
from dataclasses import asdict
import json
import os
import subprocess
from pathlib import Path
import sys

import torch
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
import run_comparison as c
from report_experiment import render


def main():
    torch.set_num_threads(1)
    config=yaml.safe_load((c.ROOT/'configs/proposal_v2.yaml').read_text())
    config['training'].update(n_envs=2,n_steps=32,batch_size=64,n_epochs=1,checkpoint_steps=64)
    config['training']['checkpoint_selection'].update(seasons=1,workers=2)
    config['scenarios']['evaluation_workers']=2
    config['scenarios']['bootstrap_replicates']=100
    config['scenarios']['sensitivity_seasons_per_condition']=1
    smoke_config=c.ROOT/'tmp/final_pipeline_smoke.yaml'
    smoke_config.parent.mkdir(exist_ok=True)
    smoke_config.write_text(yaml.safe_dump(config,sort_keys=False))
    run=c.new_run(c.ROOT,'final_pipeline_technical',config_source=smoke_config)
    c.write_json(run/'effective_config.json',config)
    os.environ['MARS_RUN_DIR']=str(run)
    fits=c.training_plan(config,steps=128,seeds=[0])
    original=c.MaskablePPO.learn
    calls=0
    def interrupted(model,*args,**kwargs):
        nonlocal calls
        calls+=1
        if calls==2:
            raise InterruptedError('Intentional technical interruption after first committed checkpoint')
        return original(model,*args,**kwargs)
    c.MaskablePPO.learn=interrupted
    try:
        try:
            c.train(run,config,fits[0])
            raise AssertionError('Interruption was not exercised')
        except InterruptedError:
            state=json.loads((run/f'{fits[0].label}_partial.json').read_text())
            assert state['steps']==64 and state['checkpoint_file']
    finally:
        c.MaskablePPO.learn=original
    for fit in fits:
        c.train(run,config,fit)
        record=json.loads((run/f'{fit.label}_training.json').read_text())
        assert record['steps']==fit.steps
        assert record['frozen_checkpoint_sha256']=={label:c.sha256(c.checkpoint(run,label)) for label,_ in fit.frozen}
    common=['--resume',str(run),'--steps','128','--seeds','0','--seasons','1','--first-season','1700']
    runner=run/'source_snapshot/scripts/run_comparison.py'
    subprocess.run([sys.executable,str(runner),'--phase','train',*common],check=True)
    subprocess.run([sys.executable,str(runner),'--phase','evaluate',*common],check=True)
    rows=c.evaluate_all(run,config,fits,[1700],[0])
    replay=c.evaluate_all(run,config,fits,[1700],[0])
    assert rows==replay
    matrices=c.assemble(rows,[0],[1700])
    checks=c.checks(rows,matrices,c.evaluation_conditions(config))
    assert checks['all_cells_generated'] and checks['a0_equals_b_none_b0'] and checks['resource_violations']==0
    report=render(run)
    c.write_json(run/'technical_verification.json',{'passed':True,'checks':checks,
        'interrupted_and_resumed':True,'cached_evaluation_reproduced':True,
        'fits':len(fits),'steps':sum(f.steps for f in fits),
        'final_test_split_used':False,'report':str(report),
        'technical_overrides':config['training']})
    print('TECHNICAL_PASS',run,flush=True)


if __name__=='__main__':
    main()
