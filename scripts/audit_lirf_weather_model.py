"""Qualify original hourly/daily weather and dated public modelling inputs."""
from collections import defaultdict
from datetime import datetime,timedelta
import gzip
import io
import json
from pathlib import Path
import sys
import zipfile
import openpyxl
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.lirf_weather import aggregate_hourly_solar,api_daily_value


def main():
    source=ROOT/'outputs/runs/20261106T083612Z_lirf_public_sources_d90f9eab'
    model=ROOT/'outputs/runs/20261106T084700Z_lirf_model_package_f84234e1'
    api=ROOT/'outputs/runs/20261106T084911Z_lirf_station_windows_0f693d5f'
    global ACTIVE_RUN
    run=new_run(ROOT,'lirf_weather_model_audit');ACTIVE_RUN=run;print(run,flush=True)
    evidence={}
    for label,folder in (('source',source),('model',model),('api',api)):
        d=json.loads((folder/'verification.json').read_text());assert d['passed']
        evidence[label]=dict(path=folder.relative_to(ROOT).as_posix(),report_sha256=sha256(folder/'verification.json'))
    src=json.loads((source/'verification.json').read_text())
    assert all(sha256(source/f['file'])==f['sha256'] for f in src['files'])
    api_report=json.loads((api/'verification.json').read_text())
    assert all(sha256(api/r['file'])==r['sha256'] for r in api_report['requests'])
    model_report=json.loads((model/'verification.json').read_text())
    assert sha256(model/'agmip_download.zip')==model_report['package_sha256']
    assert all(sha256(model/'package'/m['name'])==m['sha256'] for m in model_report['members'])
    solar=[];daily={};definitions=[];hour_sources={};hourly_failures=[]
    # Quantization bound: daily 0.01MJ/2 plus24 hourly 0.01kJ/min/2 *60/1000.
    # Diagnostic comparison only. Source corrections can exceed this bound.
    bound=.005+24*.005*.06+1e-9
    for year in range(2008,2012):
        filename=f'LIRF_Weather_{year}.xlsx'
        workbook=openpyxl.load_workbook(source/filename,data_only=True)
        sheet=workbook['Hourly'];grouped=defaultdict(list);flags=defaultdict(list)
        assert sheet['F3'].value=='kJ/m^2/min' and sheet['A4'].value=='(end of period)'
        for row in workbook['Data Description']:
            definitions.append(dict(file=filename,row=row[0].row,cells={c.coordinate:c.value for c in row if c.value is not None}))
        for row in sheet:
            if isinstance(row[0].value,datetime):
                stamp=row[0].value;day=(stamp-timedelta(seconds=1)).date()
                grouped[day].append((stamp,row[5].value))
                flags[day].append(dict(cell=row[5].coordinate,time=stamp.isoformat(),value=row[5].value,
                    replacement_flag=row[20].value if len(row)>20 else None))
        for row in workbook['Daily']:
            if not isinstance(row[0].value,datetime):continue
            day=row[0].value.date();value=row[8].value
            try:derived=aggregate_hourly_solar(day,grouped[day])
            except ValueError as exc:
                derived=None
                hourly_failures.append(dict(date=day.isoformat(),error=str(exc),
                    hour_end_times=[stamp.isoformat() for stamp,_ in grouped[day]]))
            daily[day.isoformat()]=dict(tMax=row[3].value,tMin=row[4].value,solarRad=value,
                station_flag=row[18].value if len(row)>18 else None,source_file=filename,source_row=row[0].row)
            available=isinstance(value,(float,int))
            delta=derived-value if available and derived is not None else None
            solar.append(dict(date=day.isoformat(),daily_source_cell=row[8].coordinate,
                daily_srad_mj_m2_day=value,hourly_integrated_mj_m2_day=derived,hour_end_count=len(grouped[day]),
                hourly_minus_daily_mj_m2_day=delta,diagnostic_quantization_bound=bound,
                exceeds_quantization_bound=delta is not None and abs(delta)>bound,
                negative_hourly_values=sum(v<0 for _,v in grouped[day]),
                daily_station_flag=daily[day.isoformat()]['station_flag']))
            if not available:hour_sources[day.isoformat()]=flags[day]
    assert len(solar)==1461
    gaps=[];comparisons=[]
    for target,preferred in (('2009-10-02','gly04'),('2010-07-16','gly04'),('2011-08-11','ksy01')):
        target_date=datetime.fromisoformat(target).date()
        record=daily[target]
        if record['station_flag'] is not None:assert record['station_flag'].lower()==preferred
        for station in ('gly04','ksy01'):
            filename=f'{station}_{target}.json';payload=json.loads((api/filename).read_text())
            for ds in payload['time']:
                for field in ('tMax','tMin','solarRad'):
                    value=api_daily_value(payload,datetime.fromisoformat(ds).date(),field,station=station)
                    original=daily[ds][field]
                    comparable=isinstance(original,(int,float)) and value is not None
                    comparisons.append(dict(date=ds,field=field,station=station,source_api=filename,
                        workbook_value=original,api_value=value,api_minus_workbook=value-original if comparable else None))
            for field in ('tMin','solarRad'):
                if isinstance(record[field],(int,float)):continue
                value=api_daily_value(payload,target_date,field,station=station)
                gap=dict(date=target,field=field,source_preferred_station=preferred,candidate_station=station,
                    same_station=station==preferred,api_value=value,api_source=filename,applied=False,
                    decision='current same-station observation missing' if station==preferred and value is None
                        else 'alternate-station observation only; not automatic substitution')
                if field=='solarRad':
                    gap['original_hourly_integrated_mj_m2_day']=next(s['hourly_integrated_mj_m2_day'] for s in solar if s['date']==target)
                    gap['hourly_instrument_base_station']='gly04'
                gaps.append(gap)
    same=[g for g in gaps if g['same_station']]
    assert len(same)==4 and all(g['api_value'] is None for g in same)
    package=model/'package/Greeley CO LIRF Means'
    ace=json.loads(gzip.decompress((package/'ace.aceb').read_bytes()))
    dome=json.loads(gzip.decompress((package/'domes.dome').read_bytes()))
    write_json(run/'decoded_ace.json',ace);write_json(run/'decoded_dome.json',dome)
    with zipfile.ZipFile(package/'cultivar.zip') as archive:
        name=next(n for n in archive.namelist() if n.endswith('.CUL'))
        cultivar=archive.read(name);(run/'MZCER045.CUL').write_bytes(cultivar)
    rows=[r for r in cultivar.decode('latin-1').splitlines() if r.startswith('IB1068 ')]
    assert len(rows)==1 and 'DEKALB 521' in rows[0]
    experiment=ace['experiments'][0]
    planting=next(e for e in experiment['management']['events'] if e['event']=='planting')
    assert planting['cul_id']=='IB1068' and planting['cul_name']=='DEKALB 521'
    stats=dict(experiments=len(ace['experiments']),soil_profiles=len(ace['soils']),
        weather_stations=len(ace['weathers']),weather_days=len(ace['weathers'][0]['dailyWeather']),
        weather_first=ace['weathers'][0]['dailyWeather'][0]['w_date'],
        weather_last=ace['weathers'][0]['dailyWeather'][-1]['w_date'],
        treatment=experiment['trt_name'],time_series_rows=len(experiment['observed']['timeSeries']),
        cultivar_header='MZCER045',cultivar_id='IB1068',cultivar_name='DEKALB 521',
        field_cultivar_name='DeKalb 52-59',cultivar_equivalence_verified=False,
        cultivar_row=rows[0],unmapped_trailing_coefficients=True,parameter_calibration_studies_known=False,
        full_24_treatment_year_coverage=False,default_cultivar_replacement_allowed=False,
        dssat048_compatibility_verified=False)
    assert stats['experiments']==1 and stats['weather_days']==366 and stats['weather_first']=='20080101'
    for name,value in [('solar_crosscheck',solar),('gap_candidates',gaps),('api_workbook_comparisons',comparisons),
        ('hourly_gap_source_cells',hour_sources),('source_definitions',definitions),('model_package_scope',stats),
        ('hourly_chronology_failures',hourly_failures)]:
        write_json(run/f'{name}.json',value)
    report=dict(passed=True,scope='weather provenance and public package qualification; no gap applied or native simulation',
        evidence=evidence,daily_dates_audited=1461,
        valid_hourly_aggregations=sum(s['hourly_integrated_mj_m2_day'] is not None for s in solar),
        daily_hourly_solar_comparisons=sum(s['hourly_minus_daily_mj_m2_day'] is not None for s in solar),
        hourly_chronology_failures=hourly_failures,
        solar_exceeds_quantization_bound=sum(s['exceeds_quantization_bound'] for s in solar),
        max_solar_difference_mj_m2_day=max(abs(s['hourly_minus_daily_mj_m2_day']) for s in solar if s['hourly_minus_daily_mj_m2_day'] is not None),
        negative_hourly_values_preserved=sum(s['negative_hourly_values'] for s in solar),
        hourly_reconstruction_candidates=3,same_station_api_missing_fields=4,remaining_missing_fields=4,
        original_workbooks_modified=False,missing_daily_temperature_replaced_with_hourly_mean_minimum=False,
        gap_candidates_automatically_applied=False,model_package_scope=stats,
        independent_study_split_unchanged=True,quantitative_fit_ready=False,research_ready=False,main_training_allowed=False)
    write_json(run/'verification.json',report)
    write_json(run/'derived_files_sha256.json',{p.name:sha256(p) for p in run.iterdir() if p.is_file()})
    print(json.dumps({k:report[k] for k in ('daily_dates_audited','daily_hourly_solar_comparisons','solar_exceeds_quantization_bound','max_solar_difference_mj_m2_day','remaining_missing_fields')},indent=2))


if __name__=='__main__':
    try:main()
    except Exception as exc:
        if 'ACTIVE_RUN' in globals():write_json(ACTIVE_RUN/'failure.json',dict(passed=False,exception=repr(exc),research_ready=False))
        raise
