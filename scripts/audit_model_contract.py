"""Native calendar/input/output audit with immutable raw evidence."""
import argparse
from dataclasses import asdict
import json
from pathlib import Path
import shutil
import sys
import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from mars_env.artifacts import new_run, write_json, sha256
from mars_env.audits import enable_audit_outputs, weather_rows, shift_yrdoy, verify_completed_weather, management_events
from mars_env.dssat_backend import DssatBackend
from mars_env.environment import CropManagementEnv
from mars_env.experimental_env import ExperimentalPestEnv
from mars_env.exogenous import generate_season
from mars_env.resources import WaterShock
from mars_env.online_pests import ExperimentalOnlineBackend
from mars_env.pests import PestParameters
from mars_env.observations import FIELDS


def normal(value):
    return value.tolist() if hasattr(value, 'tolist') else value


def collect_case(folder, *, diagnostic, managed, seed=123456, outputs=True):
    folder.mkdir()
    config = yaml.safe_load((ROOT/'configs/proposal_v2.yaml').read_text())
    season = generate_season(config, split='validation', season_id=0).with_condition(
        beta=1, shock=WaterShock(1, 0, .4))
    if diagnostic:
        backend = ExperimentalOnlineBackend(parameters=PestParameters(10,30), noise_std=.01, season=season)
        backend.filex_transform = enable_audit_outputs if outputs else None
        env = ExperimentalPestEnv(season=season, parameters=PestParameters(10,30), noise_std=.01,
                                  backend_factory=lambda **kwargs: backend)
    else:
        backend = DssatBackend(filex_transform=enable_audit_outputs if outputs else None)
        env = CropManagementEnv(pest_enabled=False, backend_factory=lambda **kwargs: backend)
    preplant = []
    original_step = backend.step
    def record_step(*args):
        before = dict(backend.state)
        result = original_step(*args)
        preplant.append({'before':before,'after':dict(result[0]),'water':args[0],'nitrogen':args[1], 'done':result[1]})
        return result
    if not diagnostic:
        backend.step = record_step
    trace = []
    try:
        obs, info = env.reset(seed=seed, options=None if diagnostic else {'season':season})
        preplant_only = list(preplant)
        for day in range(240):
            before = dict(env.state)
            current_obs = obs.copy()
            # Known management pulses, constrained by the exact public mask.
            wanted = [2 if day in (0,15,30,45) else 0,
                      {40:3,45:4,80:6}.get(day,0),
                      int(diagnostic and day in (28,42))] if managed else [0,0,0]
            mask = env.action_masks()
            action = [v if mask[offset+v] else 0 for offset,v in zip((0,6,15),wanted)]
            before_ledger = env.ledger
            obs, reward, terminated, truncated, result = env.step(action)
            after = dict(env.state)
            trace.append({'day':day,'decision_date':int(before['yrdoy']),
                'completed_date':int(before['yrdoy']), 'returned_date':int(after['yrdoy']),
                'before':before,'after':after,'latest_policy_frame':current_obs[-len(FIELDS):].tolist(),
                'action_indices':action,'action':asdict(env.previous_action),
                'announcement':before_ledger.announcement(), 'reward':reward,
                'terminated':terminated,'truncated':truncated})
            if terminated or truncated:
                assert terminated and not truncated
                break
        native = backend._env
        source = Path(native._tmp_folder)
        # Finish the supported legacy close handshake so Fortran buffers flush.
        # Preserve this one native temporary directory until evidence is copied.
        native.close(_close_tmp=False)
        for path in source.iterdir():
            if path.is_file() and (path.suffix.upper() in ('.OUT','.MZX') or path.name.endswith('.yml')):
                shutil.copy2(path, folder/path.name)
        # Preserve actual scenario inputs without modifying installed data.
        for path in (Path('/opt/dssat_pdi/Soil/SOIL.SOL'),Path('/opt/dssat_pdi/Weather/UFGA8201.WTH')):
            if path.exists(): shutil.copy2(path,folder/path.name)
        native._close_tmp_folder()
        rows = weather_rows((folder/'Weather.OUT').read_text()) if outputs else {}
        checks = []
        for entry in preplant_only if outputs else []:
            checks.append(verify_completed_weather(entry['after'], entry['before']['yrdoy'],rows))
        for entry in trace:
            completed = entry['completed_date']
            expected = completed if entry['terminated'] else shift_yrdoy(completed,1)
            assert entry['returned_date'] == expected, 'Returned date convention changed'
            if outputs:
                checks.append(verify_completed_weather(entry['after'],completed,rows))
                checks.append(verify_completed_weather(entry['before'],shift_yrdoy(completed,-1),rows))
            for key in ('rain','tmax','srad'):
                index, scale = next((i,scale) for i,(name,scale) in enumerate(FIELDS) if name==key)
                assert np.isclose(entry['latest_policy_frame'][index]*scale,entry['before'][key],atol=1e-5)
        if outputs:
            actual=sorted(management_events((folder/'MgmtEvent.OUT').read_text()))
            expected=sorted((e['decision_date'],operation,float(e['action'][key]))
                for e in trace for key,operation in [('water_mm','Irrigation'),('nitrogen_kg_ha','Fertilizer')]
                if e['action'][key]>0)
            assert actual==expected,(actual,expected)
        # Audit output switches must not change weather/crop states; compare paired cases outside.
        write_json(folder/'timeline.json', json.loads(json.dumps({'preplant':preplant_only,'policy':trace},default=normal)))
        files = {p.name:{'bytes':p.stat().st_size,'sha256':sha256(p)} for p in folder.iterdir() if p.is_file()}
        return {'passed':True,'steps':len(trace),'preplant_steps':info['preplant_days'],
            'weather_comparisons':len(checks),'weather_tolerance':.05001,
            'planting_date':backend.planting_yrdoy,'emergence_dates':sorted({e['completed_date'] for e in trace if e['before']['vstage']==0 and e['after']['vstage']>0}),
            'announcement_days':[e['day'] for e in trace if e['announcement']['announced'] and e['announcement']['days_since']==0],
            'survey_days':[e['day'] for e in trace if diagnostic and e['before']['mars_pest_public']['survey_age']==0],
            'management_events_matched':len(actual) if outputs else None,
            'final_result':result['episode_result'],'files':files}
    finally:
        env.close()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--image-id');args=parser.parse_args()
    run=new_run(ROOT,'model_contract',image_id=args.image_id)
    print(f'RUN_DIR={run}',flush=True)
    try:
        cases={}
        for diagnostic in (False,True):
            name='experimental_pest' if diagnostic else 'no_pest'
            cases[name]=collect_case(run/name,diagnostic=diagnostic,managed=True)
            cases[name+'_control']=collect_case(run/(name+'_control'),diagnostic=diagnostic,managed=True,outputs=False)
            first=json.loads((run/name/'timeline.json').read_text())['policy']
            second=json.loads((run/(name+'_control')/'timeline.json').read_text())['policy']
            assert first==second,'Output controls changed the native crop/policy trajectory'
            cases[name]['audit_output_trajectory_exact']=True
        write_json(run/'verification.json',{'passed':True,'cases':cases,'research_ready':False,
            'whole_system_balance_validated':False})
        print(json.dumps({name:{k:v for k,v in case.items() if k!='files'} for name,case in cases.items()},indent=2))
    except BaseException as exc:
        write_json(run/'failure.json',{'error':repr(exc),'passed':False})
        raise


if __name__=='__main__': main()
