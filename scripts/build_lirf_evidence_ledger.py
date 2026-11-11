"""Package/native/field differences with cell-level evidence; no input replacement."""
from collections import Counter
import json
from pathlib import Path
import shutil
import sys
import openpyxl
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.lirf_evidence import temperature_descriptions


def main():
    original=ROOT/'outputs/runs/20261106T083612Z_lirf_public_sources_d90f9eab'
    staged=ROOT/'outputs/runs/20261106T084019Z_lirf_input_qualification_62b909f8'
    native=ROOT/'outputs/runs/20261106T133507Z_lirf_native_qualification_f44ee96f'
    crosswalk=ROOT/'outputs/runs/20261106T090447Z_lirf2008_input_crosswalk_dbb8c54c'
    refs=ROOT/'outputs/runs/20261106T134643Z_lirf_reference_definitions_c197b893'
    dictionary=ROOT/'outputs/runs/20261106T085959Z_icasa_dictionary_8bbb3db6'
    def read(path):return json.loads(path.read_text(encoding='utf-8'))
    inputs=[original,staged,native,crosswalk,refs,dictionary]
    assert all(read(p/'verification.json')['passed'] for p in inputs)
    for item in read(original/'verification.json')['files']:
        assert sha256(original/item['file'])==item['sha256']
    assert sha256(refs/'DSSAT-vol3.pdf')==read(refs/'verification.json')['sha256']
    for folder,indexname in ((staged,'derived_files_sha256.json'),(crosswalk,'derived_files_sha256.json')):
        assert all(sha256(folder/p)==h for p,h in read(folder/indexname).items())
    run=new_run(ROOT,'lirf_evidence_ledger');print(run,flush=True)
    observations=[];definitions=[]
    for year in range(2008,2012):
        filename=f'LIRF_Weather_{year}.xlsx';w=openpyxl.load_workbook(original/filename,data_only=True,read_only=True)
        for row in w['Daily']:
            if not hasattr(row[0].value,'year'):continue
            observations.append(dict(date=row[0].value.date().isoformat(),tmean_c=row[2].value,
                source_file=filename,sheet='Daily',cell=row[2].coordinate,
                station_flag=row[18].value if len(row)>18 else None))
        definitions += [dict(file=filename,row=row[0].row,cells={c.coordinate:c.value for c in row if c.value is not None})
            for row in w['Data Description'] if any('Temperature' in str(c.value) or 'replaced' in str(c.value) for c in row)]
    climate=temperature_descriptions(observations)
    climate['source_period']='2008-2011; station-corrected records, not long-term normals'
    climate['station_flags_by_year']={str(y):dict(Counter(str(r['station_flag']) for r in observations if r['date'].startswith(str(y)))) for y in range(2008,2012)}
    climate['amp_definition_qualification']={
        'official_manual_source':'DSSAT-vol3.pdf physicalpage209 printed197 AppendixB Climate',
        'manual_climate_AMP':'half monthly mean temperature range',
        'pinned_native_source':'vendor/dssat-pdi-source/SPAM/STEMP.for',
        'native_formula':'TAMP / 2.0 in seasonal temperature terms',
        'mapping_from_climate_AMP_to_weather_TAMP_verified':False,
        'selected_native_tamp':None,'no_factor_selected_from_yield_fit':True}
    soil_book=openpyxl.load_workbook(original/'LIRF_Soils.xlsx',data_only=True,read_only=True)
    locations=[dict(site=row[0].value,plot=row[1].value,source_row=row[0].row)
        for row in soil_book['Moisture Release'].iter_rows(min_row=5,max_row=31) if row[1].value=='D22']
    assert len(locations)==4 and {r['site'] for r in locations}=={5}
    plots=[r for r in read(staged/'plot_yields.json') if r['year']==2008 and r['plot']=='D22']
    assert len(plots)==1 and plots[0]['treatment']==1 and plots[0]['block']==2
    horizons=[]
    for row in soil_book['Soil Texture']:
        if row[0].value!=5:continue
        horizons.append(dict(site_id=5,plot='D22',top_cm=row[5].value,bottom_cm=row[6].value,
            sand_percent=row[8].value,clay_percent=row[9].value,silt_percent=row[10].value,
            ph_saturated_paste=row[24].value,gravel_percent=row[7].value,
            source_file='LIRF_Soils.xlsx',sheet='Soil Texture',row=row[0].row,
            cells=dict(top=row[5].coordinate,bottom=row[6].coordinate,sand=row[8].coordinate,
                clay=row[9].coordinate,silt=row[10].coordinate,ph=row[24].coordinate)))
    assert len(horizons)==8 and horizons[0]['top_cm']==0
    assert all(abs(a['bottom_cm']-b['top_cm'])<1e-8 for a,b in zip(horizons,horizons[1:]))
    assert all(abs(h['sand_percent']+h['clay_percent']+h['silt_percent']-100)<1e-8 for h in horizons)
    soil_candidate=dict(site_id=5,plot='D22',treatment=1,block=2,year=2008,
        profile_depth_cm=horizons[-1]['bottom_cm'],native_diagnostic_depth_cm=200,
        missing_bottom_depth_cm=200-horizons[-1]['bottom_cm'],horizons=horizons,
        measured_ph_method='saturated paste',native_target_ph_definition='ICASA SLPHW: pH in water',
        ph_method_equivalence_verified=False,field_population_represented='one of four T1 plots, not treatment mean',
        plot_yield_reference=plots[0],moisture_release_subset_rows=locations,
        full_native_profile_ready=False,automatic_layer_fill_allowed=False,
        bulk_density_block_D2=[dict(row=row[0].row,cells={c.coordinate:c.value for c in row if c.value is not None})
            for row in soil_book['Bulk Density'] if row[0].value=='D' and row[1].value==2],
        bulk_density_sampling_scope='pooled2008-2015 NMM calibration cores, not verified2008 D22 horizon-specific density')
    entries=[]
    def entry(id,package,native_value,field,status,next_action,evidence):
        entries.append(dict(id=id,package=package,native_effective=native_value,field=field,
            status=status,next_action=next_action,evidence=evidence,automatic_field_replacement_allowed=False))
    native_ref='outputs/runs/20261106T133507Z_lirf_native_qualification_f44ee96f/verification.json'
    cross_ref='outputs/runs/20261106T090447Z_lirf2008_input_crosswalk_dbb8c54c/verification.json'
    entry('annual_temperature',None,20.,dict(period='2008-2011',daily_mean_air_c=climate['pooled_daily_mean_air_c']),
        'source_derived_candidate','Declare representative climate period and air/soil use; no automatic TAV replacement',
        ['daily_mean_air_observations.json',native_ref])
    entry('temperature_amplitude',None,5.,dict(full_monthly_range_c=climate['pooled_full_monthly_range_c'],half_monthly_range_c=climate['pooled_half_monthly_range_c']),
        'definition_mapping_unresolved','Resolve Climate AMP vs native weather TAMP convention before sensitivity/export',
        ['temperature_descriptions.json','DSSAT-vol3.pdf page209','vendor/dssat-pdi-source/SPAM/STEMP.for:340'])
    entry('soil_ph',None,7.,dict(site=5,plot='D22',range=[min(h['ph_saturated_paste'] for h in horizons),max(h['ph_saturated_paste'] for h in horizons)],method='saturated paste'),
        'measured_partial_method_unmatched','Verify method equivalence and individual-plot scenario; do not average pH across layers',
        ['d22_soil_candidate.json','LIRF_Soils.xlsx Data Description B5/B18',native_ref])
    entry('texture',dict(upper_clay=.05,upper_silt=.1),dict(diagnostic_upper_clay=5,diagnostic_upper_silt=10),
        dict(D22_top25_4cm=dict(sand=65,clay=19.5,silt=15.5)),
        'measured_partial','Use explicit D22 case only after full profile and hydraulic/initial-state mapping',
        ['d22_soil_candidate.json',native_ref])
    entry('soil_profile_depth',200,200,182.88,'measured_partial','Resolve bottom17.12cm without extrapolating measured horizons', ['d22_soil_candidate.json'])
    entry('bulk_density',dict(upper60cm=1.492),dict(upper60cm=1.492),dict(scope='D2 pooled2008-2015 cores'),
        'sampling_scope_unmatched','Keep pooled core statistics separate from2008 D22 measurements',['d22_soil_candidate.json'])
    entry('evaporation_parameter',None,dict(SLU1=6),dict(TEW_assumption_mm=12,residue_cover_assumption_fraction=.10),
        'different_quantity','Do not set SLU1 equal to TEW; establish module parameter meaning and sensitivity protocol',
        ['LIRF_Maize_2008.xlsx Data Descriptions C24',native_ref])
    entry('soil_fertility_factors',dict(SLNF=None,SLPF=.95),dict(SLNF=1.,SLPF=.95),None,
        'unmeasured_model_assumption','Retain source/default distinction and predeclare sensitivity, no independent-study fitting',[native_ref])
    entry('planting_date','20080512','2008133','2008-05-12','reported_technical_match','Keep date mapping frozen',['LIRF_Maize_2008.xlsx CropLog A10:D10',native_ref])
    entry('row_spacing_cm',75,75,76,'reported_difference','Resolve method precision before field profile export',['LIRF_Methodology_r1.pdf p5',native_ref])
    entry('cultivar','DEKALB521 IB1068 six coefficients','explicit048 transplanted row','DeKalb52-59 VT3',
        'identity_and_calibration_unresolved','Verify cultivar equivalence and calibration independence',[native_ref,'LIRF_Maize_2008.xlsx CropLog'])
    entry('initial_water',dict(date='20080101',mm=337.4),dict(date='20080101',mm=338.2),dict(first_treatment_mean_date='2008-06-10'),
        'observation_date_unmatched','Do not infer January stock from June observation',[cross_ref,native_ref])
    entry('initial_soil_n',dict(date='20080101',mineral_n_kg_ha=23.683296),dict(date='20080101',printed_mineral_n_kg_ha=23.7),dict(date='2008-05-10',no3_kg_ha=148,depth_cm=60),
        'observation_date_and_pool_unmatched','Keep nitrate vs total mineral N and differing dates separate',[cross_ref,native_ref])
    entry('irrigation_water_n',None,'allocation_unverified',dict(conditional_kg_ha=109.525,assumed_mg_n_l=25),
        'source_allocation_unresolved','Trace irrigation-water N in native uptake/balance before adding any N',[cross_ref])
    entry('fertilizer_n',dict(total_kg_n_ha=134.4),dict(kg_n_ha=134.4,applications=10),dict(post_may10_kg_n_ha=89.7),
        'period_and_schedule_unmatched','Compare same dates; do not reapply April fertilizer after May initial state',[cross_ref,native_ref])
    entry('rain_and_irrigation',dict(overlap_rain_mm=270,irrigation_mm=459.1),dict(input_events_verified=True),dict(overlap_rain_mm=229.886,irrigation_mm=459.1,one_day_event_disagreement=True),
        'source_schedule_unmatched','Resolve rain gauge/field source and39.5mm event day without yield-based selection',[cross_ref,native_ref])
    entry('weather_readback','seven-digit date header',dict(explicit_header_adapter=True,comparisons=2364,mismatches=0),dict(unfilled_original_fields=4),
        'verified_technical_only','Preserve native header adapter; do not label field gaps filled',[native_ref])
    entry('harvest_endpoint','dry grain kg_ha','HWAH dry grain kg_ha','Seasonal I column dry grain kg_ha',
        'quantity_basis_match','Define independent validation protocol/uncertainty before model-data comparisons',
        ['LIRF_Maize_2008.xlsx Data Descriptions C34','LIRF_Maize_2008.xlsx Seasonal I5 comment',native_ref])
    entry('biotic_and_frost_events','not explicitly parameterized','not validated',dict(logs='mites/hail/frost'),
        'uncontrolled_external_disturbance','Predeclare inclusion/covariate rules before simulation performance is inspected',[str((staged/'risk_logs.json').relative_to(ROOT))])
    assert len(entries)==len({e['id'] for e in entries})==19
    for name,data in [('daily_mean_air_observations',observations),('temperature_descriptions',climate),
        ('d22_soil_candidate',soil_candidate),('input_difference_ledger',entries),('temperature_source_definitions',definitions)]:
        write_json(run/f'{name}.json',data)
    png=ROOT/'outputs/lirf-climate-definition-209.png'
    shutil.copy2(png,run/png.name)
    report=dict(passed=True,ledger_items=len(entries),status_counts=dict(Counter(e['status'] for e in entries)),
        daily_mean_air_records=len(observations),soil_candidate_sites=1,soil_candidate_horizons=8,
        soil_candidate_plot='2008 T1 block2 D22',soil_candidate_depth_cm=182.88,
        partial_soil_profile_not_promoted=True,temperature_candidate_not_applied=True,
        native_parameters_changed=0,new_native_simulations=0,source_workbooks_modified=False,
        field_validation_ready=False,research_ready=False,main_training_allowed=False,
        source_evidence={str((p/'verification.json').relative_to(ROOT)):sha256(p/'verification.json') for p in inputs},
        code_definitions_sha256={str(p.relative_to(ROOT)):sha256(p) for p in (
            ROOT/'vendor/dssat-pdi-source/SPAM/STEMP.for',ROOT/'vendor/dssat-pdi-source/Weather/IPWTH_alt.for')},
        scope='source-measurement/default distinction and partial candidates, no model parameter selection or validation score')
    write_json(run/'verification.json',report)
    write_json(run/'derived_files_sha256.json',{p.name:sha256(p) for p in run.iterdir() if p.is_file()})
    print(json.dumps(dict(items=19,temperature_mean=climate['pooled_daily_mean_air_c'],temperature_full_range=climate['pooled_full_monthly_range_c'],temperature_half_range=climate['pooled_half_monthly_range_c'],d22_ph_range=[min(h['ph_saturated_paste'] for h in horizons),max(h['ph_saturated_paste'] for h in horizons)]),indent=2))


if __name__=='__main__':main()
