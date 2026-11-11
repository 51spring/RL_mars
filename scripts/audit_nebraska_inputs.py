"""Read-only source reconciliation; diagnostics never become policy/model inputs."""
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import json
from pathlib import Path
import statistics
import sys
import openpyxl
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256


def main():
    source=ROOT/'outputs/runs/20261106T232619Z_field_calibration_candidates_9542cf1f'
    paper=ROOT/'outputs/runs/20261106T233714Z_nebraska_paper_384ae31b'
    workbook=source/'nebraska_Manuscript_data.xlsx'
    assert sha256(workbook)=='f2f14d1de1e581f55696dde1c8b950af576b239aec66f821ce21fd1294d51bfb'
    acquired=json.loads((paper/'verification.json').read_text(encoding='utf-8'))
    assert acquired['source_sha256']==sha256(paper/'Li2023.pdf')
    wb=openpyxl.load_workbook(workbook,read_only=True,data_only=True)
    raw=list(wb['yield_raw']);summary=list(wb['yield_summary'])
    groups=defaultdict(list);units=defaultdict(list)
    factors=[(i,c,s) for i in ('deficit','full') for c in ('rye','NoCover') for s in ('removal','retention')]
    codes=['DCA','DCN','DXA','DXN','FCA','FCN','FXA','FXN']
    paper_codes=['DCM','DCR','DXM','DXR','FCM','FCR','FXM','FXR']
    for row in raw[1:]:
        vals=[c.value for c in row]
        groups[(vals[2],*vals[4:7])].append(row)
        units[str(vals[0])].append(dict(year=vals[2],treatment=vals[3],source_row=row[0].row))
    assert len(groups)==72 and len(units)==32
    # Floors only classify arithmetic discrepancies for review; they are NOT
    # confidence limits or native/field-model acceptance tolerances.
    endpoints=[('grain',8,2,1000,1e-6),('biomass',9,12,1000,1e-6),
               ('grain_n',10,22,1,1e-4),('biomass_n',11,32,1,1e-4)]
    comparisons=[]
    for endpoint,col,offset,scale,floor in endpoints:
        for row in summary[offset:offset+9]:
            for j,factor in enumerate(factors):
                members=groups[(row[0].value.year,*factor)]
                assert all(r[1].value==row[0].value for r in members)
                values=[r[col].value for r in members if isinstance(r[col].value,(int,float))]
                mean=statistics.fmean(values)/scale
                sd=statistics.stdev(values)/scale if len(values)>1 else None
                stated_mean,stated_sd=row[1+2*j].value,row[2+2*j].value
                assert isinstance(stated_mean,(int,float))
                delta_mean=mean-stated_mean
                delta_sd=sd-stated_sd if sd is not None and isinstance(stated_sd,(int,float)) else None
                comparisons.append(dict(endpoint=endpoint,year=row[0].value.year,code=codes[j],n=len(values),
                    source_cells=[r[col].coordinate for r in members],summary_mean_cell=row[1+2*j].coordinate,
                    summary_sd_cell=row[2+2*j].coordinate,scale_raw_to_summary=scale,
                    unit='Mg/ha' if scale==1000 else 'kg N/ha',raw_mean=mean,raw_sample_sd=sd,
                    reported_mean=stated_mean,reported_sd=stated_sd,mean_delta=delta_mean,sd_delta=delta_sd,
                    arithmetic_review_floor=floor,mean_difference_flag=abs(delta_mean)>floor,
                    sd_difference_flag=abs(delta_sd)>floor if delta_sd is not None else None,
                    uncertainty_qualified=False))
    counts={endpoint:dict(comparisons=sum(x['endpoint']==endpoint for x in comparisons),
        mean_difference_flags=sum(x['endpoint']==endpoint and x['mean_difference_flag'] for x in comparisons),
        sd_difference_flags=sum(x['endpoint']==endpoint and x['sd_difference_flag'] is True for x in comparisons),
        uncomputable_sd=sum(x['endpoint']==endpoint and x['raw_sample_sd'] is None for x in comparisons))
        for endpoint,*_ in endpoints}
    precipitation=[]
    for row in list(wb['precipitation'])[1:]:
        date=row[0].value
        if isinstance(date,str):
            date=datetime.strptime(date,'%d/%m/%Y') # explicit DD/MM/YYYY source header
            method='source_header_DD/MM/YYYY'
        else:
            assert isinstance(date,datetime)
            method='excel_datetime'
        assert isinstance(row[1].value,(int,float))
        precipitation.append(dict(date=date.date().isoformat(),mm=row[1].value,
            source_cell=row[0].coordinate,original_date=str(row[0].value),method=method))
    dates=[datetime.fromisoformat(r['date']).date() for r in precipitation]
    expected={min(dates)+timedelta(days=i) for i in range((max(dates)-min(dates)).days+1)}
    precip_report=dict(rows=len(dates),first_date=str(min(dates)),last_date=str(max(dates)),
        duplicate_dates=len(dates)-len(set(dates)),missing_days=[str(d) for d in sorted(expected-set(dates))],
        source_header=wb['precipitation']['A1'].value,
        strings_parsed=sum(r['method']=='source_header_DD/MM/YYYY' for r in precipitation),
        original_workbook_modified=False,native_assignment_allowed=False)
    irrigation=defaultdict(list);missing=Counter()
    for row in list(wb['irrigation'])[1:]:
        date,treatment,amount,kind=[c.value for c in row]
        if not isinstance(amount,(int,float)):
            missing['amount_missing_or_nonnumeric']+=1
        if date is None:missing['date_missing']+=1
        if isinstance(amount,(int,float)):
            assert isinstance(date,datetime)
            irrigation[(date.date().isoformat(),treatment,amount,kind)].append(row[2].coordinate)
    event_candidates=[]
    for (date,treatment,amount,kind),cells in sorted(irrigation.items()):
        event_candidates.append(dict(date=date,treatment=treatment,amount_cm=amount,amount_mm=amount*10,
            kind=kind,source_cells=cells,multiplicity=len(cells),
            deduplicated_event_qualified=False,unit_ids_not_present=True))
    totals=defaultdict(lambda:dict(distinct_tuple_mm=0,all_rows_mm=0,distinct_tuples=0))
    for event in event_candidates:
        key=(event['date'][:4],event['treatment']);v=totals[key]
        v['distinct_tuple_mm']+=event['amount_mm'];v['all_rows_mm']+=event['amount_mm']*event['multiplicity'];v['distinct_tuples']+=1
    irrigation_report=dict(numeric_rows=sum(len(c) for c in irrigation.values()),distinct_numeric_tuples=len(irrigation),
        multiplicity_histogram=dict(Counter(len(c) for c in irrigation.values())),missing=dict(missing),
        zero_amount_rows=sum(len(c) for k,c in irrigation.items() if k[2]==0),
        no_zero_imputation=True,no_native_event_schedule_selected=True,
        repeated_rows_may_represent_field_replicates_but_unverified=True)
    pages=PdfReader(paper/'Li2023.pdf').pages
    assert 'four field replicates' in pages[1].extract_text()
    assert '0 % moisture content' in pages[2].extract_text()
    fields=[
        ('site',2,dict(latitude=40.582,longitude=-98.144,elevation_m=552),'reported'),
        ('design',2,dict(type='randomized complete block split-split plot',replicates=4,
            whole_plot='irrigation',split_plot='cover crop',split_split_plot='stover'),
            'reported_design; block IDs and hierarchy-to-unit mapping unresolved'),
        ('repeated_years',3,dict(year_as_repeated_measure=True),'source analysis confirmed; unit dependence must be preserved'),
        ('grain_endpoint',3,dict(moisture_percent=0,unit='Mg/ha'),'dry endpoint confirmed; detailed sampling in Schmer2020'),
        ('surface_soil',2,dict(depth_cm=[0,30],bulk_density_g_cm3=1.25,pH_water_1to1=6.8,SOC_g_kg=16.2),
            'baseline scalar only; not complete soil profile'),
        ('soil_layers',3,dict(sampling_month='2010-10',sampling_depths_cm=[0,7.5,15,30,60,90,120,150],
            model_depths_cm=[0,15,30,60,90,120,150]),'layer values not acquired; after initial planting'),
        ('soil_table_reference',3,dict(reference_as_printed='Table 1',actual_table1='ANOVA p-values'),
            'source cross-reference inconsistency retained; no numeric soil layer invented'),
        ('irrigation',2,dict(deficit_fraction_of_full=0.6,timing_reference='Fig S1'),
            'schedule and repeated workbook rows not qualified'),
        ('fertilizer',2,dict(material='UAN32-0-0',rate_kg_N_ha=200,stage='V4-V6',method='sidedress coulter injection'),
            'rate independently confirmed in prose; exact annual dates/depth not acquired'),
        ('cover_crop',2,dict(crop='winter cereal rye',seed_kg_ha=112,planting='late October/early November',
            termination='chemically before corn planting late April/early May'),'exact annual dates/initial carryover unresolved'),
        ('stover',2,dict(removal_fraction_approx=0.59,timing='after grain harvest'),'not live-leaf defoliation'),
        ('weather',3,dict(station='HARVARD 4SW',distance_km_approx=1.5),
            'station name only; full daily TMAX/TMIN/SRAD not acquired'),
        ('initialization',3,dict(fast_intermediate_slow_humus_percent=[1,9,90],method='RZWQM2 Initialization Wizard'),
            'model assumptions not observed DSSAT initial states; initial mineral N/water unresolved'),
        ('model_calibration',3,dict(model='RZWQM2',calibration_treatment='FXR',workbook_code='FXN',
            replicate_average_for_input=4,nitrification_N2O_fraction=0.044),
            'same study used for calibration; no independent-study claim; not DSSAT cultivar coefficients'),
        ('cultivar',3,None,'cultivar identity/genetic coefficients and calibration exposure unqualified'),
        ('management',3,dict(references=['Schmer2020','Sindelar2019a']),
            'full annual corn planting/harvest/fertilizer/pesticide schedule and density not acquired'),
        ('uncertainty',4,dict(source_figure_envelope_multiplier_sd=3.9),
            'not adopted: conflicting source SD; source probability claim not independently validated; no SE/covariance inferred'),
    ]
    dossier=[dict(id=key,pdf_page=page,reported=value,status=status,native_assignment_allowed=False) for key,page,value,status in fields]
    run=new_run(ROOT,'nebraska_input_audit');print(run,flush=True)
    outputs={'raw_summary_comparisons':comparisons,'arithmetic_reconciliation_counts':counts,
        'unit_history':dict(units),'precipitation_date_candidates':precipitation,'precipitation_profile':precip_report,
        'irrigation_repeated_tuple_candidates':event_candidates,'irrigation_profile':irrigation_report,
        'irrigation_seasonal_sum_diagnostics':[dict(year=y,treatment=t,**v,native_assignment_allowed=False) for (y,t),v in sorted(totals.items())],
        'source_input_dossier':dossier,'treatment_crosswalk':[dict(workbook=c,paper=p,factors=f) for c,p,f in zip(codes,paper_codes,factors)]}
    for name,data in outputs.items():write_json(run/f'{name}.json',data)
    report=dict(passed=True,scope='source reconciliation completed, not evidence that source summaries match or model is valid',
        source_sha256={'workbook':sha256(workbook),'paper':sha256(paper/'Li2023.pdf')},
        endpoint_year_treatment_comparisons=len(comparisons),arithmetic_counts=counts,
        arithmetic_review_floors={'mass_Mg_ha':1e-6,'N_kg_ha':1e-4},
        review_floor_basis='conservative reporting-resolution screen (0.001 kg dry mass/ha or 0.0001 kg N/ha); not measurement/native/fit tolerance; full signed differences retained',
        planned_grain_slots=9*8*4,available_grain_rows=len(raw)-1,unavailable_grain_slots=9*8*4-len(raw)+1,
        unit_ids=len(units),unit_treatment_assignment_stable=all(len({v['treatment'] for v in history})==1 for history in units.values()),
        block_mapping_qualified=False,precipitation=precip_report,irrigation=irrigation_report,input_dossier_fields=len(dossier),
        original_workbook_modified=False,summary_values_overwritten=False,native_input_assignments=0,
        active_studies_added=0,new_native_simulations=0,new_training_runs=0,quantitative_fit_ready=False,
        research_ready=False,main_training_allowed=False,
        next_task='Acquire official supplementary material and Schmer2020/Sindelar2019a management sources; resolve source SD, unit hierarchy and daily event semantics before fitting')
    assert sha256(workbook)==report['source_sha256']['workbook']
    write_json(run/'verification.json',report)
    write_json(run/'derived_files_sha256.json',{p.name:sha256(p) for p in run.iterdir() if p.is_file()})
    wb.close()
    print(json.dumps({k:report[k] for k in ('arithmetic_counts','precipitation','irrigation','unavailable_grain_slots')},indent=2))


if __name__=='__main__':main()
