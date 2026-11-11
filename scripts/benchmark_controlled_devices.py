"""Audit archived device evidence and run counterbalanced same-image pilots."""
import argparse
from collections import defaultdict
import json
import os
from pathlib import Path
from statistics import geometric_mean
import subprocess
import sys
import zipfile

import torch
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from mars_env.artifacts import new_run, sha256, write_json

ARCHIVE = {
    'cpu': '20261105T131819Z_benchmark_experimental_pest_cpu_ab616534',
    'cuda': '20261105T140204Z_benchmark_experimental_pest_cuda_7da9d805',
}
PARAMETERS = ('gamma', 'gae_lambda', 'n_steps', 'batch_size', 'n_epochs', 'n_envs', 'seed', 'learning_rate')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def checkpoint_parameters(folder):
    with zipfile.ZipFile(sorted(folder.glob('checkpoint_*/checkpoint.zip'))[-1]) as archive:
        model = json.loads(archive.read('data'))
    return {key: model[key] for key in PARAMETERS}


def archive_audit():
    summary, configs = {}, {}
    for device, name in ARCHIVE.items():
        folder = ROOT / 'outputs/runs' / name
        result = read(folder / 'verification.json')
        manifest = read(folder / 'manifest.json')
        assert result['passed'] and result['steps'] == 102400
        configs[device] = yaml.safe_load((folder / 'config.yaml').read_text())
        summary[device] = {
            'verification': (folder / 'verification.json').relative_to(ROOT).as_posix(),
            'verification_sha256': sha256(folder / 'verification.json'),
            'config_sha256': sha256(folder / 'config.yaml'),
            'image_id': manifest['image_id'],
            'benchmark_source_sha256': manifest['source_sha256']['scripts/benchmark_real_ppo.py'],
            'distribution_validation_reported': result.get('distribution_validation'),
            'checkpoint_parameters': checkpoint_parameters(folder),
            'steps_per_second': result['steps_per_second'],
            'host_load_context': ('overlapped image builds and diagnostics' if device == 'cpu'
                                  else 'separate run with low initial GPU utilization'),
        }
    assert summary['cpu']['checkpoint_parameters'] == summary['cuda']['checkpoint_parameters']
    differing_sections = [key for key in sorted(configs['cpu'].keys() | configs['cuda'].keys())
                          if configs['cpu'].get(key) != configs['cuda'].get(key)]
    return {'archives': summary, 'differing_config_sections': differing_sections,
            'controlled_speed_comparison': False}


def gpu_snapshot():
    query = 'utilization.gpu,memory.used,memory.total,temperature.gpu,driver_version'
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=' + query, '--format=csv,noheader,nounits'],
                                capture_output=True, text=True, timeout=8)
    except (OSError, subprocess.TimeoutExpired) as error:
        return {'error': str(error)}
    if result.returncode:
        return {'error': result.stderr.strip() or f'exit {result.returncode}'}
    return {'fields': query.split(','), 'samples': [line.split(', ') for line in result.stdout.splitlines()]}


def launch(device, steps, image_id):
    initial_gpu = gpu_snapshot()
    command = [sys.executable, '-u', str(ROOT / 'scripts/benchmark_real_ppo.py'),
               '--mode', 'experimental_pest', '--device', device, '--steps', str(steps),
               '--distribution-validation', 'enabled', '--image-id', image_id]
    folder = None
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as process:
        for line in process.stdout:
            print(line, end='', flush=True)
            if line.startswith('RUN_DIR='):
                folder = Path(line.removeprefix('RUN_DIR=').strip())
        code = process.wait()
    if code or folder is None:
        raise RuntimeError(f'{device} benchmark failed (exit {code}, run directory {folder})')
    result = read(folder / 'verification.json')
    manifest = read(folder / 'manifest.json')
    assert manifest['image_id'] == image_id and result['device'] == device
    assert result['passed'] and result['steps'] == steps and result['ppo_updates'] == steps // 128
    assert result['distribution_validation'] == 'enabled' and result['resumed_from'] is None
    assert result['simulator_workers_cleaned_up'] and result['n_envs'] == 4
    assert all(result[key] == 0 for key in ('invalid_action_exceptions', 'backend_errors', 'truncations'))
    metrics = ('initialization_seconds', 'learning_seconds', 'checkpoint_seconds', 'evaluation_seconds',
               'steps_per_second', 'peak_process_tree_rss_mib', 'peak_learner_cuda_allocated_mib',
               'peak_learner_cuda_reserved_mib', 'completed_train_episodes', 'ppo_updates')
    return {'device': device, 'run': folder.relative_to(ROOT).as_posix(),
            'verification_sha256': sha256(folder / 'verification.json'),
            'config_sha256': manifest['effective_config_sha256'],
            'benchmark_source_sha256': manifest['source_sha256']['scripts/benchmark_real_ppo.py'],
            'first_season_ids': result['first_season_ids'], 'parameters': checkpoint_parameters(folder),
            'gpu_before': initial_gpu, 'gpu_after': gpu_snapshot(),
            **{key: result[key] for key in metrics}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--steps', type=int, choices=[1024, 102400], default=1024)
    args = parser.parse_args()
    image_id = os.environ['MARS_IMAGE_ID']
    if not torch.cuda.is_available() or os.environ.get('MARS_CANONICAL_UFGA_METADATA') != '1':
        raise RuntimeError('Require the metadata-corrected CUDA image with a visible GPU')
    run = new_run(ROOT, 'controlled_device_pair', image_id=image_id)
    print(f'PAIR_DIR={run}', flush=True)
    runs = []
    write_json(run / 'archive_audit.json', archive_audit())
    try:
        for device in ('cpu', 'cuda', 'cuda', 'cpu'):
            entry = launch(device, args.steps, image_id)
            runs.append(entry)
            write_json(run / 'sequence.json', {'runs': runs})
        for key in ('config_sha256', 'benchmark_source_sha256', 'first_season_ids', 'parameters'):
            assert all(r[key] == runs[0][key] for r in runs), key
        rates = defaultdict(list)
        for result in runs:
            rates[result['device']].append(result['steps_per_second'])
        pair_ratios = [runs[0]['steps_per_second'] / runs[1]['steps_per_second'],
                       runs[3]['steps_per_second'] / runs[2]['steps_per_second']]
        report = {'passed': True, 'scope': 'diagnostic throughput only', 'image_id': image_id,
                  'torch': torch.__version__, 'cuda_runtime': torch.version.cuda,
                  'gpu_name': torch.cuda.get_device_name(),
                  'steps_per_run': args.steps, 'runs': runs, 'rates': dict(rates),
                  'cpu_over_cuda_ratio_by_block': pair_ratios,
                  'cpu_over_cuda_ratio_geometric_mean': geometric_mean(pair_ratios),
                  'long_controlled_cpu_gpu_comparison_complete': args.steps == 102400,
                  'research_ready': False, 'main_training_allowed': False}
        write_json(run / 'verification.json', report)
        print(json.dumps({'steps_per_run': args.steps, 'rates': dict(rates), 'ratios': pair_ratios}), flush=True)
    except BaseException as error:
        write_json(run / 'failure.json', {'passed': False, 'error': repr(error), 'completed': runs})
        raise


if __name__ == '__main__':
    main()
