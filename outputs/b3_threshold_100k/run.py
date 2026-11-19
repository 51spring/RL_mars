"""Matched b3 pilot: learn spray timing under fixed or selectable survey thresholds."""
from concurrent.futures import ProcessPoolExecutor
from functools import partial
import json
from multiprocessing import get_context
import os
from pathlib import Path
from statistics import mean
import sys
import time

import gymnasium as gym
import numpy as np
import torch
import yaml

sys.path.insert(0, '/workspace/scripts')
import run_comparison as c
from mars_env.observations import FIELDS

HERE = Path(__file__).resolve().parent
RUNS = HERE.parent / 'runs'
CONTROL = RUNS / '20261116T230943Z_b3_b4_200704'
ORIGINAL = RUNS / '20261116T040824Z_b0_b4_ppo_from_scratch'
THRESHOLDS = {'fixed': (.7,), 'adaptive': (.7, .5, .6, .8, .9)}
SEEDS = (0, 1, 2)
SEASONS = tuple(range(1920, 1952))
CONDITIONS = ('none', 'early_40', 'mid_40', 'late_40')
STEPS = 100_352
SURVEY = [name for name, _ in FIELDS].index('survey_value') - len(FIELDS)


def spray_mask(observation, permitted, thresholds):
    survey = float(observation[SURVEY])
    return np.array([True, *(bool(permitted) and survey >= np.float32(limit) for limit in thresholds)])


class ThresholdCycler(c.ChannelCycler):
    def __init__(self, config, frozen, thresholds, rank):
        super().__init__(config, learn=(2,), frozen=frozen, rank=rank, n_envs=config['training']['n_envs'])
        self.thresholds = thresholds
        self.action_space = gym.spaces.Discrete(1 + len(thresholds))

    def action_masks(self):
        return spray_mask(self.observation, super().action_masks()[1], self.thresholds)

    def step(self, action):
        chosen = int(action)
        if not self.action_masks()[chosen]:
            raise ValueError('Invalid threshold action')
        return super().step(int(chosen > 0))


class PilotAudit(c.Audit):
    def __init__(self, label):
        super().__init__()
        self.label = label

    def _on_step(self):
        ok = super()._on_step()
        if self.num_timesteps % 20_480 == 0:
            print('PROGRESS', self.label, self.num_timesteps, flush=True)
        return ok


def train(config, frozen, arm, seed):
    label = f'{arm}_s{seed}'
    path = HERE / f'{label}.zip'
    record = HERE / f'{label}_training.json'
    if record.exists():
        assert json.loads(record.read_text())['sha256'] == c.sha256(path)
        return path
    cfg = config['training']
    thresholds = THRESHOLDS[arm]
    env = c.SubprocVecEnv([partial(ThresholdCycler, config, frozen, thresholds, rank)
                          for rank in range(cfg['n_envs'])], start_method='spawn')
    try:
        model = c.MaskablePPO('MlpPolicy', env, seed=seed, device='cpu', gamma=cfg['gamma'],
            gae_lambda=cfg['gae_lambda'], n_steps=cfg['n_steps'], batch_size=cfg['batch_size'],
            n_epochs=cfg['n_epochs'], learning_rate=.0003, ent_coef=0.,
            policy_kwargs={'net_arch': {'pi': cfg['policy_layers'], 'vf': cfg['value_layers']}})
        # Both arms allocate 3% total initial mass to spraying before masking.
        # The adaptive arm assigns 80% of that spray mass to the existing 0.70 threshold.
        probabilities = [.97, .03] if arm == 'fixed' else [.97, .024, .0015, .0015, .0015, .0015]
        with torch.no_grad():
            model.policy.action_net.weight.zero_()
            model.policy.action_net.bias.copy_(torch.tensor(probabilities).log())
        print('TRAIN', label, STEPS, flush=True)
        start = time.perf_counter()
        audit = PilotAudit(label)
        model.learn(STEPS, callback=audit)
        assert model.num_timesteps == STEPS and audit.truncations == 0
        assert all(torch.isfinite(p).all() for p in model.policy.parameters())
        model.save(path)
        c.write_json(record, {'steps': STEPS, 'seed': seed, 'arm': arm, 'sha256': c.sha256(path),
                              'seconds': time.perf_counter()-start, 'train_seasons': len(audit.returns)})
        print('TRAINED', label, flush=True)
        return path
    finally:
        env.close()


class SprayPolicy:
    def __init__(self, model, thresholds):
        self.model = model
        self.thresholds = thresholds
        self.events = []

    def apply(self, observation, mask, action):
        legal = spray_mask(observation, mask[16], self.thresholds)
        selected = int(self.model.predict(observation, deterministic=True, action_masks=legal)[0].item())
        action[2] = int(selected > 0)
        if selected:
            self.events.append({'threshold': self.thresholds[selected-1], 'survey': float(observation[SURVEY])})
        return action


def evaluate(job):
    config, frozen, paths, seed, season_id = job
    torch.set_num_threads(1)
    rules = c.ResourceRules.from_config(config)
    price = c.grain_price(config)
    parameters, noise = c.pest_settings(config)
    shocks = c.evaluation_conditions(config)
    original = c.generate_season(config, split='validation', season_id=season_id)
    reference = c.RulePolicy.from_config(config)
    fixed_channels = tuple(c.FrozenChannels(c.MaskablePPO.load(p, device='cpu'), channels, True)
                           for p, channels in frozen)
    weather = {}
    rows = []
    for arm, path in paths.items():
        model = c.MaskablePPO.load(path, device='cpu')
        for condition in CONDITIONS:
            season = original.with_condition(beta=1., shock=shocks[condition])
            spray = SprayPolicy(model, THRESHOLDS[arm])
            policy = c.CompositePolicy(reference, fixed_channels + (spray,))
            backend = partial(c.LegacyProcessBackend, mode='experimental_pest', season=season,
                              parameters=parameters, noise_std=noise)
            env = c.ExperimentalPestEnv(season=season, parameters=parameters, noise_std=noise,
                                        rules=rules, grain_price=price, backend_factory=backend)
            try:
                record = c.evaluate_episode(env, policy, season, rules, price, reset_options={})
            finally:
                env.close()
            result = record['episode_result']
            assert c.resource_violations(result, result['water_cut_mm'], rules, season.beta) == 0
            assert np.isfinite([result['net_return'], result['harvested_grain_kg_ha']]).all()
            tape = record['daily_tape']
            trace = {day['yrdoy']: day['weather'] for day in tape}
            assert all(weather[d] == trace[d] for d in weather.keys() & trace.keys())
            weather.update(trace)
            days = [d['decision_day'] for d in tape if d['action_indices'][2]]
            assert len(days) == len(spray.events) == result['sprays']
            rows.append(dict(result, seed=seed, arm=arm, season=season_id, condition=condition,
                             sprays_detail=[dict(e, day=d) for e, d in zip(spray.events, days)]))
    return rows


def summarize(rows):
    metrics = ('harvested_grain_kg_ha', 'net_return', 'sprays')
    indexes = {arm: {(r['seed'], r['season'], r['condition']): r for r in rows if r['arm'] == arm}
               for arm in THRESHOLDS}
    expected = {(seed, s, c) for seed in SEEDS for s in SEASONS for c in CONDITIONS}
    assert len(rows) == 2*len(expected) and all(set(i) == expected for i in indexes.values())
    fixed, adaptive = indexes['fixed'], indexes['adaptive']
    return {condition: {'episodes_per_arm': len(keys),
        **{arm: {m: mean(index[k][m] for k in keys) for m in metrics} for arm, index in indexes.items()},
        'adaptive_minus_fixed': {m: mean(adaptive[k][m]-fixed[k][m] for k in keys) for m in metrics},
        'adaptive_yield_delta_by_seed': {seed: mean(adaptive[k][metrics[0]]-fixed[k][metrics[0]]
            for k in keys if k[0] == seed) for seed in SEEDS}}
        for condition in (*CONDITIONS, 'all')
        for keys in [sorted(k for k in expected if condition == 'all' or k[2] == condition)]}


def main():
    os.environ['MARS_RUN_DIR'] = str(HERE)
    torch.set_num_threads(1)
    design = json.loads((CONTROL/'design.json').read_text())
    config_path = ORIGINAL/'config.yaml'
    assert c.sha256(config_path) == design['config_sha256']
    assert os.environ['MARS_IMAGE_ID'] == design['image']
    for name, digest in design['source_sha256'].items():
        assert c.sha256(Path('/workspace')/name) == digest, name
    config = yaml.safe_load(config_path.read_text())
    assert STEPS % (config['training']['n_steps']*config['training']['n_envs']) == 0
    probe = np.zeros(len(FIELDS), dtype=np.float32)
    probe[SURVEY] = .6
    assert spray_mask(probe, True, THRESHOLDS['adaptive']).tolist() == [True, False, True, True, False, False]
    assert spray_mask(probe, True, THRESHOLDS['fixed']).tolist() == [True, False]
    assert spray_mask(probe, False, THRESHOLDS['adaptive']).sum() == 1
    protocol = {'steps': STEPS, 'seeds': SEEDS, 'thresholds': THRESHOLDS, 'conditions': CONDITIONS,
                'validation_seasons': SEASONS, 'source_sha256': design['source_sha256'],
                'script_sha256': c.sha256(__file__), 'config_sha256': design['config_sha256'],
                'image': design['image'], 'final_test_split_used': False}
    if (HERE/'protocol.json').exists():
        assert json.loads((HERE/'protocol.json').read_text()) == json.loads(json.dumps(protocol))
    else:
        c.write_json(HERE/'protocol.json', protocol)
    rows = []
    for seed in SEEDS:
        frozen = tuple((str(CONTROL/f'b{i}_s{seed}.zip'), (i-1,)) for i in (1,2))
        assert {Path(p).stem: c.sha256(p) for p,_ in frozen} == design['b3_fixed_final_sha256'][f'b3_s{seed}']
        paths = {arm: train(config,frozen,arm,seed) for arm in THRESHOLDS}
        batch = HERE/f'seed_{seed}_episodes.json'
        if not batch.exists():
            print('EVALUATE', seed, flush=True)
            with ProcessPoolExecutor(max_workers=6, mp_context=get_context('fork')) as pool:
                cases = [row for group in pool.map(evaluate, [(config,frozen,paths,seed,s) for s in SEASONS])
                         for row in group]
            c.write_json(batch,cases)
        rows.extend(json.loads(batch.read_text()))
    c.write_json(HERE/'results.json', {'conditions': summarize(rows), 'final_test_split_used': False})
    print('PILOT_COMPLETE', flush=True)


if __name__ == '__main__':
    main()
