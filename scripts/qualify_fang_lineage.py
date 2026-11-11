"""Verify chapter retrieval limits, non-promotion gate and source preservation."""
import copy
import json
from pathlib import Path
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.validation_lineage import independent_lineage_status


def main():
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    folder=ROOT/'outputs/runs/20261106T150015Z_fang_lineage_audit_0ab94133'
    acquisition=ROOT/'outputs/runs/20261106T145526Z_fang_lineage_sources_00e0e4ee'
    handle=ROOT/'outputs/runs/20261106T150207Z_fang_handle_followup_2b58cca2'
    tests=ROOT/'outputs/runs/20261106T150107Z_unit_regressions_152dae62/verification.json'
    ready=ROOT/'outputs/runs/20261106T150245Z_readiness_9e5411d4/readiness.json'
    for name,digest in read(folder/'derived_files_sha256.json').items():assert sha256(folder/name)==digest
    for name,digest in read(folder/'verification.json')['source_reports_sha256'].items():assert sha256(ROOT/name)==digest
    for name,digest in read(folder/'verification.json')['source_files_sha256'].items():assert sha256(ROOT/name)==digest
    for item in read(acquisition/'verification.json')['files']:
        if item['acquired']:assert sha256(acquisition/item['file'])==item['sha256']
    h=read(handle/'verification.json');assert h['passed'] and not h['fulltext_pdf_acquired']
    assert sha256(handle/h['file'])==h['sha256'] and 'search.nal.usda.gov' in h['final_url']
    chapter=read(folder/'chapter_evidence_status.json')
    assert chapter['doi']=='10.2134/advagricsystmodel5.c1' and chapter['chapter_fulltext_acquired'] is False
    assert chapter['coefficient_vector'] is None and chapter['fulltext_access_bypass_attempted'] is False
    matrix=read(folder/'related_coefficient_comparisons.json')
    assert all(not c['exact_full_row_match'] and len(c['matching_keys'])==3 for c in matrix['comparisons'])
    assert set(matrix['comparisons'][0]['matching_keys'])!=set(matrix['comparisons'][1]['matching_keys'])
    for c in matrix['comparisons']:
        for key,value in c['coefficients'].items():assert abs(matrix['package'][key]-value-c['package_minus_source'][key])<1e-12
    source=ROOT/'outputs/runs/20261106T083612Z_lirf_public_sources_d90f9eab'
    for item in read(source/'verification.json')['files']:assert sha256(source/item['file'])==item['sha256']
    sources=read(ROOT/'configs/agronomic_sources.json')['studies'];assert len(sources)==10
    study=next(s for s in sources if s['id']=='usda_lirf2008_2011')
    actual=independent_lineage_status(ROOT,study);assert actual['required'] and actual['parameter_lineage_eligible'] is False
    forged=copy.deepcopy(study)
    for field in ('exact_package_calibration_lineage_verified','cultivar_calibration_independence_verified','independent_validation_allowed'):forged[field]=True
    negative=independent_lineage_status(ROOT,forged)
    assert negative['parameter_lineage_eligible'] is False
    assert 'evidence_whole_study_independence_verified' in negative['blockers']
    forged['calibration_provenance_sha256']='0'*64
    assert 'evidence_sha256_mismatch' in independent_lineage_status(ROOT,forged)['blockers']
    t=read(tests);r=read(ready)
    assert t['passed'] and t['tests_run']==203 and not(t['failures'] or t['errors'] or t['skipped'])
    assert r['research_ready'] is False and r['main_training_allowed'] is False and not r['quantitative_fit_ready_studies']
    assert 'independent_parameter_lineage' in r['pending_gates']
    assert next(s for s in r['independent_parameter_lineage'] if s['study_id']==study['id'])==actual
    files=[folder/'verification.json',folder/'derived_files_sha256.json',acquisition/'verification.json',handle/'verification.json',tests,ready,
        ROOT/'src/mars_env/validation_lineage.py',ROOT/'tests/test_validation_lineage.py',
        ROOT/'scripts/fetch_fang_lineage_sources.py',ROOT/'scripts/audit_fang_lineage.py',Path(__file__),ROOT/'scripts/build_readiness_report.py',
        ROOT/'configs/lirf_translation_contract.json',ROOT/'configs/agronomic_sources.json',
        ROOT/'docs/FANG_LINEAGE_FOLLOWUP.md',ROOT/'docs/NEXT_STEPS.md',ROOT/'PROGRESS.md']
    run=new_run(ROOT,'fang_lineage_release')
    shutil.copy2(ROOT/'outputs/lirf-zhang2021-04.png',run/'Zhang2021-page04.png')
    write_json(run/'negative_gate_controls.json',dict(actual=actual,forged_registry_flags=negative,source_files_mutated=False))
    write_json(run/'verification.json',dict(passed=True,tests_run=203,chapter_fulltext_acquired=False,
        related_exact_package_rows=0,forged_registry_flags_rejected=True,tampered_hash_rejected=True,
        independent_validation_allowed=False,study_split_changed=False,source_sha256_unchanged=True,
        old_workspace_empty=True,new_native_simulations=0,new_training_runs=0,
        research_ready=False,main_training_allowed=False,quantitative_fit_ready_studies=0,
        evidence_sha256={str(p.relative_to(ROOT)):sha256(p) for p in files},
        figure_sha256=sha256(run/'Zhang2021-page04.png'),
        scope='bounded lineage search and evidence-pinned readiness gate; original chapter and exact parameter lineage remain unverified'))
    print(run)


if __name__=='__main__':main()
