"""Pilot: choose next survey interval's threshold before its first reading."""
from collections import Counter
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

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'b3_threshold_100k'))
import run as pilot

c = pilot.c
LIMITS = (.7, .5, .6, .8, .9)
SEASONS = tuple(range(1964, 1996))
ARMS = ('fixed', 'adaptive', 'clamped')


class WeeklyThreshold:
    def __init__(self, flexible):
        self.flexible = flexible
        self.day = 0
        self.active = 0

    @property
    def choosing(self):
        # Day 6 chooses the threshold for days 7–13, before day 7's new reading.
        return self.day % 7 == 6

    def observe(self, observation):
        return np.concatenate((observation, np.array([LIMITS[self.active], self.choosing], dtype=np.float32)))

    def mask(self, observation, permitted):
        timing = pilot.spray_mask(observation, permitted, (LIMITS[self.active],))
        choice = [True] + [self.flexible and self.choosing] * (len(LIMITS)-1)
        return np.concatenate((timing, choice))

    def advance(self, next_threshold):
        if self.choosing:
            self.active = next_threshold
        self.day += 1


class WeeklyCycler(c.ChannelCycler):
    def __init__(self, config, frozen, flexible, rank):
        super().__init__(config, learn=(2,), frozen=frozen, rank=rank, n_envs=config['training']['n_envs'])
        self.flexible = flexible
        size = self.observation_space.shape[0]
        self.observation_space = gym.spaces.Box(-np.inf, np.inf, (size+2,), dtype=np.float32)
        self.action_space = gym.spaces.MultiDiscrete([2, len(LIMITS)])

    def reset(self, **kwargs):
        self.week = WeeklyThreshold(self.flexible)
        observation, info = super().reset(**kwargs)
        return self.week.observe(observation), info

    def action_masks(self):
        return self.week.mask(self.observation, super().action_masks()[1])

    def step(self, action):
        spray, threshold = map(int, action)
        legal = self.action_masks()
        if not (legal[spray] and legal[2+threshold]):
            raise ValueError('Masked spray or threshold action')
        observation, reward, terminated, truncated, info = super().step(spray)
        self.week.advance(threshold)
        return self.week.observe(observation), reward, terminated, truncated, info


def train(config, frozen, arm, seed):
    label = f'{arm}_s{seed}'
    model_file, record_file = HERE/f'{label}.zip', HERE/f'{label}_training.json'
    if record_file.exists():
        record = json.loads(record_file.read_text())
        assert record['steps'] == pilot.STEPS and record['sha256'] == c.sha256(model_file)
        return model_file
    cfg = config['training']
    env = c.SubprocVecEnv([partial(WeeklyCycler, config, frozen, arm=='adaptive', rank)
                          for rank in range(cfg['n_envs'])], start_method='spawn')
    try:
        model = c.MaskablePPO('MlpPolicy', env, seed=seed, device='cpu', gamma=cfg['gamma'],
            gae_lambda=cfg['gae_lambda'], n_steps=cfg['n_steps'], batch_size=cfg['batch_size'],
            n_epochs=cfg['n_epochs'], learning_rate=.0003, ent_coef=0.,
            policy_kwargs={'net_arch': {'pi':cfg['policy_layers'], 'vf':cfg['value_layers']}})
        # Split logits into the two-action timing head and five-action threshold head.
        with torch.no_grad():
            model.policy.action_net.weight.zero_()
            model.policy.action_net.bias.copy_(torch.tensor([.97,.03,.8,.05,.05,.05,.05]).log())
        start = time.perf_counter()
        print('TRAIN',label,pilot.STEPS,flush=True)
        audit = pilot.PilotAudit(label)
        model.learn(pilot.STEPS,callback=audit)
        assert model.num_timesteps == pilot.STEPS and audit.truncations == 0
        assert all(torch.isfinite(x).all() for x in model.policy.parameters())
        model.save(model_file)
        c.write_json(record_file,{'steps':pilot.STEPS,'sha256':c.sha256(model_file),
            'seconds':time.perf_counter()-start,'train_seasons':len(audit.returns)})
        return model_file
    finally:
        env.close()


class WeeklyPolicy:
    def __init__(self, model, flexible):
        self.model = model
        self.week = WeeklyThreshold(flexible)
        self.assignments = []
        self.events = []
        self.survey_bins = Counter()

    def apply(self, observation, mask, action):
        spray, threshold = map(int,self.model.predict(self.week.observe(observation),deterministic=True,
            action_masks=self.week.mask(observation,mask[16]))[0])
        survey = float(observation[pilot.SURVEY])
        if mask[16]:
            survey_bin = str(np.searchsorted((.5,.6,.7,.8,.9),survey,side='right'))
            self.survey_bins[f'{survey_bin}_days'] += 1
            self.survey_bins[f'{survey_bin}_sprays'] += spray
        action[2] = spray
        if spray:
            self.events.append({'day':self.week.day,'survey':survey,'threshold':LIMITS[self.week.active]})
        if self.week.choosing:
            self.assignments.append({'selected_on':self.week.day,'effective_from':self.week.day+1,
                                     'threshold':LIMITS[threshold]})
        self.week.advance(threshold)
        return action


def evaluate(job):
    config, frozen, paths, seed, season_id = job
    torch.set_num_threads(1)
    rules, price = c.ResourceRules.from_config(config), c.grain_price(config)
    parameters, noise = c.pest_settings(config)
    original = c.generate_season(config,split='validation',season_id=season_id)
    shocks = c.evaluation_conditions(config)
    reference = c.RulePolicy.from_config(config)
    channels = tuple(c.FrozenChannels(c.MaskablePPO.load(path,device='cpu'),indices,True)
                     for path,indices in frozen)
    models = {arm:c.MaskablePPO.load(path,device='cpu') for arm,path in paths.items()}
    weather, rows = {}, []
    for arm in ARMS:
        for condition in pilot.CONDITIONS:
            season = original.with_condition(beta=1.,shock=shocks[condition])
            spray = WeeklyPolicy(models['adaptive' if arm=='clamped' else arm],arm=='adaptive')
            policy = c.CompositePolicy(reference,channels+(spray,))
            backend = partial(c.LegacyProcessBackend,mode='experimental_pest',season=season,
                              parameters=parameters,noise_std=noise)
            env = c.ExperimentalPestEnv(season=season,parameters=parameters,noise_std=noise,
                                        rules=rules,grain_price=price,backend_factory=backend)
            try:
                record = c.evaluate_episode(env,policy,season,rules,price,reset_options={})
            finally:
                env.close()
            result = record['episode_result']
            assert c.resource_violations(result,result['water_cut_mm'],rules,season.beta)==0
            trace = {d['yrdoy']:d['weather'] for d in record['daily_tape']}
            assert all(weather[d]==trace[d] for d in weather.keys() & trace.keys())
            weather.update(trace)
            assert len(spray.events)==result['sprays']
            # Only count assignments actually in force on at least one later decision day.
            assignments = [x for x in spray.assignments if x['effective_from'] < record['steps']]
            rows.append(dict(result,arm=arm,seed=seed,season=season_id,condition=condition,
                             events=spray.events,assignments=assignments,survey_bins=spray.survey_bins))
    return rows


def summarize(rows,seasons,seeds):
    index = {arm:{(r['seed'],r['season'],r['condition']):r for r in rows if r['arm']==arm} for arm in ARMS}
    expected = {(s,t,k) for s in seeds for t in seasons for k in pilot.CONDITIONS}
    assert len(rows)==len(ARMS)*len(expected) and all(set(i)==expected for i in index.values())
    metrics = ('harvested_grain_kg_ha','net_return','sprays')
    results = {}
    for cond in (*pilot.CONDITIONS,'all'):
        keys = sorted(k for k in expected if cond=='all' or k[2]==cond)
        entry = {'pairs':len(keys)}
        for arm,i in index.items():
            entries = [i[k] for k in keys]
            entry[arm] = {m:mean(r[m] for r in entries) for m in metrics}
            entry[arm]['assigned_threshold_counts'] = Counter(e['threshold'] for r in entries for e in r['assignments'])
            entry[arm]['spray_threshold_counts'] = Counter(e['threshold'] for r in entries for e in r['events'])
            entry[arm]['survey_bins'] = dict(sum((Counter(r['survey_bins']) for r in entries),Counter()))
            first_days = [r['events'][0]['day'] for r in entries if r['events']]
            entry[arm]['mean_first_spray_day'] = mean(first_days) if first_days else None
        for comparator in ('fixed','clamped'):
            entry[f'adaptive_minus_{comparator}'] = {'by_seed':{str(s):{
                m:mean(index['adaptive'][k][m]-index[comparator][k][m] for k in keys if k[0]==s)
                for m in metrics} for s in seeds}, **{
                m:mean(index['adaptive'][k][m]-index[comparator][k][m] for k in keys) for m in metrics},
                'changed_spray_schedules':sum([e['day'] for e in index['adaptive'][k]['events']] !=
                    [e['day'] for e in index[comparator][k]['events']] for k in keys)}
        results[cond] = entry
    return results


def main():
    torch.set_num_threads(1)
    smoke = '--smoke' in sys.argv
    work = HERE/'smoke' if smoke else HERE
    work.mkdir(exist_ok=True)
    os.environ['MARS_RUN_DIR'] = str(work)
    design = json.loads((pilot.CONTROL/'design.json').read_text())
    config_path = pilot.ORIGINAL/'config.yaml'
    assert c.sha256(config_path)==design['config_sha256'] and os.environ['MARS_IMAGE_ID']==design['image']
    for name,sha in design['source_sha256'].items():
        assert c.sha256(Path('/workspace')/name)==sha,name
    config = yaml.safe_load(config_path.read_text())
    seeds, seasons = ((0,),(SEASONS[0],)) if smoke else (pilot.SEEDS,SEASONS)
    assert not set(SEASONS)&(set(pilot.SEASONS)|set(range(1960,1964)))
    protocol = {'steps':pilot.STEPS,'seeds':seeds,'validation_seasons':seasons,'conditions':pilot.CONDITIONS,
        'limits':LIMITS,'choice_timing':'day 6 modulo 7, effective next day','initial_week':.7,
        'config_sha256':design['config_sha256'],'source_sha256':design['source_sha256'],
        'runner_sha256':c.sha256(__file__),'reused_pilot_helper_sha256':c.sha256(pilot.__file__),
        'image':design['image'],'final_test_split_used':False,'smoke':smoke}
    protocol_file = work/'protocol.json'
    if protocol_file.exists():
        assert json.loads(protocol_file.read_text())==json.loads(json.dumps(protocol))
    else:
        c.write_json(protocol_file,protocol)
    all_rows = []
    for seed in seeds:
        frozen = tuple((str(pilot.CONTROL/f'b{i}_s{seed}.zip'),(i-1,)) for i in (1,2))
        assert {Path(p).stem:c.sha256(p) for p,_ in frozen}==design['b3_fixed_final_sha256'][f'b3_s{seed}']
        if smoke:
            paths = smoke_models(config,frozen,seed,work)
        else:
            paths = {arm:train(config,frozen,arm,seed) for arm in ARMS[:2]}
        destination = work/f'seed_{seed}_episodes.json'
        if not destination.exists():
            print('EVALUATE',seed,flush=True)
            with ProcessPoolExecutor(max_workers=6,mp_context=get_context('fork')) as pool:
                rows = [row for group in pool.map(evaluate,[(config,frozen,paths,seed,s) for s in seasons]) for row in group]
            c.write_json(destination,rows)
        all_rows.extend(json.loads(destination.read_text()))
    c.write_json(work/'results.json',{'passed':True,'conditions':summarize(all_rows,seasons,seeds),
                                    'final_test_split_used':False,'smoke':smoke})
    print('SMOKE_COMPLETE' if smoke else 'PILOT_COMPLETE',flush=True)


def smoke_models(config,frozen,seed,work):
    spec = WeeklyThreshold(True)
    probe = np.zeros(196,dtype=np.float32)
    probe[pilot.SURVEY] = .6
    assert not spec.mask(probe,True)[1]
    for _ in range(6):
        spec.advance(0)
    assert spec.choosing and spec.mask(probe,True)[2:].all()
    assert not spec.mask(probe,True)[1]
    spec.advance(LIMITS.index(.6))
    assert not spec.choosing and spec.mask(probe,True)[1]
    paths = {}
    for arm in ARMS[:2]:
        env = WeeklyCycler(config,frozen,arm=='adaptive',0)
        try:
            model = c.MaskablePPO('MlpPolicy',env,seed=seed,device='cpu',n_steps=32,batch_size=32,n_epochs=1)
            model.learn(64)
            paths[arm] = work/f'{arm}.zip'
            model.save(paths[arm])
        finally:
            env.close()
    return paths


if __name__ == '__main__':
    main()
