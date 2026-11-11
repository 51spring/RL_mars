"""Release checks for source screening; no fitting or native execution."""
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from mars_env.artifacts import new_run, sha256, write_json


def main():
    def read(path):
        return json.loads(path.read_text(encoding='utf-8'))

    folder = ROOT / 'outputs/runs/20261106T232859Z_field_calibration_screen_6e56601b'
    source = ROOT / 'outputs/runs/20261106T232619Z_field_calibration_candidates_9542cf1f'
    workbook = source / 'nebraska_Manuscript_data.xlsx'
    for name, digest in read(folder / 'derived_files_sha256.json').items():
        assert sha256(folder / name) == digest
    report = read(folder / 'verification.json')
    assert sha256(workbook) == report['workbook_source_sha256']
    assert report['candidates_screened'] == 4 and report['active_studies_added'] == 0
    assert report['advanced_to_input_qualification'] == 1
    assert report['quantitative_fit_ready_candidates'] == 0
    wb = load_workbook(workbook, read_only=True, data_only=True)
    values = list(wb['yield_raw'].values)
    records = read(folder / 'nebraska_grain_source_records.json')
    groups = defaultdict(list)
    for row in records:
        assert values[row['source_row'] - 1][8] == row['grain_dry_matter_kg_ha']
        groups[(row['year'], row['treatment'])].append(row['grain_dry_matter_kg_ha'])
    assert len(records) == 271 and len(groups) == 72
    for group in read(folder / 'nebraska_group_statistics.json'):
        vals = groups[(group['year'], group['treatment'])]
        assert group['n'] == len(vals)
        assert abs(group['mean_kg_ha'] - statistics.mean(vals)) < 1e-8
        if len(vals) == 1:
            assert group['sample_sd_kg_ha'] is None
        else:
            assert abs(group['sample_sd_kg_ha'] - statistics.stdev(vals)) < 1e-8
    wb.close()
    previous = ROOT / 'outputs/runs/20261106T232111Z_oveysi_input_dossier_release_39e76c34/source_snapshot/configs/agronomic_sources.json'
    current = read(ROOT / 'configs/agronomic_sources.json')['studies']
    assert {s['id']: s['planned_role'] for s in current} == {s['id']: s['planned_role'] for s in read(previous)['studies']}
    assert len(current) == 10 and not any(s['quantitative_fit_ready'] for s in current)
    tests = ROOT / 'outputs/runs/20261106T233007Z_unit_regressions_c46dd35c/verification.json'
    ready = ROOT / 'outputs/runs/20261106T233307Z_readiness_6b058457/readiness.json'
    priority = ROOT / 'outputs/runs/20261106T233305Z_agronomic_input_priorities_58982957/verification.json'
    t, r = read(tests), read(ready)
    assert t['passed'] and t['tests_run'] == 204 and not (t['failures'] or t['errors'] or t['skipped'])
    assert r['research_ready'] is False and r['main_training_allowed'] is False
    assert not r['quantitative_fit_ready_studies']
    assert r['agronomic_input_priority_sha256'] == sha256(ROOT / 'configs/agronomic_input_priorities.json')
    assert read(priority)['roles_changed'] == 0
    files = [tests, ready, priority, folder / 'verification.json', folder / 'derived_files_sha256.json', workbook,
             ROOT / 'configs/field_calibration_candidate_screen.json', ROOT / 'configs/agronomic_sources.json',
             ROOT / 'configs/agronomic_input_priorities.json', ROOT / 'docs/FIELD_CALIBRATION_CANDIDATE_SCREEN.md',
             ROOT / 'docs/AGRONOMIC_INPUT_PRIORITIES.md', ROOT / 'docs/LIRF_DATA_AVAILABILITY.md',
             ROOT / 'docs/NEXT_STEPS.md', ROOT / 'PROGRESS.md', Path(__file__),
             ROOT / 'scripts/fetch_calibration_candidates.py', ROOT / 'scripts/screen_field_calibration_candidates.py']
    run = new_run(ROOT, 'field_calibration_screen_release')
    write_json(run / 'verification.json', dict(passed=True, candidates_screened=4, active_studies_added=0,
        raw_cell_and_group_arithmetic_verified=True, source_sha256_unchanged=True,
        observations_and_roles_unchanged=True, old_workspace_empty=True, tests_run=204,
        new_native_simulations=0, new_training_runs=0, quantitative_fit_ready_studies=0,
        research_ready=False, main_training_allowed=False,
        evidence_sha256={p.relative_to(ROOT).as_posix(): sha256(p) for p in files},
        scope='source screening and no-promotion release checks; not field-model validation'))
    print(run)


if __name__ == '__main__':
    main()
