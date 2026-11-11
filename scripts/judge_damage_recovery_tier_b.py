"""Tier B comparison under configs/damage_recovery_tier_b.json (frozen 2026-11-10).

Runs the frozen 16 seasons x 10 treatments and applies the frozen criteria.
Nothing here selects stages, fractions, seasons, management or tolerances.
"""
import json
import math
import os
from pathlib import Path
from statistics import mean, pstdev
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from mars_env.artifacts import new_run, sha256, write_json
from mars_env.field_validation import relative_yield_verdict
from mars_env.leaf_diagnostics import LeafDiagnosticBackend

IRRIGATION_DAPS = (10, 20, 30, 40, 50, 60, 70, 80)   # 10 mm each, as diagnose_damage_matrix.py water=1
NITROGEN_BY_DAP = {40: 27, 45: 35, 80: 54}            # 116 kg N/ha, as diagnose_damage_matrix.py nitrogen=1
STAGE_RULES = {'V8': lambda s: float(s['vstage']) >= 8, 'V13': lambda s: float(s['vstage']) >= 13,
               'R1': lambda s: int(s['istage']) == 4}


def season(run, name, wgen_seed, stage, fraction):
    backend = LeafDiagnosticBackend()
    backend._runtime_log_path = str(run / 'native_logs' / f'{name}.log')
    pulse, max_lai = None, 0.0
    try:
        state = backend.reset(seed=123456, wgen_seed=wgen_seed)
        for _ in range(400):
            dap, date, apply = int(state['dap']), int(state['yrdoy']), 0.0
            planted = date >= backend.planting_yrdoy
            if planted and stage and pulse is None and STAGE_RULES[stage](state):
                apply = fraction
                pulse = {'date': date, 'dap': dap, 'vstage': float(state['vstage']), 'istage': int(state['istage']),
                         'lai_before': float(state['xlai'])}
            water = 10 if planted and dap in IRRIGATION_DAPS else 0
            nitrogen = NITROGEN_BY_DAP.get(dap, 0) if planted else 0
            after, done, outcome = backend.step_damage(water, nitrogen, apply)
            if apply:
                pulse['lai_after'] = float(after['xlai'])
            if planted and math.isfinite(float(after['xlai'])):
                max_lai = max(max_lai, float(after['xlai']))
            state = after
            if done:
                break
        else:
            raise RuntimeError('unterminated season')
        valid = outcome.reason in ('harvest', 'crop_failure') and (pulse is not None or not stage)
        return {'name': name, 'wgen_seed': wgen_seed, 'stage': stage, 'fraction': fraction, 'pulse': pulse,
                'yield_kg_ha': float(outcome.harvested_grain_kg_ha), 'reason': outcome.reason,
                'max_lai': max_lai, 'maturity': outcome.summary.get('MDAT'), 'valid': valid}
    finally:
        backend.close()


def main():
    tiers = json.loads((ROOT / 'configs/field_validation_tiers.json').read_text(encoding='utf-8'))
    pinned = tiers['tiers']['B_damage_recovery_relative_yield']['criterion']
    frozen_path = ROOT / pinned['frozen_config']
    assert sha256(frozen_path) == pinned['frozen_config_sha256'], 'frozen tier B config changed'
    frozen = json.loads(frozen_path.read_text(encoding='utf-8'))
    cells = [(c['stage'], c['defoliation_pct']) for c in frozen['reference']['cells']]
    seeds = frozen['simulation']['wgen_seeds']
    run = new_run(ROOT, 'damage_recovery_tier_b')
    (run / 'native_logs').mkdir()
    print(f'RUN_DIR={run}', flush=True)
    records = []
    try:
        for seed in seeds:
            control = season(run, f's{seed}_control', seed, None, 0.0)
            records.append(control)
            for stage, pct in cells:
                records.append(season(run, f's{seed}_{stage}_{pct}', seed, stage, pct / 100))
            print(seed, control['yield_kg_ha'], flush=True)
            write_json(run / 'records_partial.json', records)
        controls = {r['wgen_seed']: r for r in records if r['stage'] is None}
        controls_ok = all(r['reason'] == 'harvest' and r['yield_kg_ha'] > 0 for r in controls.values())
        valid_runs = sum(r['valid'] for r in records) if controls_ok else 0
        ratios, spread = {}, {}
        for stage, pct in cells:
            values = [r['yield_kg_ha'] / controls[r['wgen_seed']]['yield_kg_ha'] for r in records
                      if r['stage'] == stage and round(r['fraction'] * 100) == pct] if controls_ok else []
            assert not controls_ok or len(values) == len(seeds)
            ratios[stage, pct] = mean(values) if values else float('nan')
            spread[f'{stage}_{pct}'] = {'sd_across_seasons': pstdev(values), 'min': min(values), 'max': max(values),
                                        'crop_failures': sum(r['reason'] == 'crop_failure' for r in records
                                                             if r['stage'] == stage and round(r['fraction'] * 100) == pct)
                                        } if values else None
        verdict = relative_yield_verdict(frozen, ratios, valid_runs) if controls_ok else {
            'passed': False, 'all_runs_valid': False, 'reason': 'control season without positive harvest'}
        write_json(run / 'verification.json', {
            'passed': verdict['passed'], 'tier': 'B_damage_recovery_relative_yield',
            'gate': tiers['tiers']['B_damage_recovery_relative_yield']['gate'],
            'frozen_config': pinned['frozen_config'], 'frozen_config_sha256': pinned['frozen_config_sha256'],
            'criteria': frozen['criteria'], 'verdict': verdict, 'ratio_spread': spread,
            'valid_runs': valid_runs, 'total_runs': len(records),
            'control_yield_kg_ha': {str(k): v['yield_kg_ha'] for k, v in controls.items()},
            'control_max_lai': {str(k): v['max_lai'] for k, v in controls.items()},
            'records': records, 'image': os.environ.get('MARS_IMAGE_ID'),
            'leaf_run_location': os.environ.get('MARS_LEAF_RUN_LOCATION'),
            'scope_if_passed': frozen['scope_if_passed'], 'mapping_assumptions': frozen['mapping_assumptions'],
            'research_ready': False, 'main_training_allowed': False,
        })
        print(json.dumps({k: v for k, v in verdict.items() if k != 'cells'}, indent=2))
        for row in verdict.get('cells', []):
            print(row['stage'], row['defoliation_pct'], round(row['observed_ratio'], 3),
                  round(row['simulated_ratio'], 3), round(row['error'], 3))
    except BaseException as exc:
        write_json(run / 'failure.json', {'passed': False, 'error': repr(exc), 'completed_records': len(records)})
        raise


if __name__ == '__main__':
    main()
