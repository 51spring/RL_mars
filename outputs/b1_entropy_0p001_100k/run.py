"""Only vary b1's entropy coefficient, reusing the matched historical controls."""
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
import importlib.util
import json
from multiprocessing import get_context
import os
from pathlib import Path
from statistics import mean
import sys

import torch
import yaml

RUN = Path(__file__).resolve().parent
RUNS = RUN.parent / 'runs'
PRIOR = RUNS / '20261116T040824Z_b0_b4_ppo_from_scratch'
BASELINE = RUNS / '20261116T133222Z_b1_100352_sparse13_continuation'
ENTROPY_REFERENCE = RUNS / '20261117T065610Z_b1_entropy_001_100352'
INITIALIZER = RUNS / '20261117T060544Z_b1_entropy_001_51200' / 'run_b1.py'
COEF = .001
STAGES = (20_480, 51_200, 100_352)
CONDITIONS = ('none', 'early_40')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def load_script(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def eval_job(job):
    # Workers fork after the archived evaluation module is loaded and configured.
    return evaluator.evaluate(job)


def main():
    global evaluator
    torch.set_num_threads(1)
    initializer = load_script('archived_b1_initialize', INITIALIZER)
    evaluator_path = ENTROPY_REFERENCE / 'run_b1.py'
    evaluator = load_script('archived_b1_evaluate', evaluator_path)
    c = initializer.comparison
    d, baseline = read(PRIOR/'design.json'), read(BASELINE/'design.json')
    config_path = PRIOR/'config.yaml'
    assert c.sha256(config_path) == d['config_sha256'] == baseline['prior_config_sha256']
    assert d['image'] == baseline['image'] == os.environ['MARS_IMAGE_ID']
    assert d['source_sha256'] == baseline['source_sha256']
    for name, sha in d['source_sha256'].items():
        assert c.sha256(Path('/workspace')/name)==sha, name
    assert baseline['initialization_nonzero_probability'] == .13
    assert baseline['checkpoints_compared'] == list(STAGES[1:])
    assert baseline['conditions'] == list(CONDITIONS)
    seeds, seasons = baseline['seeds'], baseline['seasons']
    assert seeds == d['policy_seeds'] and seasons == d['seasons']
    config = yaml.safe_load(config_path.read_text(encoding='utf-8'))
    assert 'sparse_nonzero_mass' not in config['training']
    plan = [f for f in c.training_plan(config,steps=STAGES[-1],seeds=seeds) if f.regime=='b' and f.policy==1]
    controls = {}
    for fit in plan:
        checkpoint = BASELINE/f'{fit.label}_final.zip'
        controls[fit.label] = c.sha256(checkpoint)
        record = read(BASELINE/f'{fit.label}_training.json')
        assert controls[fit.label] == record['final_checkpoint_sha256'] and record['steps'] == STAGES[-1]
    if '--check' in sys.argv:
        print('PREFLIGHT_PASS', len(plan), 'matched seeds', flush=True)
        return
    assert read(RUN.parent/'b3_threshold_100k/results.json')['final_test_split_used'] is False
    protocol = {'coefficient': COEF, 'baseline_coefficient': 0., 'stages': STAGES, 'seeds':seeds,
        'validation_seasons':seasons, 'conditions':CONDITIONS, 'sparse_irrigation':.13,
        'config_sha256':d['config_sha256'], 'source_sha256':d['source_sha256'], 'image':d['image'],
        'control_model_sha256':controls, 'runner_sha256':c.sha256(__file__),
        'initializer_sha256':c.sha256(INITIALIZER), 'evaluator_sha256':c.sha256(evaluator_path),
        'final_test_split_used':False}
    if (RUN/'design.json').exists():
        assert read(RUN/'design.json') == json.loads(json.dumps(protocol))
    else:
        c.write_json(RUN/'design.json',protocol)
    os.environ['MARS_RUN_DIR'] = str(RUN)
    evaluator.RUN, evaluator.BASELINE, evaluator.ENTROPY_COEF = RUN, BASELINE, COEF
    evaluator.EVALUATED_STEPS = (STAGES[-1],)
    initializer.ENTROPY_COEF = COEF
    rows = []
    for fit in plan:
        previous = None
        for step in STAGES:
            work = RUN if step == STAGES[-1] else RUN/f'stage_{step}'
            work.mkdir(exist_ok=True)
            if previous is None:
                initializer.FIRST_STAGE = work
                initializer.initialize(config,fit)
            elif not (work/f'{fit.label}_partial.json').exists():
                initializer.FIRST_STAGE, initializer.RUN = previous, work
                initializer.STEPS = (int(previous.name.split('_')[-1]), step)
                initializer.prepare_fit(fit)
            print('TRAIN', fit.label, COEF, step, flush=True)
            c.train(work,config,replace(fit,steps=step))
            previous = work
        batch = RUN/f'{fit.label}_episodes.json'
        if not batch.exists():
            with ProcessPoolExecutor(max_workers=8,mp_context=get_context('fork')) as pool:
                cases = [row for group in pool.map(eval_job,[(config,fit,s) for s in seasons]) for row in group]
            c.write_json(batch,cases)
        rows.extend(read(batch))
    paired = defaultdict(dict)
    for row in rows:
        assert row['resource_violations'] == 0
        key = row['seed'],row['season'],row['condition']
        assert row['ent_coef'] not in paired[key]
        paired[key][row['ent_coef']] = row
    expected = {(i,s,k) for i in seeds for s in seasons for k in CONDITIONS}
    assert set(paired)==expected and all(set(p)=={0.,COEF} for p in paired.values())
    saved = {(r['seed'],r['season'],r['condition']):r for r in read(BASELINE/'episodes.json') if r['steps']==STAGES[-1]}
    assert set(saved)==expected
    metrics = ('harvested_grain_kg_ha','net_return','water_mm','water_before_day13_mm')
    assert all(paired[k][0.][m]==saved[k][m] for k in expected for m in metrics)
    results = {}
    for condition in CONDITIONS:
        pairs = [p for k,p in paired.items() if k[2]==condition]
        results[condition] = {'control': evaluator.summary([p[0.] for p in pairs],config['environment']['initial_water_mm']),
            'entropy_0.001': evaluator.summary([p[COEF] for p in pairs],config['environment']['initial_water_mm']),
            'delta_0.001_minus_0': {m:mean(p[COEF][m]-p[0.][m] for p in pairs) for m in metrics},
            'delta_by_seed': {seed:{m:mean(p[COEF][m]-p[0.][m] for p in pairs if p[COEF]['seed']==seed)
                                    for m in metrics} for seed in seeds}}
    c.write_json(RUN/'episodes.json',rows)
    c.write_json(RUN/'results.json',{'passed':True,'results':results,'saved_controls_reproduced':True,
                                   'final_test_split_used':False})
    print('B1_COMPLETE',flush=True)


if __name__=='__main__':
    main()
