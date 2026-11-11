"""Run paired synthetic FAW parameter checks with the production state equations."""
from collections import defaultdict
import json
from pathlib import Path
from statistics import fmean
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from mars_env.artifacts import new_run, write_json
from mars_env.exogenous import stream
from mars_env.pests import DamageSurvey, PestParameters, PestState


def simulate(config, pest, temperatures, uniforms, noise, spray_days):
    inputs = {**config, 'pest': pest}
    parameters = PestParameters.from_config(inputs)
    survey = DamageSurvey.from_config(inputs)
    state = PestState()
    densities, losses, readings = [], [], []
    arrivals = 0
    for day, (temperature, uniform, error) in enumerate(zip(temperatures, uniforms, noise, strict=True)):
        survey = survey.morning(day, error)
        if survey.reading is not None and survey.reading.day == day:
            readings.append(survey.reading.value)
        arrival = pest['arrival_amplitude'] if uniform < pest['arrival_probability'] else 0
        arrivals += bool(arrival)
        state, loss, _ = state.advance(day, temperature, arrival, day in spray_days, parameters)
        survey = survey.complete_day(day, loss)
        densities.append(state.density)
        losses.append(loss)
    assert all(0 <= x <= 1 for x in (*densities, *losses, *readings))
    return {
        'arrivals': arrivals,
        'mean_density': fmean(densities),
        'peak_density': max(densities),
        'mean_daily_leaf_loss': fmean(losses),
        'mean_survey': fmean(readings),
        'survey_at_boundary_fraction': fmean(x in (0, 1) for x in readings),
        'survey_count': len(readings),
    }


def main():
    config = yaml.safe_load((ROOT / 'configs/proposal_v2.yaml').read_text(encoding='utf-8'))
    spec = json.loads((ROOT / 'configs/faw_technical_sensitivity.json').read_text(encoding='utf-8-sig'))
    assert spec['scope'] == 'technical_diagnostic_only'
    assert not spec['research_ready'] and not spec['main_training_allowed']
    assert all(config['pest'][key] is None for key in spec['baseline_overrides'])
    horizon = spec['horizon_days']
    base = {**config['pest'], **spec['baseline_overrides']}
    cases = {'baseline': base}
    for axis, levels in spec['axes'].items():
        for level, overrides in levels.items():
            assert overrides.keys() <= base.keys()
            cases[f'{axis}/{level}'] = {**base, **overrides}
    rows = []
    aggregates = defaultdict(list)
    for profile, cycle in spec['synthetic_temperature_cycles_c'].items():
        temperatures = [cycle[day % len(cycle)] for day in range(horizon)]
        for replicate in range(spec['replicates']):
            uniforms = stream(spec['base_seed'], replicate, 'pest_arrival').random(horizon)
            noise = stream(spec['base_seed'], replicate, 'survey_noise').standard_normal(horizon)
            paired = {case: simulate(config, pest, temperatures, uniforms, noise, spec['spray_days'])
                      for case, pest in cases.items()}
            baseline = paired['baseline']
            assert paired['arrival_probability/zero']['peak_density'] == 0
            assert paired['arrival_probability/zero']['mean_daily_leaf_loss'] == 0
            assert paired['efficacy/full']['mean_density'] <= baseline['mean_density'] <= paired['efficacy/zero']['mean_density']
            for case in ('survey_noise/zero', 'survey_noise/stress', 'alpha/half', 'alpha/double'):
                assert paired[case]['mean_density'] == baseline['mean_density']
            assert all(row['survey_count'] == len(range(0, horizon, config['management']['survey_interval_days']))
                       for row in paired.values())
            for case, metrics in paired.items():
                rows.append({'profile': profile, 'replicate': replicate, 'case': case, **metrics})
                aggregates[profile, case].append({key: value - baseline[key] for key, value in metrics.items()})
    summaries = [
        {'profile': profile, 'case': case, 'mean_paired_delta': {
            metric: fmean(delta[metric] for delta in deltas) for metric in deltas[0]
        }} for (profile, case), deltas in aggregates.items()
    ]
    run = new_run(ROOT, 'faw_technical_sensitivity')
    write_json(run / 'sensitivity.json', {
        'scope': spec['scope'],
        'research_ready': False,
        'main_training_allowed': False,
        'scenarios': cases,
        'rows': rows,
        'paired_summaries': summaries,
    })
    print(run.relative_to(ROOT).as_posix(), len(rows), 'trajectory runs')


if __name__ == '__main__':
    main()
