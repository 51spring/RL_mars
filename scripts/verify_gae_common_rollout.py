"""Audit MaskablePPO GAE on fixed real DSSAT action sequences without updates."""
import hashlib
import json
import math
import os
from pathlib import Path
import sys

import gymnasium as gym
import numpy as np
from sb3_contrib import MaskablePPO
from stable_baselines3.common.callbacks import BaseCallback
import torch
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from mars_env.economics import grain_price
from mars_env.artifacts import new_run, sha256, write_json
from mars_env.experimental_env import ExperimentalPestEnv
from mars_env.exogenous import generate_season
from mars_env.pests import PestParameters
from mars_env.process_backend import LegacyProcessBackend
from mars_env.resources import ResourceRules
from mars_env.rewards import PotentialRewardWrapper


class FixedActions(gym.Wrapper):
    def __init__(self, env, actions, dates):
        super().__init__(env)
        self.actions, self.dates = actions, dates

    def reset(self, **kwargs):
        self.index = 0
        return self.env.reset(**kwargs)

    def action_masks(self):
        mask = self.env.action_masks()
        fixed = np.zeros_like(mask)
        choices = [offset + action for offset, action in zip((0, 6, 15), self.actions[self.index], strict=True)]
        assert mask[choices].all()
        fixed[choices] = True
        return fixed

    def step(self, action):
        assert tuple(action) == self.actions[self.index]
        assert self.unwrapped.state['yrdoy'] == self.dates[self.index]
        self.index += 1
        return self.env.step(action)


class AuditCapture(BaseCallback):
    def __init__(self):
        super().__init__()
        self.steps = []

    def _on_step(self):
        info = self.locals['infos'][0]
        done = bool(self.locals['dones'][0])
        timeout = info.get('TimeLimit.truncated', False)
        # Callback runs before the collector adds a timeout bootstrap.
        self.steps.append({
            'raw': info['raw_reward'], 'shaped': float(self.locals['rewards'][0]),
            'done': done, 'timeout': timeout,
            'terminal_obs': info.get('terminal_observation'),
            'revenue': info['revenue'], 'episode_result': info.get('episode_result'),
        })
        return True


def evaluate(config, season, reference, limit, coefficient):
    pest = reference['pest']
    parameters = PestParameters.from_config({**config, 'pest': pest})
    rules = ResourceRules.from_config(config)
    rows = reference['rows'][:limit]
    actions = [
        (rules.water_grid.index(row['action']['water_mm']),
         rules.nitrogen_grid.index(row['action']['nitrogen_kg_ha']), row['action']['spray'])
        for row in rows
    ]
    base = ExperimentalPestEnv(season=season, parameters=parameters, noise_std=pest['survey_noise_std'],
                               rules=rules, max_days=limit,
                               grain_price=grain_price(config),
                               backend_factory=lambda **kwargs: LegacyProcessBackend(
                                   mode='experimental_pest', season=season, parameters=parameters,
                                   noise_std=pest['survey_noise_std'], **kwargs))
    shape = config['reward_shaping']
    env = FixedActions(PotentialRewardWrapper(base, eta_by_stage=shape['eta_by_stage'],
                       scale=shape['scale'], gamma=shape['gamma']), actions,
                       [row['completed_date'] for row in rows])
    try:
        steps = len(rows) + 1  # Also collect the first step after automatic reset.
        gamma = config['training']['gamma']
        model = MaskablePPO('MlpPolicy', env, device='cpu', seed=42, gamma=gamma,
                            gae_lambda=coefficient, n_steps=steps, batch_size=64, verbose=0)
        capture = AuditCapture()
        _, callback = model._setup_learn(steps, capture)
        vector = model.get_env()
        assert model.collect_rollouts(vector, callback, model.rollout_buffer, steps)
        buffer = model.rollout_buffer
        assert len(capture.steps) == steps
        assert [i for i, row in enumerate(capture.steps) if row['done']] == [steps - 2]
        assert np.flatnonzero(buffer.episode_starts[:, 0]).tolist() == [0, steps - 1]
        assert buffer.actions[:, 0].tolist() == [list(a) for a in actions + actions[:1]]
        assert [row['raw'] for row in capture.steps] == [r['reward'] for r in rows + rows[:1]]

        boundary = capture.steps[-2]
        timeout = limit < len(reference['rows'])
        assert boundary['timeout'] == timeout and boundary['terminal_obs'] is not None
        with torch.no_grad():
            def critic(obs):
                tensor, _ = model.policy.obs_to_tensor(obs)
                return model.policy.predict_values(tensor).cpu().numpy().reshape(-1)

            terminal_value = float(critic(boundary['terminal_obs'])[0])
            last_value = float(critic(model._last_obs)[0])
        values = buffer.values[:, 0].astype(float)
        expected_rewards = np.array([row['shaped'] for row in capture.steps], dtype=float)
        if timeout:
            assert boundary['revenue'] == 0 and boundary['episode_result'] is None
            assert not math.isclose(terminal_value, values[-1], abs_tol=1e-5)
            expected_rewards[-2] += gamma * terminal_value
        else:
            assert boundary['episode_result'] == reference['episode_result']
            assert abs(terminal_value) > 1e-5
        np.testing.assert_allclose(buffer.rewards[:, 0], expected_rewards, rtol=0, atol=2e-7)

        # Direct weighted sums of TD residuals, stopped at each episode boundary.
        dones = np.array([row['done'] for row in capture.steps])
        next_values = np.r_[values[1:], last_value]
        residuals = expected_rewards + gamma * next_values * ~dones - values
        expected_advantages = [
            math.fsum((gamma * coefficient) ** (j - i) * residuals[j] for j in range(i, end + 1))
            for i in range(steps) for end in [next((j for j in range(i, steps) if dones[j]), steps - 1)]
        ]
        np.testing.assert_allclose(buffer.advantages[:, 0], expected_advantages, rtol=0, atol=3e-6)
        np.testing.assert_allclose(buffer.returns[:, 0], np.asarray(expected_advantages) + values,
                                   rtol=0, atol=3e-6)
        return {
            'decisions': steps, 'timeout': timeout, 'terminal_critic_value': terminal_value,
            'reset_critic_value': float(values[-1]),
            'last_nonterminal_critic_value': last_value,
            'boundary_reward_before_bootstrap': boundary['shaped'],
            'boundary_reward_in_buffer': float(buffer.rewards[-2, 0]),
            'raw_reward_sum_before_reset': math.fsum(row['raw'] for row in capture.steps[:-1]),
            'optimizer_updates': model._n_updates,
            'max_advantage_error': float(np.max(np.abs(buffer.advantages[:, 0] - expected_advantages))),
            'rewards': buffer.rewards[:, 0].tolist(), 'critic_values': values.tolist(),
            'advantages': buffer.advantages[:, 0].tolist(),
            'observations_sha256': hashlib.sha256(buffer.observations.tobytes()).hexdigest(),
        }
    finally:
        env.close()


def main():
    config = yaml.safe_load((ROOT / 'configs/proposal_v2.yaml').read_text(encoding='utf-8'))
    tracker = json.loads((ROOT / 'configs/field_calibration_candidate_screen.json').read_text(encoding='utf-8'))
    reference = ROOT / tracker['faw_dssat_pairing_evidence']
    verified = json.loads(reference.read_text(encoding='utf-8'))
    assert verified['passed'] and not verified['research_ready']
    run = new_run(ROOT, 'gae_common_rollout')
    os.environ['MARS_RUN_DIR'] = str(run)
    print(f'RUN_DIR={run}', flush=True)
    summaries = {}
    try:
        for season_id, limit in [(0, 240), (1, 240), (0, 60)]:
            key = f'season_{season_id}'
            label = f'{key}_{"harvest" if limit == 240 else "timeout"}'
            season = generate_season(config, split='validation', season_id=season_id).with_condition(beta=1, shock=None)
            assert season.paired_digest() == verified['seasons'][key]['season']['paired_digest']
            baseline_path = reference.with_name(f'{key}_baseline.json')
            baseline = json.loads(baseline_path.read_text(encoding='utf-8'))
            cases = {}
            for coefficient in config['training']['gae_lambda_candidates']:
                print(label, coefficient, flush=True)
                cases[str(coefficient)] = evaluate(config, season, baseline, limit, coefficient)
            low, high = cases.values()
            for field in ('rewards', 'critic_values', 'observations_sha256', 'raw_reward_sum_before_reset'):
                assert low[field] == high[field], field
            assert all(c['optimizer_updates'] == 0 for c in cases.values())
            difference = np.abs(np.subtract(low['advantages'], high['advantages']))
            assert difference[-2] == difference[-1] == 0 and np.max(difference) > 0
            summaries[label] = {'season': season.manifest(), 'baseline_sha256': sha256(baseline_path),
                                'max_advantage_delta': float(np.max(difference)), 'cases': cases}
            write_json(run / f'{label}.json', summaries[label])
        write_json(run / 'verification.json', {'passed': True, 'real_dssat': True,
                   'experimental_only': True, 'research_ready': False, 'main_training_allowed': False,
                   'source': reference.relative_to(ROOT).as_posix(), 'critic': 'untrained, common seed 42',
                   'runs': summaries})
    except BaseException as error:
        write_json(run / 'failure.json', {'passed': False, 'error': repr(error), 'completed': list(summaries)})
        raise


if __name__ == '__main__':
    main()
