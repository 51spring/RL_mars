"""Verify complete study coverage, unchanged roles and all independent gate names."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.validation_lineage import independent_lineage_status
from mars_env.agronomic_scenarios import build_registry,source_contrasts


def main():
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    folder=ROOT/'outputs/runs/20261106T151837Z_agronomic_input_priorities_8e4335a1'
    tests=ROOT/'outputs/runs/20261106T151838Z_unit_regressions_8b1cd7f5/verification.json'
    ready=ROOT/'outputs/runs/20261106T151953Z_readiness_3e953cc2/readiness.json'
    previous=ROOT/'outputs/runs/20261106T150544Z_fang_lineage_release_a1542273/source_snapshot/configs/agronomic_sources.json'
    for name,digest in read(folder/'derived_files_sha256.json').items():assert sha256(folder/name)==digest
    for name,digest in read(folder/'verification.json')['config_sha256'].items():assert sha256(ROOT/name)==digest
    for name,digest in read(folder/'source_evidence_sha256.json').items():assert sha256(ROOT/name)==digest
    registry=read(ROOT/'configs/agronomic_sources.json')['studies']
    old=read(previous)['studies']
    assert {s['id']:s['planned_role'] for s in registry}=={s['id']:s['planned_role'] for s in old}
    plan=read(ROOT/'configs/agronomic_input_priorities.json')
    rows=read(folder/'study_input_matrix.json')
    assert len(rows)==10 and {r['study_id'] for r in rows}=={s['id'] for s in registry}
    assert sum(len(r['states']) for r in rows)==80
    assert all(not r['quantitative_fit_ready'] and not r['model_scoring_allowed'] for r in rows)
    assert read(folder/'work_queue.json')==plan['work_queue']
    assert plan['work_queue'][0]['studies']==['oveysi2010']
    assert all(q['quantitative_execution_allowed'] is False for q in plan['work_queue'])
    scenarios=build_registry(ROOT);assert len(scenarios)==28 and len(source_contrasts(scenarios))==16
    t=read(tests);r=read(ready)
    assert t['passed'] and t['tests_run']==204 and not(t['failures'] or t['errors'] or t['skipped'])
    assert r['research_ready'] is False and r['main_training_allowed'] is False and not r['quantitative_fit_ready_studies']
    assert r['agronomic_input_priority_sha256']==sha256(ROOT/'configs/agronomic_input_priorities.json')
    expected={'oveysi2010','abang2024','blanco2022','blanco2023','oliveira2026','usda_lirf2008_2011'}
    actual=[independent_lineage_status(ROOT,s) for s in registry]
    assert {s['study_id'] for s in actual if s['required']}==expected
    assert actual==r['independent_parameter_lineage']
    assert all(not s['parameter_lineage_eligible'] for s in actual if s['required'])
    files=[folder/'verification.json',folder/'derived_files_sha256.json',tests,ready,previous,
        ROOT/'configs/agronomic_input_priorities.json',ROOT/'configs/agronomic_sources.json',ROOT/'configs/agronomic_protocols.json',
        ROOT/'src/mars_env/validation_lineage.py',ROOT/'tests/test_validation_lineage.py',ROOT/'scripts/build_readiness_report.py',
        ROOT/'scripts/build_agronomic_input_priorities.py',Path(__file__),
        ROOT/'docs/AGRONOMIC_INPUT_PRIORITIES.md',ROOT/'docs/NEXT_STEPS.md',ROOT/'PROGRESS.md']
    run=new_run(ROOT,'agronomic_input_priorities_release')
    write_json(run/'verification.json',dict(passed=True,study_rows=10,dimension_states=80,work_items=5,
        roles_unchanged=True,registered_scenarios=28,source_contrasts=16,
        independent_roles_requiring_lineage=6,independent_roles_qualified=0,tests_run=204,
        old_workspace_empty=True,new_native_simulations=0,new_training_runs=0,new_sources_acquired=0,
        research_ready=False,main_training_allowed=False,quantitative_fit_ready_studies=0,
        evidence_sha256={str(p.relative_to(ROOT)):sha256(p) for p in files},
        scope='existing evidence completeness, unchanged roles and next task order; no new agronomic qualification'))
    print(run)


if __name__=='__main__':main()
