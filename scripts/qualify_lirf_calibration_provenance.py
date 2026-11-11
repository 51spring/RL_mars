"""Check coefficient transcription, role restrictions and immutable provenance."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256


def main():
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    folder=ROOT/'outputs/runs/20261106T144720Z_lirf_calibration_provenance_94510be8'
    papers=ROOT/'outputs/runs/20261106T144434Z_lirf_calibration_sources_a5f2fc47'
    tests=ROOT/'outputs/runs/20261106T144849Z_unit_regressions_72e11b1e/verification.json'
    ready=ROOT/'outputs/runs/20261106T144929Z_readiness_cd053a37/readiness.json'
    report=read(folder/'verification.json');assert report['passed']
    for name,digest in read(folder/'derived_files_sha256.json').items():assert sha256(folder/name)==digest
    for name,digest in report['evidence_sha256'].items():assert sha256(ROOT/name)==digest
    for item in read(papers/'verification.json')['files']:assert sha256(papers/item['file'])==item['sha256']
    matrix=read(folder/'coefficient_comparisons.json')
    keys=['P1','P2','P5','G2','G3','PHINT']
    assert list(matrix['package'])==keys
    assert list(matrix['package'].values())==[245.6,.156,704.4,994.,6.239,52.88]
    initial=next(c for c in matrix['comparisons'] if c['source']=='fang2017_table2_initial')
    assert list(initial['coefficients'].values())==[245.6,.1562,704.4,994.1,6.239,52.89]
    assert initial['exact_numeric_matches']==3
    for entry in matrix['comparisons']:
        assert entry['numerical_similarity_proves_identity_or_calibration_independence'] is False
        for k in keys:assert abs(matrix['package'][k]-entry['coefficients'][k]-entry['package_minus_source'][k])<1e-12
    docs=read(folder/'source_document_pages.json')
    for doc in docs:assert sha256(ROOT/doc['file'])==doc['sha256']
    fang=next(d for d in docs if d['file'].endswith('Fang2017.pdf'))
    table=next(p['text'] for p in fang['pages'] if p['physical_page']==7)
    assert all(token in table for token in ['245.6','0.1562','704.4','994.1','6.239','52.89'])
    ledger=read(folder/'publication_data_exposure.json')
    assert len(ledger)==3 and ledger[0]['untouched_whole_study_validation_established'] is False
    assert ledger[1]['results_pool_calibration_and_validation'] is True
    assert ledger[2]['proves_exact_package_lineage'] is False
    role=read(folder/'validation_role_contract.json')
    assert role['role_status']=='conditional_candidate_not_qualified'
    assert role['independent_validation_allowed'] is False and role['whole_study_holdout_changed'] is False
    assert role['calibration_on_LIRF_outcomes_allowed'] is False and role['new_independent_studies_added']==0
    sources=read(ROOT/'configs/agronomic_sources.json')['studies'];assert len(sources)==10
    s=next(s for s in sources if s['id']=='usda_lirf2008_2011')
    assert s['planned_role']==role['planned_role'] and s['role_status']==role['role_status']
    assert s['independent_validation_allowed'] is False and s['quantitative_fit_ready'] is False
    assert s['cultivar_calibration_independence_verified'] is False and s['exact_package_calibration_lineage_verified'] is False
    specification=read(ROOT/'docs/LIRF_MISSING_DATA_SPEC.json')
    assert any(r['id']=='exact_parameter_lineage' for r in specification['requirements'])
    assert specification['contact_authorized'] is False and specification['messages_sent']==0
    t=read(tests);r=read(ready)
    assert t['passed'] and t['tests_run']==199 and not(t['failures'] or t['errors'] or t['skipped'])
    assert r['research_ready'] is False and r['main_training_allowed'] is False and not r['quantitative_fit_ready_studies']
    files=[folder/'verification.json',folder/'derived_files_sha256.json',papers/'verification.json',tests,ready,
        ROOT/'scripts/fetch_lirf_calibration_sources.py',ROOT/'scripts/audit_lirf_calibration_provenance.py',Path(__file__),
        ROOT/'configs/lirf_translation_contract.json',ROOT/'configs/agronomic_sources.json',
        ROOT/'docs/LIRF_CALIBRATION_PROVENANCE.md',ROOT/'docs/LIRF_MISSING_DATA_SPEC.json',ROOT/'docs/NEXT_STEPS.md',ROOT/'PROGRESS.md']
    run=new_run(ROOT,'lirf_calibration_provenance_release')
    write_json(run/'verification.json',dict(passed=True,coefficient_variants=5,publication_exposure_ledgers=3,
        exact_package_fang_initial_matches=3,independent_validation_allowed=False,study_split_changed=False,
        source_sha256_unchanged=True,old_workspace_empty=True,tests_run=199,new_native_simulations=0,new_training_runs=0,
        research_ready=False,main_training_allowed=False,quantitative_fit_ready_studies=0,
        evidence_sha256={str(p.relative_to(ROOT)):sha256(p) for p in files},
        scope='transcribed/source coefficient and exposure-role consistency; exact package lineage still unverified'))
    print(run)


if __name__=='__main__':main()
