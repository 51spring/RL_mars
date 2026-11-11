"""Pair experimental pest settings on real DSSAT under identical fixed actions."""
from dataclasses import asdict
import json
import math
import os
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from mars_env.artifacts import new_run, write_json
from mars_env.audits import shift_yrdoy
from mars_env.experimental_env import ExperimentalPestEnv
from mars_env.exogenous import generate_season
from mars_env.leaf_diagnostics import verify_leaf_accounting
from mars_env.observations import FIELDS
from mars_env.pests import PestParameters
from mars_env.process_backend import LegacyProcessBackend
from mars_env.resources import ResourceRules
from verify_season_balance_online import check_online_replay

SURVEY_FIELDS = {name: (i, scale) for i, (name, scale) in enumerate(FIELDS)
                 if name.startswith('survey_')}
NON_SURVEY = [i for i, (name, _) in enumerate(FIELDS) if name not in SURVEY_FIELDS]


def run_case(config, season, pest, spray_days):
    parameters = PestParameters.from_config({**config, 'pest': pest})
    noise_std = pest['survey_noise_std']
    def backend_factory(**kwargs):
        return LegacyProcessBackend(mode='experimental_pest', season=season,
                                    parameters=parameters, noise_std=noise_std, **kwargs)

    env = ExperimentalPestEnv(season=season, parameters=parameters, noise_std=noise_std,
                              rules=ResourceRules.from_config(config), backend_factory=backend_factory,
                              grain_price=config['economics']['grain_usd_kg'])
    rows = []
    try:
        obs, info = env.reset()
        assert info['experimental_only'] and not info['research_ready']
        for day in range(env.max_days):
            completed_date = int(env.state['yrdoy'])
            action = [2 if day in (0, 15, 30, 45) else 0,
                      {40: 3, 45: 4, 80: 6}.get(day, 0), int(day in spray_days)]
            mask = env.action_masks()
            assert all(mask[offset + choice] for offset, choice in zip((0, 6, 15), action))
            obs, reward, terminated, truncated, info = env.step(action)
            assert env.observation_space.contains(obs) and obs.shape == env.observation_space.shape
            assert not info['research_ready'] and 'mars_pest_diagnostic' not in info and 'density' not in info
            state = env.state
            diagnostic = state['mars_pest_diagnostic']
            assert diagnostic['day'] == day and diagnostic['spray'] == bool(action[2])
            assert int(state['yrdoy']) == (completed_date if terminated else shift_yrdoy(completed_date, 1))
            assert diagnostic['mean_temperature_c'] == (state['tmin'] + state['tmax']) / 2
            public = state['mars_pest_public']
            assert public == diagnostic['next_morning_survey']
            latest = obs[-len(FIELDS):]
            for key, (index, scale) in SURVEY_FIELDS.items():
                assert math.isclose(float(latest[index]) * scale, public[key], abs_tol=1e-6)
            leaf = state.get('mars_leaf_diagnostic')
            if diagnostic['applied_fraction'] > 0:
                assert leaf is not None and leaf['yrdoy'] == completed_date
                assert leaf['fraction'] == diagnostic['applied_fraction']
                verify_leaf_accounting(leaf)
            rows.append({'completed_date': completed_date, 'action': asdict(env.previous_action),
                         'diagnostic': diagnostic, 'leaf': leaf, 'plant': state['mars_plant_audit'],
                         'non_survey_frame': latest[NON_SURVEY].tolist(), 'reward': reward})
            if terminated or truncated:
                assert terminated and not truncated and info['episode_result']['reason'] == 'harvest'
                assert math.isclose(sum(row['reward'] for row in rows),
                                    info['episode_result']['net_return'], abs_tol=1e-6)
                assert info['episode_result']['sprays'] == len(spray_days)
                break
        check_online_replay({'online_diagnostics': [row['diagnostic'] for row in rows]},
                            parameters, season, noise_std)
        return {'rows': rows, 'episode_result': info['episode_result']}
    finally:
        env.close()


def check_pair(base, variant, name):
    shared = min(len(base['rows']), len(variant['rows']))
    changed = False
    for a, b in zip(base['rows'][:shared], variant['rows'][:shared], strict=True):
        assert a['completed_date'] == b['completed_date'] and a['action'] == b['action']
        x, y = a['diagnostic'], b['diagnostic']
        assert x['mean_temperature_c'] == y['mean_temperature_c'] and x['arrival'] == y['arrival']
        if name == 'survey_noise':
            assert {k: v for k, v in x.items() if k != 'next_morning_survey'} == {
                k: v for k, v in y.items() if k != 'next_morning_survey'}
            assert all(a[k] == b[k] for k in ('leaf', 'plant', 'non_survey_frame', 'reward'))
            changed |= x['next_morning_survey']['survey_value'] != y['next_morning_survey']['survey_value']
        elif name == 'alpha':
            assert x['density'] == y['density']
            assert math.isclose(y['requested_fraction'], 2 * x['requested_fraction'], abs_tol=1e-12)
            changed |= y['applied_fraction'] > x['applied_fraction']
        else:
            assert y['density'] + 1e-12 >= x['density'] and y['effect'] == 0
            changed |= y['density'] > x['density']
    if name == 'survey_noise':
        assert len(base['rows']) == len(variant['rows']) and base['episode_result'] == variant['episode_result']
    assert changed, f'{name} contrast had no qualifying response'
    return shared


def main():
    config = yaml.safe_load((ROOT / 'configs/proposal_v2.yaml').read_text(encoding='utf-8'))
    spec = json.loads((ROOT / 'configs/faw_technical_sensitivity.json').read_text(encoding='utf-8-sig'))
    assert spec['scope'] == 'technical_diagnostic_only'
    assert all(config['pest'][key] is None for key in spec['baseline_overrides'])
    base = {**config['pest'], **spec['baseline_overrides']}
    variants = {'survey_noise': spec['axes']['survey_noise']['stress'],
                'alpha': spec['axes']['alpha']['double'], 'efficacy': spec['axes']['efficacy']['zero']}
    run = new_run(ROOT, 'faw_dssat_pairing')
    os.environ['MARS_RUN_DIR'] = str(run)
    print(f'RUN_DIR={run}', flush=True)
    summaries = {}
    try:
        for season_id in (0, 1):
            season = generate_season(config, split='validation', season_id=season_id).with_condition(beta=1, shock=None)
            label = f'season_{season_id}'
            summaries[label] = {'season': season.manifest(), 'cases': {}}
            baseline = None
            for name, overrides in {'baseline': {}, **variants}.items():
                print(f'{label} {name}', flush=True)
                pest = {**base, **overrides}
                result = run_case(config, season, pest, spec['spray_days'])
                write_json(run / f'{label}_{name}.json', {'pest': pest, **result})
                if name == 'baseline':
                    baseline = result
                shared = len(result['rows']) if name == 'baseline' else check_pair(baseline, result, name)
                summaries[label]['cases'][name] = {
                    'days': len(result['rows']), 'matched_days': shared,
                    'positive_native_writes': sum(row['diagnostic']['applied_fraction'] > 0 for row in result['rows']),
                    'episode_result': result['episode_result'],
                }
        write_json(run / 'verification.json', {'passed': True, 'experimental_only': True,
                   'research_ready': False, 'main_training_allowed': False, 'seasons': summaries})
    except BaseException as error:
        write_json(run / 'failure.json', {'passed': False, 'error': repr(error), 'completed': summaries})
        raise


if __name__ == '__main__':
    main()
