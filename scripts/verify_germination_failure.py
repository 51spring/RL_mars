"""Native dry germination failure; isolated container weather, no model edits."""
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import psutil

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from mars_env.artifacts import new_run, write_json, sha256
from mars_env.dssat_backend import DssatBackend
from mars_env.environment import CropManagementEnv
from verify_sequence_handoff import normal


def dry_filex(template):
    lines = template.splitlines()
    for i, line in enumerate(lines):
        if line.startswith('@C  ICBL'):
            j = i + 1
            while j < len(lines) and lines[j].strip() and not lines[j].startswith(('@', '*', '!')):
                row = lines[j]
                spans = list(re.finditer(r'\S+', row))
                # Diagnostic water below all profile lower limits; keep N unchanged.
                a, b = spans[1].end(), spans[2].end()
                lines[j] = row[:a] + '.010'.rjust(b-a) + row[b:]
                j += 1
        if line.startswith('@N METHODS'):
            row = lines[i+1]
            spans = list(re.finditer(r'\S+', row))
            s = spans[2]
            assert s.group() == 'W'
            lines[i+1] = row[:s.start()] + 'M' + row[s.end():]
    result = '\n'.join(lines) + '\n'
    assert result != template
    return result


def dry_weather(text):
    lines = text.splitlines()
    count = 0
    for i, row in enumerate(lines):
        if re.match(r'^\d{5}\s', row):
            spans = list(re.finditer(r'\S+', row))
            a, b = spans[3].end(), spans[4].end()
            lines[i] = row[:a] + '0.0'.rjust(b-a) + row[b:]
            count += 1
    assert count == 365
    return '\n'.join(lines) + '\n'


def run_case(folder, launcher, rescue):
    folder.mkdir(parents=True)
    env = CropManagementEnv(pest_enabled=False, backend_factory=lambda **kw:
        DssatBackend(filex_transform=dry_filex, run_dssat_location=str(launcher), **kw))
    trace, actions, owned = [], [], []
    result = None
    try:
        obs, reset_info = env.reset(seed=123456)
        assert obs.shape == env.observation_space.shape
        trace.append(normal(env.state))
        native = psutil.Process(env.backend._env._client_process_pid)
        owned = native.children(recursive=True) + [native]
        for day in range(240):
            # Paid N without water preserves the germination failure trigger.
            action = [4 if rescue else 0, 1, 0] if day == 0 else [0, 0, 0]
            before = int(env.state['yrdoy'])
            _, reward, terminated, truncated, info = env.step(action)
            trace.append(normal(env.state))
            actions.append(dict(date=before, action=action, reward=reward, info=info))
            if terminated or truncated:
                break
        assert terminated and not truncated
        result = info['episode_result']
        warning = (Path(env.backend._env._tmp_folder)/'WARNING.OUT').read_text()
        assert all(float(s['rain']) == 0 for s in trace)
        if rescue:
            assert 'lack of germination' not in warning.lower()
            assert any(int(s['istage']) in (1, 2, 3, 4, 5) for s in trace)
        else:
            assert result['reason'] == 'crop_failure'
            assert 'crop failure because of lack of germination' in warning.lower()
            assert 'deep planting' not in warning.lower()
            assert result['harvested_grain_kg_ha'] == 0 and info['revenue'] == 0
            assert result['total_cost'] > 0 and result['water_mm'] == 0
            assert abs(sum(a['reward'] for a in actions)+result['total_cost']) < 1e-8
        assert abs(sum(a['reward'] for a in actions)-result['net_return']) < 1e-8
        return dict(passed=True, rescue=rescue, steps=len(actions), terminal_date=int(env.state['yrdoy']),
                    episode_result=result, sum_raw_rewards=sum(a['reward'] for a in actions),
                    first_emerged_date=next((int(s['yrdoy']) for s in trace if 1 <= int(s['istage']) <= 5),None))
    finally:
        if env.backend._env is not None:
            for p in Path(env.backend._env._tmp_folder).iterdir():
                if p.is_file(): shutil.copy2(p, folder/p.name)
        write_json(folder/'trace.json', trace)
        write_json(folder/'actions.json', actions)
        env.close()
        alive = [p.pid for p in owned if p.is_running()]
        write_json(folder/'cleanup.json', {'owned_pids':[p.pid for p in owned], 'alive_after_close':alive})
        if alive: raise RuntimeError('Owned native processes survived close')


def main():
    os.environ.update(GFORTRAN_UNBUFFERED_ALL='y', MARS_CANONICAL_UFGA_METADATA='1')
    run = new_run(ROOT, 'germination_failure')
    print('RUN_DIR='+str(run), flush=True)
    shutil.copy2('/opt/dssat_pdi/Genotype/MZCER048.SPE', run/'species_capture.SPE')
    shutil.copy2('/build/source/Plant/CERES-Maize/MZ_PHENOL.for', run/'phenol_capture.for')
    weather = Path('/opt/dssat_pdi/Weather/UFGA8201.WTH')
    original = weather.read_bytes()
    (run/'original_UFGA8201.WTH').write_bytes(original)
    modified = dry_weather(original.decode('latin-1'))
    (run/'dry_UFGA8201.WTH').write_text(modified)
    cases = []
    try:
        # Root-owned disposable container only. Restore even on diagnostic failure.
        weather.write_text(modified)
        with tempfile.TemporaryDirectory(prefix='mars_dry_') as tmp:
            for label, binary in (('control','mars_ear_audit_dscsm048'),
                                  ('candidate','mars_actual_harvest_dscsm048')):
                launcher = Path(tmp)/label
                launcher.write_text('#!/bin/sh\nexec /opt/dssat_pdi/'+binary+' "$@"\n')
                launcher.chmod(0o755)
                for rescue in (False, True):
                    name = label + ('_rescue' if rescue else '_dry')
                    result = run_case(run/name, launcher, rescue)
                    result.update(name=name, binary_sha256=sha256('/opt/dssat_pdi/'+binary))
                    cases.append(result)
                    print(name+' passed',flush=True)
        # Different harvest patches must not alter these failure/rescue outcomes.
        for rescue in (False, True):
            a,b = [c for c in cases if c['rescue']==rescue]
            assert a['episode_result']==b['episode_result'] and a['terminal_date']==b['terminal_date']
        indexes = {p.relative_to(run).as_posix():sha256(p) for p in run.rglob('*')
                   if p.is_file() and 'source_snapshot' not in p.parts}
        write_json(run/'source_files.json', indexes)
        write_json(run/'verification.json', dict(passed=True, native_runs=4, cases=cases,
            seed=123456, weather='observed UFGA8201 with RAIN=0, other columns unchanged',
            initial_water='.010 cm3/cm3 all IC layers; native effective states retained',
            planting_depth_cm=7, paid_failure_action='10kgN/ha, no irrigation on first policy day',
            owned_children_after_close=0, research_ready=False, main_training_allowed=False,
            scope='native dry germination termination, raw accounting and irrigation emergence control; not agronomic calibration'))
    except Exception as exc:
        write_json(run/'failure.json',dict(passed=False,exception=repr(exc),completed_cases=cases,research_ready=False))
        raise
    finally:
        weather.write_bytes(original)


if __name__=='__main__': main()
