"""Independent original-cell/readiness/provenance checks for partial LIRF evidence."""
import json
from pathlib import Path
import statistics
import sys
import openpyxl

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256


def main():
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    evidence=ROOT/'outputs/runs/20261106T135234Z_lirf_evidence_ledger_eaaf34b5'
    sources=ROOT/'outputs/runs/20261106T083612Z_lirf_public_sources_d90f9eab'
    tests=ROOT/'outputs/runs/20261106T135314Z_unit_regressions_9a6ec3e4/verification.json'
    ready=ROOT/'outputs/runs/20261106T135324Z_readiness_90cee1f2/readiness.json'
    for name,digest in read(evidence/'derived_files_sha256.json').items():
        assert sha256(evidence/name)==digest,name
    for item in read(sources/'verification.json')['files']:
        assert sha256(sources/item['file'])==item['sha256'],item['file']
    report=read(evidence/'verification.json')
    for name,digest in report['source_evidence'].items():assert sha256(ROOT/name)==digest
    for name,digest in report['code_definitions_sha256'].items():assert sha256(ROOT/name)==digest
    observations=read(evidence/'daily_mean_air_observations.json')
    assert len(observations)==1461
    books={}
    for observation in observations:
        f=observation['source_file']
        if f not in books:books[f]=openpyxl.load_workbook(sources/f,data_only=True,read_only=True)
    # Read worksheets once: repeated random access on streaming XLSX is expensive.
    values={f:{c.coordinate:c.value for row in w['Daily'] for c in row if c.value is not None} for f,w in books.items()}
    for observation in observations:
        assert values[observation['source_file']][observation['cell']]==observation['tmean_c']
    climate=read(evidence/'temperature_descriptions.json')
    assert abs(statistics.fmean(r['tmean_c'] for r in observations)-climate['pooled_daily_mean_air_c'])<1e-12
    assert climate['native_tav_tamp_selected'] is False
    assert climate['long_term_climate_normals'] is False
    soil=read(evidence/'d22_soil_candidate.json')
    w=openpyxl.load_workbook(sources/'LIRF_Soils.xlsx',data_only=True,read_only=True)
    cells={c.coordinate:c.value for row in w['Soil Texture'] for c in row if c.value is not None}
    for horizon in soil['horizons']:
        for target,field in [('top','top_cm'),('bottom','bottom_cm'),('sand','sand_percent'),('clay','clay_percent'),('silt','silt_percent'),('ph','ph_saturated_paste')]:
            assert cells[horizon['cells'][target]]==horizon[field]
    assert len(soil['horizons'])==8 and soil['profile_depth_cm']==182.88
    assert soil['plot_yield_reference']['plot']=='D22' and soil['plot_yield_reference']['treatment']==1
    assert soil['plot_yield_reference']['block']==2 and soil['plot_yield_reference']['year']==2008
    assert soil['full_native_profile_ready'] is False and soil['ph_method_equivalence_verified'] is False
    ledger=read(evidence/'input_difference_ledger.json')
    assert len({r['id'] for r in ledger})==len(ledger)==19
    assert all(r['automatic_field_replacement_allowed'] is False for r in ledger)
    t=read(tests);r=read(ready)
    assert t['passed'] and t['tests_run']==185 and not(t['failures'] or t['errors'] or t['skipped'])
    assert r['research_ready'] is False and r['main_training_allowed'] is False
    assert r['public_studies']==10 and not r['quantitative_fit_ready_studies']
    contract=read(ROOT/'configs/lirf_translation_contract.json')
    assert contract['native_ready'] is False and contract['field_evidence_ledger']['evidence']==str((evidence/'verification.json').relative_to(ROOT)).replace('\\','/')
    files=[evidence/'verification.json',evidence/'derived_files_sha256.json',tests,ready,
        ROOT/'src/mars_env/lirf_evidence.py',ROOT/'tests/test_lirf_evidence.py',
        ROOT/'scripts/build_lirf_evidence_ledger.py',Path(__file__),
        ROOT/'configs/agronomic_sources.json',ROOT/'configs/lirf_translation_contract.json',
        ROOT/'docs/LIRF_EVIDENCE_LEDGER.md',ROOT/'docs/NEXT_STEPS.md',ROOT/'PROGRESS.md']
    run=new_run(ROOT,'lirf_evidence_ledger_release')
    write_json(run/'verification.json',dict(passed=True,original_cells_verified=1461+8*6,
        ledger_items=19,tests_run=185,source_sha256_unchanged=True,old_workspace_empty=True,
        native_parameter_replacements=0,new_native_simulations=0,new_training_runs=0,
        research_ready=False,main_training_allowed=False,quantitative_fit_ready_studies=0,
        evidence_sha256={str(p.relative_to(ROOT)):sha256(p) for p in files},
        scope='original-source cell, artifact hash and conservative gate consistency; no agronomic validation'))
    print(run)


if __name__=='__main__':main()
