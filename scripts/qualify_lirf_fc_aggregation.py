"""Verify raw FC cells, paired-depth dispersion and unmodified unresolved rows."""
from decimal import Decimal
import json
from pathlib import Path
import sys
import openpyxl
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256


def main():
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    folder=ROOT/'outputs/runs/20261106T142730Z_lirf_fc_aggregation_b33c4f08'
    source=ROOT/'outputs/runs/20261106T083612Z_lirf_public_sources_d90f9eab'
    tests=ROOT/'outputs/runs/20261106T142835Z_unit_regressions_aecf4216/verification.json'
    ready=ROOT/'outputs/runs/20261106T142849Z_readiness_2147e1a5/readiness.json'
    for name,digest in read(folder/'derived_files_sha256.json').items():assert sha256(folder/name)==digest
    for name,digest in read(folder/'verification.json')['source_sha256'].items():assert sha256(source/name)==digest
    originals={}
    for year in range(2008,2012):
        w=openpyxl.load_workbook(source/f'LIRF_Maize_{year}.xlsx',read_only=True,data_only=True)
        for sheet in ('Seasonal','Tmnt2','Tmnt3'):
            originals[(year,sheet)]={c.coordinate:c.value for row in w[sheet] for c in row if c.value is not None}
    records=read(folder/'plot_fc_records.json');assert len(records)==96
    assert len({(r['year'],r['plot']) for r in records})==96
    for record in records:
        assert len(record['cells'])==7
        for c in record['cells']:assert originals[(record['year'],'Seasonal')][c['cell']]==c['fc_percent']
    aggregate=read(folder/'fc_mean_sd_reconstruction.json');assert len(aggregate)==168
    for r in aggregate:
        cells=originals[(r['year'],'Seasonal')]
        assert cells[r['reported_mean_cell']]==r['reported_mean'] and cells[r['reported_sd_cell']]==r['reported_sd']
        values=[Decimal(str(cells[c])) for c in r['plot_cells']]
        average=sum(values)/4
        variance=sum((v-average)**2 for v in values)/3
        assert abs(float(average)-r['reconstructed_mean'])<1e-12
        assert abs(float(variance.sqrt())-r['reconstructed_sample_sd'])<1e-12
    assert sum(r['exact_stored_numeric_match'] for r in aggregate)==104
    assert all(r['exact_stored_numeric_match'] for r in aggregate if r['year']>=2010)
    summaries=read(folder/'plot_fc_storage_dispersion.json');assert len(summaries)==48
    for r in summaries:
        s=r['summary'];group=[p for p in records if p['year']==r['year'] and p['treatment']==r['treatment']]
        assert {p['block'] for p in group}=={1,2,3,4}
        assert [p['plot'] for p in group]==r['plot_ids']
        n={105:4,135:5}[r['depth_cm']]
        stocks=[sum(c['fc_percent']*(1.5 if i==0 else 3) for i,c in enumerate(p['cells'][:n])) for p in group]
        assert all(abs(a-b)<1e-10 for a,b in zip(stocks,s['plot_fc_storage_mm']))
        # Pairwise identity verifies variance independently of the covariance implementation.
        variance=sum((a-b)**2 for i,a in enumerate(stocks) for b in stocks[i+1:])/12
        assert abs(variance-s['sample_sd_fc_storage_mm']**2)<1e-8
        assert abs(variance-s['covariance_stock_variance_mm2'])<1e-8
        assert abs(s['conditional_se_fc_mean_mm']**2-variance/4)<1e-8
        assert s['daily_swc_uncertainty_available'] is False and s['model_residual_uncertainty_available'] is False
    cases=read(folder/'swd_discrepancy_cases.json');assert len(cases)==2
    for case in cases:
        assert [r['date'] for r in case['neighbors']]==['2010-06-25','2010-07-01','2010-07-06']
        assert case['correction_applied'] is False and case['error_cell_identified'] is False
        assert abs(case['neighbors'][1]['residual_mm'])>1
        assert all(abs(case['neighbors'][i]['residual_mm'])<1e-10 for i in (0,2))
        for row in case['neighbors']:
            for cell in row['cells']:assert originals[(2010,f"Tmnt{case['treatment']}")][cell['cell']]==cell['value']
    contract=read(folder/'water_comparison_contract.json')
    assert contract['model_scoring_allowed'] is False and contract['fixed_error_tolerance_for_model_comparison_mm'] is None
    assert contract['static_fc_sd_is_daily_swc_sd'] is False and contract['unresolved_two_swd_rows_preserved']
    t=read(tests);r=read(ready)
    assert t['passed'] and t['tests_run']==199 and not(t['failures'] or t['errors'] or t['skipped'])
    assert r['research_ready'] is False and r['main_training_allowed'] is False and not r['quantitative_fit_ready_studies']
    files=[folder/'verification.json',folder/'derived_files_sha256.json',tests,ready,
        ROOT/'src/mars_env/fc_uncertainty.py',ROOT/'tests/test_fc_uncertainty.py',
        ROOT/'scripts/audit_lirf_fc_aggregation.py',Path(__file__),ROOT/'configs/lirf_translation_contract.json',
        ROOT/'configs/agronomic_sources.json',ROOT/'docs/LIRF_FC_AGGREGATION.md',ROOT/'docs/NEXT_STEPS.md',ROOT/'PROGRESS.md']
    run=new_run(ROOT,'lirf_fc_aggregation_release')
    write_json(run/'verification.json',dict(passed=True,source_fc_cells_verified=672,aggregation_pairs=168,
        static_fc_stock_summaries=48,unresolved_swd_cases=2,tests_run=199,
        source_sha256_unchanged=True,old_workspace_empty=True,source_values_corrected=0,
        new_native_simulations=0,new_training_runs=0,research_ready=False,main_training_allowed=False,
        quantitative_fit_ready_studies=0,evidence_sha256={str(p.relative_to(ROOT)):sha256(p) for p in files},
        scope='source cells, FC aggregation and paired-depth variance arithmetic; no daily SWC or field-model validation'))
    print(run)


if __name__=='__main__':main()
