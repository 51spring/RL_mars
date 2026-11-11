"""Audit archived CSV scope and source arithmetic without fitting a crop model."""
from collections import Counter,defaultdict
import csv
from datetime import date
from decimal import Decimal,InvalidOperation
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256

def number(v):
    try:
        n=Decimal(v)
        return n if n.is_finite() else None
    except (InvalidOperation,TypeError):return None

def main():
    source=ROOT/'outputs/runs/20261107T011325Z_kenya_public_dataset_f18ec4ef'
    acquisition=json.loads((source/'verification.json').read_text(encoding='utf-8'))
    assert acquisition['dataset_id']=='tdw54wgvbf' and acquisition['listed_files']==acquisition['acquired_files']==20
    tables={};inventory=[]
    for entry in acquisition['files']:
        p=source/entry['local_file'];assert sha256(p)==entry['sha256'] and entry['repository_sha256_checked']
        with p.open(encoding='utf-8-sig',newline='') as f:
            reader=csv.DictReader(f);rows=list(reader);fields=reader.fieldnames
        assert all(None not in r for r in rows)
        prefix=entry['filename'][:2];tables[prefix]=rows
        role=('plot_date_and_aggregated_rainfall_exposure' if prefix=='01' else
            'treatment_aggregated_rainfall_exposure' if prefix=='02' else
            'grain_failure_counts' if prefix=='18' else 'fitted_model_or_statistical_output')
        inventory.append(dict(filename=entry['filename'],local_file=entry['local_file'],sha256=sha256(p),
            rows=len(rows),columns=fields,role=role,raw_plot_grain_yield=False,daily_weather=False))
    assert sorted(tables)==[f'{i:02}' for i in range(1,21)]
    rainfall=tables['01'];groups=defaultdict(list);physical_candidates=defaultdict(list);date_checks=[]
    assert len({r['record_id'] for r in rainfall})==len(rainfall)==90
    for line,r in enumerate(rainfall,2):
        key=(r['site'],r['season'],r['treatment']);groups[key].append(r)
        physical_candidates[(r['site'],r['rep'],r['treatment'],r['variety'])].append(r['season'])
        parsed={k:date.fromisoformat(r[k]) if r[k] else None for k in ('planting_date','germ_50_date','flowering_50_date','harvest_date')}
        known=[d for d in parsed.values() if d is not None]
        date_checks.append(dict(csv_line=line,record_id=r['record_id'],dates={k:str(v) if v else None for k,v in parsed.items()},
            source_dates_ordered=known==sorted(known),date_missing=sum(v is None for v in parsed.values())))
    rain_checks=[]
    for line,r in enumerate(tables['02'],2):
        key=(r['site'],r['season'],r['treatment']);members=groups[key]
        checks=[]
        for field in ('rain_0_30d_mm','rain_flowering_pm7d_mm','rain_plant_to_harvest_mm','longest_dry_spell_0_30d_lt1mm'):
            vals=[number(m[field]) for m in members];assert all(v is not None for v in vals)
            calc=sum(vals)/len(vals);stated=number(r[field]);assert stated is not None
            checks.append(dict(field=field,recomputed=str(calc),reported=str(stated),signed_delta=str(calc-stated),
                rounding_review_flag=abs(calc-stated)>Decimal('0.000001')))
        rain_checks.append(dict(csv_line=line,site=key[0],season=key[1],treatment=key[2],n_source_rows=len(members),
            planting_min_matches=min(m['planting_date'] for m in members)==r['planting_date_min'],
            planting_max_matches=max(m['planting_date'] for m in members)==r['planting_date_max'],checks=checks))
    failures=[]
    for line,r in enumerate(tables['18'],2):
        n=int(r['Plots']);positive=int(r['Plots with grain']);failed=int(r['Grain-failure plots'])
        expected=Decimal(failed)/n;stated=number(r['Grain-failure proportion'])
        failures.append(dict(csv_line=line,site=r['Site'],season=r['Season'],sowing=r['Sowing treatment'],variety=r['Variety'],
            total=n,positive=positive,failed=failed,count_identity=n==positive+failed,
            fraction_signed_delta=str(expected-stated),fraction_matches_rounded=abs(expected-stated)<=Decimal('0.000000001')))
    contrasts=[]
    for prefix in ('09','10','11','14','17'):
        for line,r in enumerate(tables[prefix],2):
            estimate,se,t=number(r['Estimate']),number(r['SE']),number(r['t ratio'])
            computed=estimate/se if estimate is not None and se is not None and se>0 else None
            delta=computed-t if computed is not None and t is not None else None
            contrasts.append(dict(file_prefix=prefix,csv_line=line,estimate=r['Estimate'],SE=r['SE'],reported_t=r['t ratio'],
                computed_t=str(computed) if computed is not None else None,signed_delta=str(delta) if delta is not None else None,
                relative_review_flag=abs(delta)>Decimal('0.000001')*max(Decimal(1),abs(t)) if delta is not None else None))
    cov_groups=defaultdict(list)
    for r in tables['04']:cov_groups[r['Model']].append(r)
    covariance=[]
    for r in tables['03']:
        candidates=cov_groups[r['Model']]
        aic=min(number(c['AIC']) for c in candidates);bic=min(number(c['BIC']) for c in candidates)
        aic_names=[c['Covariance structure'] for c in candidates if number(c['AIC'])==aic]
        bic_names=[c['Covariance structure'] for c in candidates if number(c['BIC'])==bic]
        covariance.append(dict(model=r['Model'],candidate_count=len(candidates),
            stated_AIC=r['AIC-selected covariance'],stated_BIC=r['BIC-selected covariance'],
            AIC_argmin_matches=r['AIC-selected covariance'] in aic_names,BIC_argmin_matches=r['BIC-selected covariance'] in bic_names,
            selectors_disagree=r['AIC-selected covariance']!=r['BIC-selected covariance']))
    run=new_run(ROOT,'kenya_input_audit');print(run,flush=True)
    outputs={'csv_inventory':inventory,'plot_date_checks':date_checks,'rainfall_summary_reconciliation':rain_checks,
        'grain_failure_reconciliation':failures,'contrast_t_reconciliation':contrasts,'covariance_selection_reconciliation':covariance,
        'repeated_unit_candidates':[dict(site=k[0],rep=k[1],sowing=k[2],variety=k[3],seasons=v,
            source_physical_plot_id_qualified=False) for k,v in sorted(physical_candidates.items())]}
    for name,data in outputs.items():write_json(run/f'{name}.json',data)
    rain_contexts=Counter((r['site'],r['season']) for r in rainfall)
    failure_contexts=Counter((r['Site'],r['Season']) for r in tables['18'])
    dossier=dict(raw_plot_grain_yield='not in the20acquired CSV schemas; corrected-grain EMM is a fitted estimate, not a raw observation',
        rainfall='90plot exposure rows over4site-season contexts, not full10contexts and not daily weather',
        dependence='same physical plots followed5seasons in public metadata; season-bearing record_id is not a new independent experiment',
        failure='75site-season-treatment-variety summaries totaling225plot-seasons; counts do not identify which raw plot failed',
        grain_basis='corrected grain yield in Mg/ha; correction moisture and drying/sampling protocol not supplied',
        varieties='variety names supplied; genetic coefficients and parameter-exposure lineage unqualified',
        soil_weather='no full soil/initial-state profile or daily TMAX/TMIN/SRAD/rainfall payload in acquired20CSV',
        management='partial planting/germination/flowering/harvest dates; fertilizer/pest practices/density/depth and field hierarchy unqualified',
        documentation='landing description mentions README; no README in returned root and one data folder file inventory; do not claim absent everywhere',
        model_results='primary/season-specific/productive-season/cross-site outputs reuse observations; do not count as independent data or select the model giving desired outcome',
        native_input_assignments=0,source_values_overwritten=False)
    write_json(run/'source_input_gaps.json',dossier)
    report=dict(passed=True,scope='public CSV acquisition/scope and source arithmetic audit; mismatch flags retained, no model fitting',
        acquired_files=20,total_data_rows=sum(i['rows'] for i in inventory),plot_rainfall_records=90,
        rainfall_contexts=[dict(site=s,season=y,rows=n) for (s,y),n in sorted(rain_contexts.items())],
        rainfall_summary_groups=len(rain_checks),rainfall_numeric_checks=sum(len(r['checks']) for r in rain_checks),
        rainfall_difference_flags=sum(c['rounding_review_flag'] for r in rain_checks for c in r['checks']),
        rainfall_date_range_flags=sum(not(r['planting_min_matches'] and r['planting_max_matches']) for r in rain_checks),
        source_date_order_flags=sum(not r['source_dates_ordered'] for r in date_checks),
        grain_failure_groups=len(failures),summarized_plot_seasons=sum(r['total'] for r in failures),
        grain_failure_plot_seasons=sum(r['failed'] for r in failures),
        failure_identity_flags=sum(not r['count_identity'] for r in failures),failure_fraction_flags=sum(not r['fraction_matches_rounded'] for r in failures),
        contrast_t_checks=len(contrasts),contrast_t_review_flags=sum(r['relative_review_flag'] is True for r in contrasts),
        contrast_t_uncomputable=sum(r['relative_review_flag'] is None for r in contrasts),
        covariance_models=len(covariance),covariance_argmin_flags=sum(not(r['AIC_argmin_matches'] and r['BIC_argmin_matches']) for r in covariance),
        AIC_BIC_disagreements=sum(r['selectors_disagree'] for r in covariance),
        raw_plot_grain_yield_acquired=False,daily_weather_acquired=False,README_acquired=False,
        active_studies_added=0,new_native_input_assignments=0,new_native_simulations=0,new_training_runs=0,
        quantitative_fit_ready=False,research_ready=False,main_training_allowed=False,
        acquisition_report_sha256=sha256(source/'verification.json'),
        next_task='Crosswalk primary/season-specific/productive-season estimands and source correction/phenology; seek linked protocol and missing raw grain/full inputs')
    write_json(run/'verification.json',report)
    write_json(run/'derived_files_sha256.json',{p.name:sha256(p) for p in run.iterdir() if p.is_file()})
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
