"""Tier A judgment of SIAZ 1995 water response from the frozen 75 cm replay.

Reads stored native outputs only; runs no simulation and selects no input.
"""
import json
from pathlib import Path
import re
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from mars_env.artifacts import new_run, sha256, write_json
from mars_env.field_validation import classify_nrmse, yield_agreement


def main():
    tiers = json.loads((ROOT / 'configs/field_validation_tiers.json').read_text(encoding='utf-8'))
    tier = tiers['tiers']['A_undamaged_water_response']
    primary, criterion, fixed = tier['primary'], tier['criterion'], tier['primary']['fixed_inputs']
    source = ROOT / primary['source_run']
    assert sha256(source) == primary['source_run_sha256'], 'frozen replay output changed'
    replay = json.loads(source.read_text(encoding='utf-8'))
    rows = [r for r in replay['records'] if r['profile'] == fixed['coefficient_profile']
            and r['experiment'] == primary['experiment'] and r['role'] == 'evaluation']
    assert replay['passed'] and len(rows) == len(replay['records']) == primary['treatments']
    assert sorted(r['treatment'] for r in rows) == list(range(1, primary['treatments'] + 1))
    assert all(r['year'] == primary['evaluation_year'] for r in rows)
    native = source.parent / 'native' / fixed['coefficient_profile'] / primary['experiment']
    for r in rows:
        overview = (native / f"t{r['treatment']:02}" / 'OVERVIEW.OUT').read_text(encoding='latin-1')
        assert re.search(rf"ROW SPACING\s*:\s*{fixed['row_spacing_cm']}\.", overview), r['treatment']
    card = replay['cards'][fixed['coefficient_profile']]
    assert card.split()[-6:] == ['258.1', '0.326', '741.7', '639.6', '6.183', '66.12'] and 'IB0001' in card

    rows.sort(key=lambda r: r['treatment'])
    observed = [float(r['observed']['HWAM']) for r in rows]
    simulated = [float(r['summary']['HWAM']) for r in rows]
    metrics = yield_agreement(observed, simulated)
    stored = replay['metrics'][fixed['coefficient_profile']]['evaluation']
    assert abs(metrics['rmse'] - stored['yield_rmse_kg_ha']) < 1e-9
    assert abs(metrics['bias'] - stored['yield_bias_kg_ha']) < 1e-9
    verdict = classify_nrmse(metrics['nrmse_pct'], criterion)
    maturity = [int(r['summary']['MDAT']) % 1000 - int(r['observed']['MDAT']) for r in rows]

    run = new_run(ROOT, 'siaz1995_water_response_judgment', image_id=replay['image'])
    write_json(run / 'verification.json', {
        'passed': verdict['passed'], 'case_id': primary['id'], 'tier': 'A_undamaged_water_response',
        'gate': tier['gate'], 'scope': 'treatment-mean dry grain yield, independent year at the calibration site',
        'criterion': criterion, 'verdict': verdict, 'metrics_kg_ha': metrics,
        'maturity_day_error_simulated_minus_observed': maturity,
        'pairs': [{'treatment': r['treatment'], 'code': r['observed']['TNAM'], 'irrigation_mm': r['summary']['IRCM'],
                   'observed': o, 'simulated': s, 'error': s - o} for r, o, s in zip(rows, observed, simulated)],
        'fixed_inputs': fixed, 'cultivar_card': card, 'open_input_caveats': primary['open_input_caveats'],
        'source_run': primary['source_run'], 'source_run_sha256': primary['source_run_sha256'],
        'binary_sha256': replay['binary_sha256'], 'image': replay['image'], 'data_commit': replay['data_commit'],
        'new_simulations': 0, 'claim_scope': tiers['claim_scope'],
        'independence_wording': tiers['independence_wording'],
        'research_ready': False, 'main_training_allowed': False,
    })
    print(run)
    print(json.dumps({'verdict': verdict, 'metrics': metrics, 'maturity_error_days': maturity}, indent=2))


if __name__ == '__main__':
    main()
