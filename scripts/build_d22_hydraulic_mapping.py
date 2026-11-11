"""Read-only source extraction with explicit laboratory/field/depth boundaries."""
import json
from pathlib import Path
import statistics
import sys
from datetime import date,timedelta
import openpyxl
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.soil_coverage import depth_coverage


def main():
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    source=ROOT/'outputs/runs/20261106T083612Z_lirf_public_sources_d90f9eab'
    prior=ROOT/'outputs/runs/20261106T135234Z_lirf_evidence_ledger_eaaf34b5'
    cross=ROOT/'outputs/runs/20261106T090447Z_lirf2008_input_crosswalk_dbb8c54c'
    for f in read(source/'verification.json')['files']:assert sha256(source/f['file'])==f['sha256']
    for directory in (prior,cross):
        for name,h in read(directory/'derived_files_sha256.json').items():assert sha256(directory/name)==h
    soil=openpyxl.load_workbook(source/'LIRF_Soils.xlsx',read_only=True,data_only=True)
    formulas=openpyxl.load_workbook(source/'LIRF_Soils.xlsx',read_only=True,data_only=False)
    maize=openpyxl.load_workbook(source/'LIRF_Maize_2008.xlsx',read_only=True,data_only=True)
    def cells(book,sheet):return {c.coordinate:c.value for row in book[sheet] for c in row if c.value is not None}
    mr=cells(soil,'Moisture Release');mf=cells(formulas,'Moisture Release')
    desc=cells(soil,'Data Description');bd=cells(soil,'Bulk Density')
    reference=read(prior/'d22_soil_candidate.json')
    run=new_run(ROOT,'d22_hydraulic_mapping');print(run,flush=True)
    horizons=[];mean_checks=0;subsamples=0
    for row in (10,11,12,13):
        assert mr[f'A{row}']==5 and mr[f'B{row}']=='D22'
        item=dict(source_row=row,top_cm=mr[f'C{row}'],bottom_cm=mr[f'D{row}'],
            provenance='2007 soil analysis title; general characterization2007/08; exact core date unresolved',
            laboratory_disturbed_sample=True,volumetric_water_content=True,observations=[])
        assert any(h['top_cm']==item['top_cm'] and h['bottom_cm']==item['bottom_cm'] for h in reference['horizons'])
        for pressure,a,b,mean in zip((3,10,33,50,100,1475),('N','O','P','Q','R','S'),('U','V','W','X','Y','Z'),('AB','AC','AD','AE','AF','AG')):
            observations=[dict(cell=f'{col}{row}',value=mr[f'{col}{row}']) for col in (a,b) if f'{col}{row}' in mr]
            values=[o['value'] for o in observations]
            assert values and all(isinstance(v,(float,int)) and 0<v<1 for v in values)
            cached=mr[f'{mean}{row}'];assert abs(statistics.fmean(values)-cached)<2e-9
            mean_checks+=1;subsamples+=len(values)
            item['observations'].append(dict(pressure_kpa=pressure,source_header_label='theta1500' if pressure==1475 else f'theta{pressure}',
                subsamples=observations,n=len(values),sample_sd=statistics.stdev(values) if len(values)>1 else None,
                mean_cell=f'{mean}{row}',cached_mean=cached,source_formula=mf[f'{mean}{row}'],
                note='technical subsamples, not independent field replicates'))
        assert all(a['cached_mean']>=b['cached_mean'] for a,b in zip(item['observations'],item['observations'][1:]))
        item['texture_estimates']={col:dict(cell=f'{col}{row}',value=mr[f'{col}{row}']) for col in ('K','L','M')}
        item['reported_taw']=dict(cell=f'AH{row}',value=mr[f'AH{row}'])
        assert abs(item['observations'][2]['cached_mean']-item['observations'][-1]['cached_mean']-mr[f'AH{row}'])<2e-9
        item['field_fc_points']=[dict(depth_cm=mr[f'{d}{row}'],value=mr[f'{v}{row}'],reported_sd=mr[f'{s}{row}'],cells=[f'{d}{row}',f'{v}{row}',f'{s}{row}'])
            for d,v,s in [('AJ','AK','AL'),('AM','AN','AO')] if f'{d}{row}' in mr]
        item['native_LL_DUL_SAT_selected']=False;horizons.append(item)
    measured=[(h['top_cm'],h['bottom_cm']) for h in horizons]
    coverage=dict(full_profile=depth_coverage(measured,[(0,200)]),
        native10_layers=depth_coverage(measured,list(zip((0,5,15,30,45,60,90,120,150,180),(5,15,30,45,60,90,120,150,180,200)))),
        scope='interval intersection only; full geometry does not prove hydraulic or agronomic equivalence')
    density=[dict(depth_label_cm=depth,mean_g_cm3=bd[f'{m}24'],reported_sd=bd[f'{s}24'],n=bd[f'{n}24'],
        cells=[f'{m}24',f'{s}24',f'{n}24']) for depth,m,s,n in zip((15,30,60,90,120,150,200),('C','F','I','L','O','R','U'),('D','G','J','M','P','S','V'),('E','H','K','N','Q','T','W'))]
    assert bd['A24']=='D' and bd['B24']==2
    rows=list(maize['Tmnt1']);first=next((i,r) for i,r in enumerate(rows,1) if i>=5 and all(isinstance(c.value,(int,float)) for c in r[4:11]))
    row_number,row=first;day=date(2008,1,1)+timedelta(days=row[0].value-1)
    sw=[dict(cell=c.coordinate,percent=c.value,fraction=c.value/100) for c in row[4:11]]
    header_layers=[(0,15),(15,45),(45,75),(75,105),(105,135),(135,165),(165,200)]
    description_layers=[(0,15),(15,45),(45,75),(75,105),(105,135),(135,175),(175,225)]
    stock=lambda layers:sum(o['fraction']*(b-a)*10 for o,(a,b) in zip(sw,layers))
    initial=dict(package_initial_date=read(cross/'soil_initial_context.json')['initial_date'],
        field_water_date=day.isoformat(),source_row=row_number,water=sw,
        sampling_population='T1 mean of4field replicates, not D22 individual plot',
        header_layers_cm=header_layers,description_layers_cm=description_layers,
        header_depth_200cm_stock_mm=stock(header_layers),description_depth_225cm_stock_mm=stock(description_layers),
        stock_interpretation_selected=False,source_depth_conflict_resolved=False,
        field_water_definition_cell='LIRF_Maize_2008.xlsx Data Descriptions C11',
        package_initial_water_validated=False,field_nitrogen_context=read(cross/'soil_initial_context.json')['field_first_n_observation'])
    definitions=dict(soil={k:v for k,v in desc.items() if k.startswith('B') or k=='A1'},
        first_water_definition=maize['Data Descriptions']['C11'].value,
        fc_period_metadata=['B31: average2007-2014','B61/B64: average5years'],
        fc_exact_years_and_sample_sizes_resolved=False,
        laboratory_pressure_label_1500_actual_definition_kpa=1475,
        no_native_conversion_or_profile_fill=True)
    for name,data in [('pressure_plate_candidates',horizons),('measurement_depth_coverage',coverage),
        ('pooled_D2_density',density),('initial_state_mapping',initial),('source_definitions',definitions)]:write_json(run/f'{name}.json',data)
    report=dict(passed=True,laboratory_horizons=4,pressure_mean_checks=mean_checks,technical_subsample_values=subsamples,
        one_subsample_horizons=[h['source_row'] for h in horizons if h['observations'][0]['n']==1],
        measured_coverage_cm=coverage['full_profile'][0]['covered_cm'],target_depth_cm=200,
        coverage_fraction=coverage['full_profile'][0]['fraction'],
        full_geometric_native_layers=sum(r['fully_covered'] for r in coverage['native10_layers']),
        pooled_density_depth_points=7,field_water_depth_definition_conflict=True,
        complete_measured_native_soil_profile=False,native_hydraulic_parameters_selected=False,
        native_initial_state_validated=False,new_native_simulations=0,new_training_runs=0,
        research_ready=False,main_training_allowed=False,
        source_sha256={str(p.relative_to(ROOT)):sha256(p) for p in (source/'LIRF_Soils.xlsx',source/'LIRF_Maize_2008.xlsx',prior/'verification.json',cross/'verification.json')},
        scope='source cells, technical subsample arithmetic and interval coverage only; no interpolation or native LL/DUL/SAT assignment')
    write_json(run/'verification.json',report)
    write_json(run/'derived_files_sha256.json',{p.name:sha256(p) for p in run.iterdir() if p.is_file()})
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
