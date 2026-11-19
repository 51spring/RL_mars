"""Authorized staged execution: wait for b3, freeze, verify, train, test, report.

Run in the DSSAT image with /workspace=project and /workdocs=evidence folder.
No test data is read until all fits and their selected-model ledger are complete.
"""
import argparse
from dataclasses import asdict
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
import run_comparison as c
from report_experiment import render

WORK = Path('/workdocs/outputs/project_execution_20261118')
STATUS = WORK/'execution_status.json'


def state(phase, **values):
    old=json.loads(STATUS.read_text()) if STATUS.exists() else {}
    c.write_json(STATUS,{**old,**values,'phase':phase,'updated_utc':__import__('datetime').datetime.now(
        __import__('datetime').timezone.utc).isoformat()})
    print('PROJECT_PHASE',phase,values,flush=True)


def load(path):
    return json.loads(path.read_text())


def run_logged(command, log_path, phase, run=None):
    started=time.perf_counter()
    with log_path.open('a') as log:
        child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
        while True:
            try:
                return child.wait(timeout=30)
            except subprocess.TimeoutExpired:
                values={'stage_wall_seconds':time.perf_counter()-started}
                if run is not None and phase=='main_training' and (run/'design.json').exists():
                    done=0; steps=0; learn=0; selection=0; storage=0; current=None
                    for fit in load(run/'design.json')['fits']:
                        record=run/f"{fit['label']}_training.json"
                        if record.exists():
                            item=load(record); done+=1
                        else:
                            record=run/f"{fit['label']}_partial.json"
                            if not record.exists(): continue
                            item=load(record); current=fit['label']
                        steps+=item['steps']; learn+=item.get('seconds',0)
                        selection+=item.get('selection_seconds',0); storage+=item.get('storage_seconds',0)
                    values.update(completed_fits=done,training_steps_done=steps,current_fit=current,
                        learn_seconds=learn,selection_seconds=selection,storage_seconds=storage,
                        estimated_training_remaining_seconds=(122880000-steps)*(learn+selection+storage)/steps if steps else None)
                state(phase,**values)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--technical-run',type=Path,required=True)
    args=parser.parse_args()
    run=None
    try:
        state('waiting_b3_selection',technical_run=str(args.technical_run))
        decision_file=WORK/'b3_decision.json'
        while not decision_file.exists():
            partials=list((WORK/'sparse').glob('b3_s*_partial.json'))
            state('waiting_b3_selection',b3_additional_steps_done=sum(max(0,load(p)['steps']-51200) for p in partials),
                  b3_additional_steps_total=897024)
            time.sleep(30)
        decision=load(decision_file)
        assert decision['passed'] and not decision['final_test_split_used']
        technical=load(args.technical_run/'technical_verification.json')
        assert technical['passed'] and not technical['final_test_split_used']
        technical_design=load(args.technical_run/'design.json')
        assert technical_design['image']==os.environ['MARS_IMAGE_ID']
        for relative,expected in technical_design['source_sha256'].items():
            assert c.sha256(c.ROOT/relative)==expected, f'Technical check source changed: {relative}'
        checks=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(c.ROOT/'tests'),'-p','test_*.py'],
            cwd=c.ROOT,capture_output=True,text=True)
        (WORK/'unit_tests.log').write_text(checks.stdout+checks.stderr)
        assert checks.returncode==0, 'Unit tests failed'
        config_path=c.ROOT/'configs/proposal_v2.yaml'
        config=yaml.safe_load(config_path.read_text())
        config['training']['sparse_nonzero_mass']={'irrigation':.13,'nitrogen':.025,'spray':decision['spray_nonzero_mass']}
        config['training']['initialization_status']='frozen'
        config['training']['b3_decision_sha256']=c.sha256(decision_file)
        config['training']['technical_verification_sha256']=c.sha256(args.technical_run/'technical_verification.json')
        config_path.write_text(yaml.safe_dump(config,sort_keys=False),encoding='utf-8')
        plan=c.training_plan(config)
        assert len(plan)==80 and sum(f.steps for f in plan)==122880000
        pointer=WORK/'main_run.json'
        if pointer.exists():
            run=Path(load(pointer)['run'])
            assert c.sha256(run/'config.yaml')==c.sha256(config_path)
        else:
            run=c.new_run(c.ROOT,'main_training_20261118',config_source=config_path)
            c.write_json(pointer,{'run':str(run),'config_sha256':c.sha256(run/'config.yaml')})
        state('main_training',run=str(run),b3_chosen=decision['chosen'],fits=80,total_steps=122880000,
            main_training_started=True)
        runner=run/'source_snapshot/scripts/run_comparison.py'
        train=[sys.executable,str(runner),'--phase','train','--resume',str(run)]
        if not (run/'training_complete.json').exists():
            result=run_logged(train,WORK/'main_training.log','main_training',run)
            assert result==0,'Main training failed; see main_training.log'
        complete=load(run/'training_complete.json')
        assert complete['fits']==80 and complete['total_steps']==122880000
        assert complete['selected_models']=={f.label:c.sha256(c.checkpoint(run,f.label)) for f in plan}
        state('final_test_evaluation',run=str(run),final_test_split_used=True)
        result=run_logged([sys.executable,str(runner),'--phase','evaluate',
            '--evaluation-split','test','--resume',str(run)],WORK/'final_evaluation.log','final_test_evaluation',run)
        assert result==0,'Final evaluation failed; completed season batches are retained'
        verification=load(run/'report_test/verification.json')
        assert verification['passed'] and verification['final_test_split_used']
        state('report_generation',run=str(run))
        result=run_logged([sys.executable,str(run/'source_snapshot/scripts/report_experiment.py'),str(run)],
            WORK/'report_generation.log','report_generation',run)
        assert result==0,'Frozen report generation failed'
        report=run/'report'
        assert len(list(report.glob('learning_*.png')))==8
        state('complete',run=str(run),report=str(report),final_test_complete=True)
    except Exception as exc:
        state('failed',error=f'{type(exc).__name__}: {exc}',run=str(run) if run else None)
        raise


if __name__=='__main__':
    main()
