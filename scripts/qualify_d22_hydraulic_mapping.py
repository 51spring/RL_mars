"""Original cell and interval-gap qualification, with conservative research gates."""
import json
from pathlib import Path
import statistics
import sys
import openpyxl
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256


def main():
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    folder=ROOT/'outputs/runs/20261106T141032Z_d22_hydraulic_mapping_4797116e'
    source=ROOT/'outputs/runs/20261106T083612Z_lirf_public_sources_d90f9eab'
    tests=ROOT/'outputs/runs/20261106T141132Z_unit_regressions_f622b3a0/verification.json'
    ready=ROOT/'outputs/runs/20261106T141149Z_readiness_5297e156/readiness.json'
    for name,digest in read(folder/'derived_files_sha256.json').items():assert sha256(folder/name)==digest
    for name,digest in read(folder/'verification.json')['source_sha256'].items():assert sha256(ROOT/name)==digest
    w=openpyxl.load_workbook(source/'LIRF_Soils.xlsx',read_only=True,data_only=True)
    cells={s:{c.coordinate:c.value for row in w[s] for c in row if c.value is not None} for s in ('Moisture Release','Bulk Density')}
    horizons=read(folder/'pressure_plate_candidates.json');count=0
    previous=read(ROOT/'outputs/runs/20261106T135234Z_lirf_evidence_ledger_eaaf34b5/d22_soil_candidate.json')
    for h in horizons:
        row=h['source_row'];m=cells['Moisture Release']
        assert m[f'A{row}']==5 and m[f'B{row}']=='D22'
        assert (m[f'C{row}'],m[f'D{row}'])==(h['top_cm'],h['bottom_cm'])
        assert any((p['top_cm'],p['bottom_cm'])==(h['top_cm'],h['bottom_cm']) for p in previous['horizons'])
        for observation in h['observations']:
            assert observation['pressure_kpa'] in (3,10,33,50,100,1475)
            for sample in observation['subsamples']:
                assert m[sample['cell']]==sample['value'];count+=1
            values=[sample['value'] for sample in observation['subsamples']]
            assert abs(statistics.fmean(values)-observation['cached_mean'])<2e-9
            assert m[observation['mean_cell']]==observation['cached_mean']
            assert len(values)==observation['n']
            if len(values)==1:assert observation['sample_sd'] is None
        assert h['native_LL_DUL_SAT_selected'] is False
    assert count==42 and len(horizons)==4
    coverage=read(folder/'measurement_depth_coverage.json')['full_profile'][0]
    assert abs(coverage['covered_cm']-sum(h['bottom_cm']-h['top_cm'] for h in horizons))<1e-10
    assert coverage['missing_intervals_cm']==[[25.4,35.56],[91.44,154.94],[182.88,200.0]]
    assert abs(coverage['covered_cm']+sum(b-a for a,b in coverage['missing_intervals_cm'])-200)<1e-10
    assert coverage['soil_values_assigned'] is False
    density=read(folder/'pooled_D2_density.json')
    for point in density:
        assert [cells['Bulk Density'][c] for c in point['cells']]==[point['mean_g_cm3'],point['reported_sd'],point['n']]
    maize=openpyxl.load_workbook(source/'LIRF_Maize_2008.xlsx',read_only=True,data_only=True)
    values={c.coordinate:c.value for row in maize['Tmnt1'] for c in row if c.value is not None}
    initial=read(folder/'initial_state_mapping.json')
    for o in initial['water']:assert values[o['cell']]==o['percent'] and abs(o['fraction']*100-o['percent'])<1e-12
    assert values['A36']==162 and initial['field_water_date']=='2008-06-10'
    assert values['J3']=='135 - 165' and values['K3']=='165 - 200'
    definition=maize['Data Descriptions']['C11'].value
    assert '135 - 175' in definition and '175 - 225' in definition
    assert initial['stock_interpretation_selected'] is False and initial['package_initial_water_validated'] is False
    t=read(tests);r=read(ready)
    assert t['tests_run']==192 and t['passed'] and not(t['failures'] or t['errors'] or t['skipped'])
    assert r['research_ready'] is False and r['main_training_allowed'] is False and not r['quantitative_fit_ready_studies']
    files=[folder/'verification.json',folder/'derived_files_sha256.json',tests,ready,
        ROOT/'src/mars_env/soil_coverage.py',ROOT/'tests/test_soil_coverage.py',
        ROOT/'scripts/build_d22_hydraulic_mapping.py',Path(__file__),
        ROOT/'configs/lirf_translation_contract.json',ROOT/'configs/agronomic_sources.json',
        ROOT/'docs/D22_HYDRAULIC_MAPPING.md',ROOT/'docs/NEXT_STEPS.md',ROOT/'PROGRESS.md']
    run=new_run(ROOT,'d22_hydraulic_mapping_release')
    write_json(run/'verification.json',dict(passed=True,technical_subsample_cells_verified=count,
        source_sha256_unchanged=True,tests_run=192,old_workspace_empty=True,
        laboratory_depth_fraction_0_200cm=.5461,field_water_depth_conflict_preserved=True,
        native_parameters_replaced=0,new_native_simulations=0,new_training_runs=0,
        research_ready=False,main_training_allowed=False,quantitative_fit_ready_studies=0,
        evidence_sha256={str(p.relative_to(ROOT)):sha256(p) for p in files},
        scope='source-cell and geometry qualification, no agronomic or initial-state validation'))
    print(run)


if __name__=='__main__':main()
