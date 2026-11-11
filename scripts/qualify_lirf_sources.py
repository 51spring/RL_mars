"""Read-only staging of USDA LIRF source values, formulas, and unresolved inputs.

Run with bundled Python (openpyxl, pypdf). No workbook recalculation or export.
No automatic DSSAT input conversion and no model fitting.
"""
import argparse
import calendar
from datetime import datetime,timedelta
import json
from pathlib import Path
import statistics
import sys
import shutil
import openpyxl
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256


def safe(v):
    return v.isoformat() if isinstance(v,datetime) else v


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('source',type=Path)
    args=parser.parse_args();source=args.source.resolve()
    acquired=json.loads((source/'verification.json').read_text())
    assert acquired['passed']
    assert all(sha256(source/f['file'])==f['sha256'] for f in acquired['files'])
    global ACTIVE_RUN
    run=new_run(ROOT,'lirf_input_qualification');ACTIVE_RUN=run;print(run,flush=True)
    plots=[];means=[];weather=[];management=[];logs=[];definitions=[];inventory=[];warnings=[]
    for year in range(2008,2012):
        filename=f'LIRF_Maize_{year}.xlsx'
        w=openpyxl.load_workbook(source/filename,data_only=True)
        formula=openpyxl.load_workbook(source/filename,data_only=False)
        for sheet in w:
            inventory.append(dict(file=filename,sheet=sheet.title,rows=sheet.max_row,columns=sheet.max_column))
        for row in w['Data Descriptions']:
            definitions.append(dict(file=filename,sheet='Data Descriptions',row=row[0].row,
                cells={c.coordinate:safe(c.value) for c in row if c.value is not None}))
        s=w['Seasonal'];f=formula['Seasonal']
        assert s['I5'].comment and 'dry weight' in s['I5'].comment.text.lower()
        assert s['I6'].value=='kg/ha'
        for row in range(26,50):
            t,b,p=s.cell(row,1).value,s.cell(row,2).value,s.cell(row,3).value
            assert t in range(1,7) and b in range(1,5) and isinstance(p,str)
            wet,dry=s.cell(row,8).value,s.cell(row,9).value
            assert isinstance(dry,(int,float)) and abs(dry-wet*.845)<1e-7
            plots.append(dict(study_id='usda_lirf2008_2011',year=year,treatment=t,block=b,plot=p,
                reported_grain_15_5pct_kg_ha=wet,dry_grain_kg_ha=dry,
                plant_population_ha=s.cell(row,4).value,aboveground_dry_biomass_kg_ha=s.cell(row,6).value,
                source_file=filename,source_sheet='Seasonal',source_row=row,
                dry_yield_formula=f.cell(row,9).value))
        assert len({(p['treatment'],p['block']) for p in plots if p['year']==year})==24
        for t in range(1,7):
            values=[p['dry_grain_kg_ha'] for p in plots if p['year']==year and p['treatment']==t]
            mean,sd=statistics.mean(values),statistics.stdev(values)
            reported=s.cell(6+t,9).value;reported_sd=s.cell(14+t,9).value
            delta=reported-mean
            means.append(dict(year=year,treatment=t,replicate_blocks=4,
                reported_dry_mean_kg_ha=reported,reported_dry_sd_kg_ha=reported_sd,
                plot_derived_dry_mean_kg_ha=mean,plot_derived_dry_sd_kg_ha=sd,
                reported_minus_plot_mean_kg_ha=delta,
                discrepancy_exceeds_one_kg_ha=abs(delta)>1,
                diagnostic_threshold_only_kg_ha=1,
                source_file=filename,mean_cell=f'I{6+t}',sd_cell=f'I{14+t}',
                mean_formula=f.cell(6+t,9).value,upstream_wet_mean_formula=f.cell(6+t,8).value,
                model_comparison_passed=None,quantitative_fit_ready=False))
        for name in [f'Tmnt{t}' for t in range(1,7)]:
            sheet=w[name];seen=[]
            assert sheet['B3'].value=='Precip' and sheet['C3'].value=='Irrig'
            assert sheet['R3'].value=='N Applied'
            for row in range(5,sheet.max_row+1):
                doy=sheet.cell(row,1).value
                # Stop at the end of the contiguous daily table. Numeric DOYs
                # later in the sheet are harvest/measurement footer tables.
                if not isinstance(doy,(int,float)) or not 1<=doy<=366 or int(doy)!=doy:
                    break
                doy=int(doy);seen.append(doy)
                management.append(dict(year=year,treatment=int(name[-1]),doy=doy,
                    date=(datetime(year,1,1)+timedelta(days=doy-1)).date().isoformat(),
                    precipitation_column_mm=sheet.cell(row,2).value,
                    drip_irrigation_column_mm=sheet.cell(row,3).value,
                    n_applied_or_initial_soil_n_column_kg_ha=sheet.cell(row,18).value,
                    recorded_growth_stage=sheet.cell(row,13).value,
                    soil_water_percent_by_source_columns={sheet.cell(3,col).value:sheet.cell(row,col).value for col in range(5,12)},
                    source_file=filename,source_sheet=name,source_row=row))
            assert len(seen)==len(set(seen)) and seen==list(range(min(seen),max(seen)+1))
        for row in w['CropLog']:
            if isinstance(row[0].value,datetime):
                logs.append(dict(year=year,date=row[0].value.date().isoformat(),
                    category=row[1].value,operation=row[2].value,details=row[3].value,
                    source_file=filename,source_sheet='CropLog',source_row=row[0].row))
        wf=f'LIRF_Weather_{year}.xlsx';ws=openpyxl.load_workbook(source/wf,data_only=True)['Daily']
        dates=[]
        for row in ws:
            if not isinstance(row[0].value,datetime):continue
            day=row[0].value
            assert day.year==year and day.timetuple().tm_yday==row[1].value
            dates.append(day)
            record=dict(year=year,date=day.date().isoformat(),doy=row[1].value,
                tmax_c=row[3].value,tmin_c=row[4].value,srad_mj_m2_day=row[8].value,
                weather_station_rain_mm=row[10].value,field_precipitation_column_mm=row[15].value,
                source_file=wf,source_sheet='Daily',source_row=row[0].row)
            for key in ('tmax_c','tmin_c','srad_mj_m2_day'):
                if not isinstance(record[key],(int,float)):
                    warnings.append(dict(issue='missing_weather_core',year=year,date=record['date'],field=key))
            weather.append(record)
        assert len(dates)==365+calendar.isleap(year) and len(set(dates))==len(dates)
    soil=openpyxl.load_workbook(source/'LIRF_Soils.xlsx',data_only=True)
    for s in soil:
        inventory.append(dict(file='LIRF_Soils.xlsx',sheet=s.title,rows=s.max_row,columns=s.max_column))
    for row in soil['Data Description']:
        definitions.append(dict(file='LIRF_Soils.xlsx',sheet='Data Description',row=row[0].row,
            cells={c.coordinate:safe(c.value) for c in row if c.value is not None}))
    assert len(plots)==96 and len(means)==24 and len(weather)==1461
    text='\n\n'.join(f'PAGE {i+1}\n'+p.extract_text() for i,p in enumerate(PdfReader(source/'LIRF_Methodology_r1.pdf').pages))
    (run/'methodology.txt').write_text(text,encoding='utf-8')
    risk_terms=('mite','insect','frost','hail','germination')
    risk_logs=[r for r in logs if any(term in str(r['details']).lower() for term in risk_terms)]
    discrepancies=[m for m in means if m['discrepancy_exceeds_one_kg_ha']]
    assert len(discrepancies)==1 and (discrepancies[0]['year'],discrepancies[0]['treatment'])==(2009,3)
    for name,value in [('plot_yields',plots),('treatment_summaries',means),('daily_weather',weather),
                       ('daily_management_source_columns',management),('crop_logs',logs),
                       ('source_definitions',definitions),('workbook_inventory',inventory),('risk_logs',risk_logs)]:
        write_json(run/f'{name}.json',value)
    pending=['DSSAT cultivar coefficients and model-package provenance',
        'soil sampling site/plot/year join and explicit layer hydraulics/initial water and N',
        '2009 treatment3 summary vs replicate mean discrepancy',
        '2008 21mm sprinkler in precipitation column, groundwater N and initial soil N separation',
        'source soil-depth labels vs definitions and per-year harvest annotation reconciliation',
        'weather field precipitation missing values and station/field rain join',
        'biotic and frost covariates from crop logs; no pest-free assumption',
        'predefined independent model comparison and uncertainty protocol']
    report=dict(passed=True,scope='read-only source staging and discrepancy detection, no DSSAT or calibration',
        source_run=source.relative_to(ROOT).as_posix(),source_report_sha256=sha256(source/'verification.json'),
        original_source_sha256={f['file']:f['sha256'] for f in acquired['files']},
        plot_yield_records=len(plots),treatment_year_summaries=len(means),daily_weather_records=len(weather),
        daily_treatment_records=len(management),crop_log_records=len(logs),risk_log_records=len(risk_logs),
        weather_core_warnings=warnings,summary_discrepancies=discrepancies,
        original_workbooks_modified=False,cached_formulas_recalculated=False,
        planned_role='independent_validation_base_crop_water_response',split_unit='entire LIRF study 2008-2011',
        missing_inputs=pending,damage_response_validated=False,quantitative_fit_ready=False,
        independent_agronomic_validation=False,research_ready=False,main_training_allowed=False)
    write_json(run/'verification.json',report)
    write_json(run/'derived_files_sha256.json',{p.name:sha256(p) for p in run.iterdir() if p.is_file()})
    print(json.dumps({k:report[k] for k in ('plot_yield_records','treatment_year_summaries','daily_weather_records','daily_treatment_records','risk_log_records')},indent=2))


if __name__=='__main__':
    try:main()
    except Exception as exc:
        if 'ACTIVE_RUN' in globals():
            write_json(ACTIVE_RUN/'failure.json',dict(passed=False,exception=repr(exc),
                scope='source qualification',research_ready=False))
        raise
