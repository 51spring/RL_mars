"""Tiered field-validation judgments from frozen replay outputs."""
from math import sqrt
from statistics import mean


def _ranks(values):
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    start = 0
    while start < len(order):
        end = start
        while end + 1 < len(order) and values[order[end + 1]] == values[order[start]]:
            end += 1
        for index in order[start:end + 1]:
            ranks[index] = (start + end) / 2 + 1
        start = end + 1
    return ranks


def _pearson(x, y):
    mx, my = mean(x), mean(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx, syy = sum((a - mx) ** 2 for a in x), sum((b - my) ** 2 for b in y)
    if not sxx or not syy:
        raise ValueError('constant series')
    return sxy / sqrt(sxx * syy)


def yield_agreement(observed, simulated):
    """Agreement statistics for paired treatment-mean yields."""
    observed, simulated = [float(v) for v in observed], [float(v) for v in simulated]
    if len(observed) != len(simulated) or len(observed) < 3:
        raise ValueError('need at least three observed/simulated pairs')
    obs_mean = mean(observed)
    if obs_mean <= 0:
        raise ValueError('observed mean must be positive')
    errors = [s - o for o, s in zip(observed, simulated)]
    rmse = sqrt(mean(e * e for e in errors))
    sxx = sum((o - obs_mean) ** 2 for o in observed)
    if not sxx:
        raise ValueError('constant series')
    slope = sum((o - obs_mean) * (s - mean(simulated)) for o, s in zip(observed, simulated)) / sxx
    potential = sum((abs(s - obs_mean) + abs(o - obs_mean)) ** 2 for o, s in zip(observed, simulated))
    return {
        'count': len(observed), 'observed_mean': obs_mean, 'bias': mean(errors), 'rmse': rmse,
        'nrmse_pct': 100 * rmse / obs_mean, 'bias_pct': 100 * mean(errors) / obs_mean,
        'willmott_d': 1 - sum(e * e for e in errors) / potential,
        'pearson_r': _pearson(observed, simulated),
        'spearman_rho': _pearson(_ranks(observed), _ranks(simulated)),
        'slope_simulated_on_observed': slope,
        'range_ratio': (max(simulated) - min(simulated)) / (max(observed) - min(observed)),
    }


def classify_nrmse(nrmse_pct, criterion):
    """Class label and pass flag; thresholds come only from the frozen config."""
    label = 'poor'
    for name, limit in sorted(criterion['classes_max_pct'].items(), key=lambda item: item[1]):
        if nrmse_pct <= limit:
            label = name
            break
    return {'class': label, 'passed': nrmse_pct <= criterion['pass_max_pct'],
            'pass_max_pct': criterion['pass_max_pct'],
            'margin_to_next_worse_class_pct': min(
                (limit - nrmse_pct for limit in criterion['classes_max_pct'].values() if limit >= nrmse_pct),
                default=None)}


def relative_yield_verdict(frozen, simulated_ratios, valid_runs):
    """Tier B verdict from the frozen damage config and simulated mean ratios.

    simulated_ratios maps (stage, defoliation_pct) to the across-season mean of
    damaged / same-season control yield.
    """
    reference, criteria = frozen['reference'], frozen['criteria']
    check = reference['no_injury_check_yield']
    cells = [(c['stage'], c['defoliation_pct'], c['yield'] / check) for c in reference['cells']]
    if set(simulated_ratios) != {(stage, pct) for stage, pct, _ in cells}:
        raise ValueError('simulated cells differ from the frozen reference cells')
    tolerance = criteria['tolerance_abs_ratio']
    rows = [{'stage': stage, 'defoliation_pct': pct, 'observed_ratio': observed,
             'simulated_ratio': float(simulated_ratios[stage, pct]),
             'error': float(simulated_ratios[stage, pct]) - observed,
             'within_tolerance': abs(float(simulated_ratios[stage, pct]) - observed) <= tolerance}
            for stage, pct, observed in cells]
    rmse = sqrt(mean(row['error'] ** 2 for row in rows))
    top = [simulated_ratios[stage, 99] for stage in ('V8', 'V13', 'R1')]
    ordered = top[0] > top[1] > top[2]
    complete = valid_runs == frozen['simulation']['runs']
    return {'passed': bool(rmse <= criteria['gating']['rmse_ratio_max'] and ordered and complete),
            'rmse_ratio': rmse, 'timing_order_at_99pct': ordered, 'all_runs_valid': complete,
            'max_abs_error': max(abs(row['error']) for row in rows),
            'cells_outside_tolerance': [[row['stage'], row['defoliation_pct']] for row in rows
                                        if not row['within_tolerance']],
            'cells': rows}


def tier_gate_status(tiers, judgment=None, damage_judgment=None):
    """Pending, satisfied and limitation gates implied by the tier config.

    Fail closed: tier A is satisfied only by a judgment that names the frozen
    primary case, passed, and matches the pinned source hash. Tier B is
    satisfied only by a passed judgment made under the pinned frozen criteria.
    """
    a = tiers['tiers']['A_undamaged_water_response']
    b = tiers['tiers']['B_damage_recovery_relative_yield']
    c = tiers['tiers']['C_not_field_verifiable']
    primary = a['primary']
    ok = (isinstance(judgment, dict) and judgment.get('passed') is True
          and judgment.get('case_id') == primary['id']
          and judgment.get('source_run_sha256') == primary['source_run_sha256']
          and judgment.get('criterion') == a['criterion'])
    pending, satisfied = [], []
    (satisfied if ok else pending).append(a['gate'])
    frozen_sha = (b.get('criterion') or {}).get('frozen_config_sha256')
    b_ok = (bool(frozen_sha) and isinstance(damage_judgment, dict) and damage_judgment.get('passed') is True
            and damage_judgment.get('frozen_config_sha256') == frozen_sha)
    (satisfied if b_ok else pending).append(b['gate'])
    return {'pending': pending, 'satisfied': satisfied, 'documented_limitations': sorted(c['items'])}
