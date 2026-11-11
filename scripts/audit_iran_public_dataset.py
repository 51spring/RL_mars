"""Read-only workbook structure, source arithmetic and calendar audit."""
from collections import Counter,defaultdict
import calendar
from datetime import date,timedelta
import json
from pathlib import Path
import statistics
import sys
import openpyxl
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256

def main():
    source=ROOT/'outputs/runs/20261106T235323Z_iran_public_dataset_d683006d'
    acquired=json.loads((source/'verification.json').read_text(encoding='utf-8'))
    assert acquired['listed_files']==acquired['acquired_files']==1
    entry=acquired['files'][0];path=source/entry['local_file']
    assert sha256(path)==entry['sha256'] and entry['repository_sha256_checked']
    w=openpyxl.load_workbook(path,read_only=True,data_only=True)
    f=openpyxl.load_workbook(path,read_only=True,data_only=False)
    inventory=[]
    for s in f:
        inventory.append(dict(sheet=s.title,rows=s.max_row,columns=s.max_column,state=s.sheet_state,
            formulas=sum(c.data_type=='f' for row in s for c in row),
            error_cells=[c.coordinate for row in w[s.title] for c in row if c.data_type=='e']))
    harvest=[];groups=defaultdict(list);identities=set();year=None
    for row in w['harvest']:
        if row[4].value in (2014,2015):year=int(row[4].value)
        if row[5].value not in ('M1','M2') or not isinstance(row[7].value,int):continue
        m,n,r=[row[i].value for i in (5,6,7)]
        assert n in ('No','N1','N2') and r in (1,2,3)
        key=(year,m,n,r);assert key not in identities;identities.add(key)
        rec=dict(year=year,irrigation_method=m,nitrogen_label_raw=n,replicate=r,
            grain_dry_kg_ha=row[10].value,aboveground_dry_kg_ha=row[11].value,
            shoot_leaf_dry_kg_ha=row[8].value,ear_dry_kg_ha=row[9].value,
            nitrogen_uptake_kg_ha=row[12].value,applied_irrigation_m3_ha=row[14].value,
            source_row=row[10].row,grain_cell=row[10].coordinate,
            N0_alias_candidate=(n=='No'),N0_alias_qualified=False,block_hierarchy_qualified=False)
        assert all(isinstance(rec[k],(int,float)) for k in ('grain_dry_kg_ha','aboveground_dry_kg_ha','applied_irrigation_m3_ha'))
        rec['biomass_component_delta_kg_ha']=rec['aboveground_dry_kg_ha']-rec['shoot_leaf_dry_kg_ha']-rec['ear_dry_kg_ha']
        rec['cached_IWP_checks']=[]
        for column,numerator in [(15,'grain_dry_kg_ha'),(16,'aboveground_dry_kg_ha')]:
            cell=row[column];formula=f['harvest'][cell.coordinate].value
            assert formula==f'={"K" if column==15 else "L"}{row[10].row}/O{row[10].row}'
            expected=rec[numerator]/rec['applied_irrigation_m3_ha']
            rec['cached_IWP_checks'].append(dict(cell=cell.coordinate,formula=formula,cached=cell.value,
                independently_computed=expected,delta=cell.value-expected if isinstance(cell.value,(int,float)) else None))
        harvest.append(rec);groups[(year,m,n)].append(rec)
    assert len(harvest)==36 and len(groups)==12 and all(len(rows)==3 for rows in groups.values())
    summaries=[dict(year=y,irrigation_method=m,nitrogen_label_raw=n,n=3,
        grain_mean_kg_ha=statistics.fmean(r['grain_dry_kg_ha'] for r in rows),
        grain_sample_sd_kg_ha=statistics.stdev(r['grain_dry_kg_ha'] for r in rows),
        grain_cells=[r['grain_cell'] for r in rows],source_summary_only=True,
        pooled_across_years=False,SE_or_contrast_covariance_qualified=False)
        for (y,m,n),rows in sorted(groups.items())]
    calendars=[];events=[];irrigation_totals=[];soil=[]
    for year in (2014,2015):
        sheet=f'Gross irrigation depth ({year})';rows=list(w[sheet]);month=None;records=[]
        for row in rows[3:]:
            if row[5].value:month=list(calendar.month_name).index(row[5].value)
            day=row[6].value
            if not isinstance(day,(int,float)):continue # exclude SUM footer, never double-count it
            candidate=date(year,month,int(day));dap=row[7].value
            rec=dict(source_row=row[6].row,source_day_cell=row[6].coordinate,
                calendar_date_candidate=candidate.isoformat(),source_weekday=row[4].value,
                computed_weekday=candidate.strftime('%A'),weekday_matches=row[4].value==candidate.strftime('%A'),
                DAP=dap,DAP_zero_date_candidate=(candidate-timedelta(days=int(dap))).isoformat() if isinstance(dap,(int,float)) else None,
                native_assignment_allowed=False)
            records.append(rec)
            for column,method in [(8,'M1'),(9,'M2')]:
                amount=row[column].value
                if isinstance(amount,(int,float)):
                    events.append(dict(year=year,method=method,amount_mm=amount,source_cell=row[column].coordinate,
                        date_candidate=candidate.isoformat(),DAP=dap,native_schedule_qualified=False))
        dates=[date.fromisoformat(r['calendar_date_candidate']) for r in records]
        span={min(dates)+timedelta(days=i) for i in range((max(dates)-min(dates)).days+1)}
        calendars.append(dict(year=year,records=records,dated_rows=len(records),
            source_months_forward_filled_for_diagnostics=True,duplicate_dates=len(dates)-len(set(dates)),
            missing_calendar_days=[d.isoformat() for d in sorted(span-set(dates))],
            weekday_mismatches=sum(not r['weekday_matches'] for r in records),
            DAP_zero_candidate_counts=dict(Counter(r['DAP_zero_date_candidate'] for r in records if r['DAP_zero_date_candidate'])),
            blank_irrigation_not_filled=True,planting_date_not_assigned=True))
        for method,column in [('M1',8),('M2',9)]:
            amounts=[e['amount_mm'] for e in events if e['year']==year and e['method']==method]
            rawsum=sum(amounts)
            footer=[r[column] for r in f[sheet] if r[column].data_type=='f']
            assert len(footer)==1
            cached=w[sheet][footer[0].coordinate].value
            applied={r['applied_irrigation_m3_ha'] for r in harvest if r['year']==year and r['irrigation_method']==method}
            assert len(applied)==1
            implied=next(iter(applied))/10 # 1 mm/ha = 10 m3/ha
            irrigation_totals.append(dict(year=year,method=method,event_rows=len(amounts),
                event_sum_mm=rawsum,footer_cell=footer[0].coordinate,footer_formula=footer[0].value,footer_cached_mm=cached,
                harvest_volume_implied_mm=implied,footer_delta_mm=rawsum-cached,harvest_delta_mm=rawsum-implied,
                total_amount_agreement=abs(rawsum-cached)<1e-8 and abs(rawsum-implied)<1e-8,
                event_dates_qualified=False))
        s=w[f'Soil moisture ({year})']
        for depth,start in [('0-20',3),('20-40',8),('40-60',13)]:
            for column in range(7,s.max_column+1):
                dap=s.cell(2,column).value
                if not isinstance(dap,(int,float)):continue
                measured=s.cell(start+3,column)
                soil.append(dict(year=year,depth_cm=depth,DAP=dap,
                    FC_vol_percent=s.cell(start,column).value,PWP_vol_percent=s.cell(start+1,column).value,
                    MAD_threshold_vol_percent=s.cell(start+2,column).value,soil_vol_percent=measured.value,
                    source_cell=measured.coordinate,replicate_and_treatment_not_identified=True,
                    initial_state_not_qualified=True))
    assert all(t['total_amount_agreement'] for t in irrigation_totals)
    assert all(abs(r['biomass_component_delta_kg_ha'])<1e-8 for r in harvest)
    assert all(c['delta'] is not None and abs(c['delta'])<1e-10 for r in harvest for c in r['cached_IWP_checks'])
    run=new_run(ROOT,'iran_input_audit');print(run,flush=True)
    for name,data in [('workbook_inventory',inventory),('harvest_source_records',harvest),('grain_group_statistics',summaries),
        ('irrigation_calendar_audit',calendars),('irrigation_event_candidates',events),('irrigation_amount_reconciliation',irrigation_totals),
        ('soil_water_source_records',soil)]:write_json(run/f'{name}.json',data)
    dossier=dict(endpoint='source labels GY dry weight (kg/ha); laboratory dry-weight protocol not supplied',
        design='public metadata RCBD x3, two years; R keys not yet mapped to fixed field/block layout',
        N_rates='legend N0/N1/N2=0/150/300 kg N/ha; raw harvest No spelling retained, alias not qualified',
        weather='no daily weather sheet or file supplied in acquired package',
        soil='FC/PWP at0-20/20-40/40-60cm; full texture/bulk density/SAT/Ksat/OC/initial mineral N unavailable',
        management='gross irrigation totals reconciled, date/DAP/weekday contradictions remain; full fertilizer timing/material and planting/cultivar/density unqualified',
        cultivar_lineage='not supplied; no cultivar coefficient or independent calibration exposure qualification',
        damage='no assigned live-leaf damage/recovery treatment in acquired package',
        growth='During the growing season explicitly contains means of3replicates, not new raw replicates',
        field_location='institution Isfahan University of Technology is not proof of field coordinates/elevation',
        native_input_assignments=0)
    write_json(run/'source_input_gaps.json',dossier)
    report=dict(passed=True,scope='read-only source extraction/arithmetic completed; calendar and full-input qualification failed/pending',
        source_sha256=sha256(path),sheets=len(inventory),harvest_records=len(harvest),year_treatment_groups=len(groups),replicates_per_group=3,
        biomass_component_identities=36,cached_IWP_formula_checks=72,irrigation_amount_reconciliations=4,
        irrigation_calendar=[{k:v for k,v in c.items() if k!='records'} for c in calendars],
        soil_water_table_cells=len(soil),numeric_soil_water_observations=sum(isinstance(r['soil_vol_percent'],(int,float)) for r in soil),
        original_workbook_modified=False,formulas_recalculated=False,source_values_overwritten=False,
        source_dates_corrected=False,active_studies_added=0,new_native_input_assignments=0,
        quantitative_fit_ready=False,research_ready=False,main_training_allowed=False,new_native_simulations=0,new_training_runs=0,
        next_task='Find primary paper/protocol and clarify dates/DAP, No/N0 mapping, replicate hierarchy, fertilizer and cultivar/full weather-soil inputs')
    assert sha256(path)==report['source_sha256']
    write_json(run/'verification.json',report)
    write_json(run/'derived_files_sha256.json',{p.name:sha256(p) for p in run.iterdir() if p.is_file()})
    w.close();f.close();print(json.dumps(report,indent=2))

if __name__=='__main__':main()
