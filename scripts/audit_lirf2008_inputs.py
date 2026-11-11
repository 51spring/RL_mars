"""Crosswalk package2008 inputs against preserved field records; no corrections."""
from collections import defaultdict
import csv
from datetime import datetime
import json
from pathlib import Path
import sys
import openpyxl
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.lirf_input_audit import initial_inventory,soil_schema_flags


def read(path):return json.loads(path.read_text(encoding='utf-8'))


def main():
    field=ROOT/'outputs/runs/20261106T083612Z_lirf_public_sources_d90f9eab'
    staged=ROOT/'outputs/runs/20261106T084019Z_lirf_input_qualification_62b909f8'
    model=ROOT/'outputs/runs/20261106T085314Z_lirf_weather_model_audit_86776d47'
    dictionary=ROOT/'outputs/runs/20261106T085959Z_icasa_dictionary_8bbb3db6'
    global ACTIVE_RUN
    run=new_run(ROOT,'lirf2008_input_crosswalk');ACTIVE_RUN=run;print(run,flush=True)
    for folder in (field,staged,model,dictionary):assert read(folder/'verification.json')['passed']
    assert all(sha256(field/f['file'])==f['sha256'] for f in read(field/'verification.json')['files'])
    for folder in (staged,model):
        assert all(sha256(folder/name)==digest for name,digest in read(folder/'derived_files_sha256.json').items())
    assert all(sha256(dictionary/f['path'])==f['sha256'] for f in read(dictionary/'verification.json')['files'])
    wanted={'PLDP','PLPOP','PLRS','FEAMN','ICBL','ICNH4','ICNO3','ICH2O','SLLB','SLBDM','SLCLY','SLSND','SLSIL','SLFC1','IRVAL'}
    definitions=[]
    for filename in ('Management_info.csv','Soils_data.csv'):
        with (dictionary/'CSV'/filename).open(encoding='utf-8-sig',newline='') as stream:
            definitions += [dict(source=filename,**row) for row in csv.DictReader(stream) if row['Code_Query'] in wanted]
    units={r['Code_Query']:r['Unit_or_type'] for r in definitions}
    assert units['ICNO3']=='ppm' and units['ICNH4']=='ppm' and units['SLLB']=='cm'
    assert units['SLBDM']=='g/cm3' and units['SLCLY']=='%' and units['SLFC1']=='cm3/cm3'
    with (dictionary/'CSV/Management_codes.csv').open(encoding='utf-8-sig',newline='') as stream:
        codes=[row for row in csv.DictReader(stream) if row['Code'] in ('FE001','FE005','FE010','IR004','IR005')]
    ace=read(model/'decoded_ace.json');experiment=ace['experiments'][0]
    soil=ace['soils'][0]['soilLayer'];initial=experiment['initial_conditions']['soilLayer']
    flags=soil_schema_flags(soil)
    assert len([f for f in flags if f['issue']=='volumetric_field_capacity_outside_0_1'])==1
    assert len([f for f in flags if f['issue']=='texture_percent_sum_not_100'])==9
    inventory=initial_inventory(soil,initial)
    top60=initial_inventory(soil,[row for row in initial if float(row['icbl'])<=60])
    management=[r for r in read(staged/'daily_management_source_columns.json') if r['year']==2008 and r['treatment']==1]
    by_date={r['date'].replace('-',''):r for r in management}
    events=experiment['management']['events']
    package_irrig=defaultdict(float);package_n=defaultdict(float)
    for event in events:
        if event['event']=='irrigation':package_irrig[event['date']]+=float(event['irval'])
        if event['event']=='fertilizer':package_n[event['date']]+=float(event['feamn'])
    sprinkler='20080521';assert by_date[sprinkler]['precipitation_column_mm']==21
    assert next(e for e in events if e['date']==sprinkler and e['event']=='irrigation')['irop']=='IR004'
    irrigation=[]
    for date in sorted(set(package_irrig)|{day for day,row in by_date.items() if row['drip_irrigation_column_mm']}):
        row=by_date.get(date)
        field_drip=(row['drip_irrigation_column_mm'] or 0) if row else None
        field_sprinkler=21 if date==sprinkler else 0
        comparison=field_drip+field_sprinkler if field_drip is not None else None
        irrigation.append(dict(date=date,package_mm=package_irrig.get(date,0),
            field_drip_mm=field_drip,identified_sprinkler_in_precip_mm=field_sprinkler,
            package_minus_field_classified_mm=package_irrig.get(date,0)-comparison if comparison is not None else None,
            source_row=row['source_row'] if row else None))
    fertilizer=[]
    initial_field=management[0]
    for date in sorted(set(package_n)|{day for day,row in by_date.items()
            if row['n_applied_or_initial_soil_n_column_kg_ha'] is not None and row is not initial_field}):
        row=by_date.get(date)
        value=row['n_applied_or_initial_soil_n_column_kg_ha'] if row else None
        fertilizer.append(dict(date=date,package_elemental_n_kg_ha=package_n.get(date,0),
            field_applied_n_column_kg_ha=value,
            package_minus_field_kg_n_ha=package_n.get(date,0)-value if value is not None else None,
            before_field_initial_n_observation=date<initial_field['date'].replace('-',''),
            package_events=[e for e in events if e['event']=='fertilizer' and e['date']==date],
            source_row=row['source_row'] if row else None))
    weather={r['w_date']:r for r in ace['weathers'][0]['dailyWeather']}
    rain=[dict(date=day,field_precip_column_mm=row['precipitation_column_mm'],
        field_rain_after_identified_sprinkler_removal_mm=(row['precipitation_column_mm'] or 0)-(21 if day==sprinkler else 0),
        package_rain_mm=float(weather[day]['rain']),source_row=row['source_row']) for day,row in by_date.items()]
    drip_total=sum(r['drip_irrigation_column_mm'] or 0 for r in management)
    field_irrig=drip_total+21;package_irrig_total=sum(package_irrig.values())
    assert abs(field_irrig-package_irrig_total)<1e-8
    workbook=openpyxl.load_workbook(field/'LIRF_Maize_2008.xlsx',data_only=True)
    log_records=[r for r in read(staged/'crop_logs.json') if r['year']==2008 and
                 (r['category'] in ('Fertilizer','Planting','Harvest') or r['date']=='2008-08-26')]
    first_water=next(r for r in management if any(isinstance(v,(float,int)) for v in r['soil_water_percent_by_source_columns'].values()))
    soil_book=openpyxl.load_workbook(field/'LIRF_Soils.xlsx',data_only=True)
    soil_context=dict(package_soil_id=ace['soils'][0]['soil_id'],package_layers=soil,
        field_bulk_density_section_D=[dict(row=row[0].row,cells={c.coordinate:c.value for c in row if c.value is not None})
            for row in soil_book['Bulk Density'] if row[0].value=='D'],
        field_soil_definitions=[dict(row=row[0].row,cells={c.coordinate:c.value for c in row if c.value is not None})
            for row in soil_book['Data Description']],
        physical_water_order_passes=all(0<=float(s['slll'])<=float(s['sldul'])<=float(s['slsat'])<=1 for s in soil),
        measured_site_to_package_profile_join_verified=False,
        initial_date=experiment['initial_conditions']['icdat'],field_first_n_observation=initial_field,
        field_first_water_observation=first_water,
        package_inventory=inventory,package_top60_inventory=top60,
        date_matched_initial_state_validation=False)
    field_rain=sum(r['field_rain_after_identified_sprinkler_removal_mm'] for r in rain)
    package_rain=sum(r['package_rain_mm'] for r in rain)
    summary=dict(passed=True,scope='source crosswalk and unit/inventory diagnosis, not native field validation',
        dictionary_revision=read(dictionary/'verification.json')['revision'],
        current_dictionary_proves_historical_exporter_units=False,
        package_initial_date=experiment['initial_conditions']['icdat'],
        package_initial_inventory=inventory,package_top60_inventory=top60,
        initial_observation_dates_differ=True,soil_schema_flags=flags,
        initial_layers=len(initial),soil_layers=len(soil),
        irrigation_total_mm=package_irrig_total,field_drip_mm=drip_total,
        field_sprinkler_identified_mm=21,
        irrigation_daily_disagreements=[r for r in irrigation if abs(r['package_minus_field_classified_mm'] or 0)>1e-8],
        rain_overlap_dates=len(rain),rain_overlap_start=min(by_date),rain_overlap_end=max(by_date),
        package_rain_overlap_mm=package_rain,field_rain_overlap_mm=field_rain,
        package_minus_field_rain_overlap_mm=package_rain-field_rain,
        package_fertilizer_n_total_kg_ha=sum(package_n.values()),
        package_fertilizer_n_after_field_initial_date_kg_ha=sum(v for date,v in package_n.items() if date>=initial_field['date'].replace('-','')),
        field_fertilizer_n_after_initial_observation_kg_ha=sum(r['n_applied_or_initial_soil_n_column_kg_ha'] or 0 for r in management[1:]),
        irrigation_water_n_conditional_kg_ha=drip_total*.25,
        irrigation_water_n_condition='only under documented constant25mgN/L for recorded drip; sprinkler source not assigned',
        package_irrigation_water_n_explicitly_recorded=False,
        planting_date_matches_log=next(e for e in events if e['event']=='planting')['date']=='20080512',
        automatic_texture_rescaling=False,automatic_slfc1_repair=False,automatic_native_input_export_allowed=False,
        public_study_role='independent_validation_base_crop_water_response',
        research_ready=False,main_training_allowed=False,quantitative_fit_ready=False,
        evidence={str(p.relative_to(ROOT)):sha256(p) for p in (field/'verification.json',staged/'verification.json',
            model/'verification.json',dictionary/'verification.json')})
    for name,value in [('dictionary_definitions',definitions),('management_codes',codes),('irrigation_crosswalk',irrigation),
        ('fertilizer_crosswalk',fertilizer),('rain_crosswalk',rain),('soil_initial_context',soil_context),('crop_log_support',log_records)]:
        write_json(run/f'{name}.json',value)
    write_json(run/'verification.json',summary)
    write_json(run/'derived_files_sha256.json',{p.name:sha256(p) for p in run.iterdir() if p.is_file()})
    print(json.dumps({k:summary[k] for k in ('irrigation_total_mm','package_minus_field_rain_overlap_mm',
        'package_fertilizer_n_total_kg_ha','field_fertilizer_n_after_initial_observation_kg_ha','irrigation_water_n_conditional_kg_ha')},indent=2))


if __name__=='__main__':
    try:main()
    except Exception as exc:
        if 'ACTIVE_RUN' in globals():write_json(ACTIVE_RUN/'failure.json',dict(passed=False,exception=repr(exc),research_ready=False))
        raise
