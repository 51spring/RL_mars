"""Keep long stability evidence separate from matched short device measurements."""
import json
from pathlib import Path
import sys
import zipfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256


def main():
    reports=[];aborted=[]
    for path in sorted((ROOT/'outputs/runs').glob('*benchmark*/verification.json')):
        data=json.loads(path.read_text());reports.append((path,data))
    for path in sorted((ROOT/'outputs/runs').glob('*benchmark*/abort_note.json')):
        aborted.append({'path':str(path.relative_to(ROOT)),'sha256':sha256(path),'details':json.loads(path.read_text())})
    short={}
    for path,data in reports:
        if data['steps']==1024 and not data.get('resumed_from') and data.get('distribution_validation')=='disabled':
            short[data['device']]=(path,data)
    assert {'cpu','cuda'}<=short.keys()
    params={}
    for device,(path,data) in short.items():
        assert data['passed'] and data['simulator_workers_cleaned_up']
        checkpoint=next(path.parent.glob('checkpoint_*/checkpoint.zip'))
        with zipfile.ZipFile(checkpoint) as archive:model=json.loads(archive.read('data'))
        params[device]={k:model[k] for k in ('gamma','gae_lambda','n_steps','batch_size','n_epochs','n_envs','seed','learning_rate')}
    assert params['cpu']==params['cuda']
    assert short['cpu'][1]['first_season_ids']==short['cuda'][1]['first_season_ids']
    run=new_run(ROOT,'benchmark_summary')
    comparison={device:{'path':str(path.relative_to(ROOT)),'sha256':sha256(path),
        'steps':d['steps'],'learning_seconds':d['learning_seconds'],'steps_per_second':d['steps_per_second'],
        'initialization_seconds':d['initialization_seconds'],'evaluation_seconds':d['evaluation_seconds'],
        'peak_process_tree_rss_mib':d['peak_process_tree_rss_mib']} for device,(path,d) in short.items()}
    long=[{'path':str(path.relative_to(ROOT)),'sha256':sha256(path),'steps':d['steps'],
        'device':d['device'],'steps_per_second':d['steps_per_second'],
        'completed_seasons':d['completed_train_episodes'],'updates':d['ppo_updates']}
        for path,d in reports if d['steps']>=102400 and not d.get('resumed_from')]
    write_json(run/'verification.json',{'passed':True,'diagnostic_only':True,'research_ready':False,
        'matched_short_comparison':comparison,'matched_hyperparameters':params['cpu'],
        'distribution_validation':'disabled; project feasibility/ledger checks remain enabled',
        'cpu_over_cuda_short_speed_ratio':comparison['cpu']['steps_per_second']/comparison['cuda']['steps_per_second'],
        'long_stability':long,'aborted_runs':aborted,'default_device':'cpu',
        'long_controlled_cpu_gpu_comparison_complete':False,
        'limitation':'CPU long run overlapped builds/diagnostics. Matched device runs are short, single replicate. GPU long default-validation run was interrupted; no final policy ranking.'})
    print(run);print(json.dumps(comparison,indent=2))


if __name__=='__main__':main()
