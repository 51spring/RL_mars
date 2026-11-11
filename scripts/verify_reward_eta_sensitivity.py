"""Verify reward sensitivity by replaying fixed actions in real DSSAT seasons."""
import hashlib
import json
import math
import os
from pathlib import Path
from statistics import fmean
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from mars_env.artifacts import new_run, sha256, write_json
from mars_env.experimental_env import ExperimentalPestEnv
from mars_env.exogenous import generate_season
from mars_env.observations import FIELDS
from mars_env.pests import PestParameters
from mars_env.process_backend import LegacyProcessBackend
from mars_env.resources import ResourceRules
from mars_env.rewards import PotentialRewardWrapper


def observed(observation, name):
    index, scale = next((i, scale) for i, (field, scale) in enumerate(FIELDS) if field == name)
    return float(observation[-len(FIELDS) + index]) * scale


def run_case(config, season, baseline, eta, limit):
    pest = baseline['pest']
    parameters = PestParameters.from_config({**config, 'pest': pest})
    rules = ResourceRules.from_config(config)

    def backend_factory(**kwargs):
        return LegacyProcessBackend(mode='experimental_pest', season=season, parameters=parameters,
                                    noise_std=pest['survey_noise_std'], **kwargs)

    base = ExperimentalPestEnv(season=season, parameters=parameters, noise_std=pest['survey_noise_std'],
                               rules=rules, max_days=limit, backend_factory=backend_factory,
                               grain_price=config['economics']['grain_usd_kg'])
    reward_config = config['reward_shaping']
    env = PotentialRewardWrapper(base, eta_by_stage=eta, scale=reward_config['scale'],
                                 gamma=reward_config['gamma'])
    rows = []
    digest = hashlib.sha256()
    try:
        obs, info = env.reset()
        assert info['experimental_only'] and not info['research_ready']
        digest.update(obs.tobytes())
        for prior in baseline['rows'][:limit]:
            assert base.state['yrdoy'] == prior['completed_date']
            actual = prior['action']
            action = [rules.water_grid.index(actual['water_mm']),
                      rules.nitrogen_grid.index(actual['nitrogen_kg_ha']), actual['spray']]
            mask = env.action_masks()
            assert all(mask[offset + value] for offset, value in zip((0, 6, 15), action, strict=True))
            old_stage = round(observed(obs, 'istage'))
            phi_before = eta[old_stage] * observed(obs, 'topwt') * base.grain_price
            obs, reward, terminated, truncated, info = env.step(action)
            digest.update(obs.tobytes())
            stage = round(observed(obs, 'istage'))
            phi_after = 0.0 if terminated else eta[stage] * observed(obs, 'topwt') * base.grain_price
            raw = info['raw_reward']
            assert raw == prior['reward']
            assert math.isclose(info['shaping_potential_before'], phi_before, abs_tol=1e-9)
            assert math.isclose(info['shaping_potential_after'], phi_after, abs_tol=1e-9)
            assert math.isclose(reward * env.scale, raw + phi_after - phi_before, abs_tol=1e-9)
            rows.append({'date': prior['completed_date'], 'action': action, 'stage_before': old_stage,
                         'stage_after': stage, 'raw_reward': raw, 'training_reward': reward,
                         'potential_delta': phi_after - phi_before})
            if terminated or truncated:
                break
        expected_harvest = limit >= len(baseline['rows'])
        assert len(rows) == min(limit, len(baseline['rows']))
        assert terminated == expected_harvest and truncated == (not expected_harvest)
        audit = info['reward_audit']
        assert abs(audit['telescoping_residual']) < 1e-6
        assert math.isclose(audit['raw_return'], math.fsum(row['raw_reward'] for row in rows), abs_tol=1e-9)
        if expected_harvest:
            assert audit['final_potential'] == 0 and info['episode_result'] == baseline['episode_result']
        else:
            assert 'episode_result' not in info and info['revenue'] == 0
        return {'rows': rows, 'observation_sha256': digest.hexdigest(),
                'episode_result': info.get('episode_result'), 'audit': audit,
                'nonterminal_mean_abs_shaping_usd_ha': fmean(
                    abs(row['potential_delta']) for row in (rows[:-1] if terminated else rows)),
                'terminal_shaping_usd_ha': rows[-1]['potential_delta'] if terminated else None}
    finally:
        env.close()


def main():
    config = yaml.safe_load((ROOT / 'configs/proposal_v2.yaml').read_text(encoding='utf-8'))
    tracker = json.loads((ROOT / 'configs/field_calibration_candidate_screen.json').read_text(encoding='utf-8'))
    reference = ROOT / tracker['faw_dssat_pairing_evidence']
    verified = json.loads(reference.read_text(encoding='utf-8'))
    assert verified['passed'] and not verified['research_ready']
    eta = config['reward_shaping']['eta_by_stage']
    profiles = {name: {stage: value * factor for stage, value in eta.items()}
                for name, factor in [('zero', 0), ('half', 0.5), ('baseline', 1), ('double', 2)]}
    run = new_run(ROOT, 'reward_eta_common_season')
    os.environ['MARS_RUN_DIR'] = str(run)
    print(f'RUN_DIR={run}', flush=True)
    summaries = {}
    try:
        for season_id, limit in [(0, 240), (1, 240), (0, 60)]:
            key = f'season_{season_id}'
            label = f'{key}_{"harvest" if limit == 240 else "truncate"}'
            season = generate_season(config, split='validation', season_id=season_id).with_condition(beta=1, shock=None)
            assert season.paired_digest() == verified['seasons'][key]['season']['paired_digest']
            baseline_file = reference.with_name(f'{key}_baseline.json')
            baseline = json.loads(baseline_file.read_text(encoding='utf-8'))
            summaries[label] = {'season': season.manifest(), 'reference_sha256': sha256(baseline_file), 'cases': {}}
            zero = None
            for name, mapping in profiles.items():
                print(label, name, flush=True)
                result = run_case(config, season, baseline, mapping, limit)
                write_json(run / f'{label}_{name}.json', result)
                if name == 'zero':
                    zero = result
                assert result['observation_sha256'] == zero['observation_sha256']
                assert result['episode_result'] == zero['episode_result']
                assert result['audit']['raw_return'] == zero['audit']['raw_return']
                assert (result['nonterminal_mean_abs_shaping_usd_ha'] > 0) == (name != 'zero')
                summaries[label]['cases'][name] = {k: v for k, v in result.items() if k != 'rows'}
            base_audit = summaries[label]['cases']['baseline']['audit']
            double_audit = summaries[label]['cases']['double']['audit']
            assert math.isclose(double_audit['initial_potential'], 2 * base_audit['initial_potential'])
            assert math.isclose(double_audit['final_potential'], 2 * base_audit['final_potential'])
        write_json(run / 'verification.json', {'passed': True, 'real_dssat': True, 'experimental_only': True,
                   'research_ready': False, 'main_training_allowed': False, 'eta_profiles': profiles,
                   'source': reference.relative_to(ROOT).as_posix(), 'reference_sha256': sha256(reference),
                   'gamma': config['reward_shaping']['gamma'], 'scale': config['reward_shaping']['scale'],
                   'runs': summaries})
    except BaseException as error:
        write_json(run / 'failure.json', {'passed': False, 'error': repr(error), 'completed': summaries})
        raise


if __name__ == '__main__':
    main()
