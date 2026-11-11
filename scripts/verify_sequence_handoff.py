"""Run private native maize-to-fallow Q/F harvest and soil handoff probes."""
import argparse
import os
from pathlib import Path
import shutil
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from mars_env.artifacts import new_run, write_json, sha256
from mars_env.sequence_audit import SequenceAuditBackend, analyze_handoff


def normal(value):
    if isinstance(value, dict): return {k: normal(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)): return [normal(v) for v in value]
    return value.tolist() if hasattr(value, 'tolist') else value


def run_case(folder, mode, grain, stover, damage, *, seed=123456, managed=True, fallow_start=None,instrumentation=None,input_transform=None):
    folder.mkdir(parents=True)
    os.environ['MARS_SEQUENCE_MODE'] = mode
    backend = SequenceAuditBackend(grain_percent=grain, stover_percent=stover,fallow_start=fallow_start)
    if input_transform is not None:
        original_transform=backend.filex_transform
        backend.filex_transform=lambda template:input_transform(original_transform(template))
    if instrumentation is not None:backend._instrumentation=instrumentation
    backend._runtime_log_path = str(folder / 'runtime.log')
    trace = []
    try:
        state = backend.reset(seed)
        for _ in range(800):
            trace.append(normal(state))
            active = len(state['mars_sequence_harvests']) == 0
            date, dap = int(state['yrdoy']), int(state['dap'])
            active = active and date >= backend.planting_yrdoy
            water = 10 if managed and active and dap in (10,20,30,40,50,60,70,80) else 0
            nitrogen = {40:27,45:35,80:54}.get(dap, 0) if managed and active else 0
            fraction = damage if active and dap in (30,31,32,33,34) else 0
            state, done, _ = backend.step_damage(water, nitrogen, fraction)
            if done:
                trace.append(normal(state))
                break
        else: raise RuntimeError('Sequence exceeded 800 interaction steps')
        native = backend._env
        source = Path(native._tmp_folder)
        # Copy completed outputs before the upstream close handshake starts another run.
        for p in source.iterdir():
            if p.is_file(): shutil.copy2(p, folder / p.name)
        write_json(folder / 'trace.json', trace)
        backend.close()
        result = {'mode':mode,'seed':seed,'managed':managed,'grain_percent':grain,'stover_percent':stover,'damage':damage,
                  'steps':len(trace)-1,'harvests':normal(state['mars_sequence_harvests']),
                  'soils':normal(state['mars_sequence_soils']),
                  'ear_records':normal(state.get('mars_ear_records',[])),
                  'barrenness_records':normal(state.get('mars_barrenness_records',[])),
                  'files':{p.name:sha256(p) for p in folder.iterdir() if p.is_file()}}
        write_json(folder / 'diagnostics.json', result)
        return result
    finally: backend.close()


if __name__ == '__main__':
    raise SystemExit('Historical unit adapter withdrawn. Run verify_sequence_inventory.py --matrix')
