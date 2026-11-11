"""Plot FC reconstruction and unresolved SWD evidence; no correction or fitting."""
from datetime import date,timedelta
import json
from pathlib import Path
import statistics
import sys
import openpyxl
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.fc_uncertainty import summarize_fc_plots


def main():
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    source=ROOT/'outputs/runs/20261106T083612Z_lirf_public_sources_d90f9eab'
    prior=ROOT/'outputs/runs/20261106T142102Z_lirf_water_depths_5a3fa17b'
    staged=ROOT/'outputs/runs/20261106T084019Z_lirf_input_qualification_62b909f8'
    for item in read(source/'verification.json')['files']:assert sha256(source/item['file'])==item['sha256']
    for folder in (prior,staged):
        for name,digest in read(folder/'derived_files_sha256.json').items():assert sha256(folder/name)==digest
    yields=read(staged/'plot_yields.json')
    run=new_run(ROOT,'lirf_fc_aggregation');print(run,flush=True)
    aggregation=[];stocks=[];cases=[];plot_records=[]
    for year in range(2008,2012):
        filename=f'LIRF_Maize_{year}.xlsx';w=openpyxl.load_workbook(source/filename,read_only=True,data_only=True)
        f=openpyxl.load_workbook(source/filename,read_only=True,data_only=False)
        seasonal=list(w['Seasonal']);j=next(i for i,c in enumerate(seasonal[4]) if c.value=='0 - 15 cm')
        assert seasonal[23][j].value=='0 - 15 cm'
        for treatment in range(1,7):
            rows=[row for row in seasonal[25:49] if row[j-1].value==treatment]
            assert len(rows)==4
            identities=[(row[0].value,row[1].value,row[2].value) for row in rows]
            assert {b for _,b,_ in identities}=={1,2,3,4} and len({p for _,_,p in identities})==4
            for row,(t,b,p) in zip(rows,identities):
                assert t==treatment and any(v['year']==year and v['plot']==p and v['block']==b and v['treatment']==t for v in yields)
                plot_records.append(dict(year=year,treatment=treatment,block=b,plot=p,source_file=filename,
                    cells=[dict(cell=c.coordinate,fc_percent=c.value,number_format=c.number_format) for c in row[j:j+7]]))
            meanrow=seasonal[treatment+5];sdrow=seasonal[treatment+13]
            assert meanrow[j-1].value==sdrow[j-1].value==treatment
            for k in range(7):
                values=[row[j+k].value for row in rows]
                mean=statistics.fmean(values);sd=statistics.stdev(values)
                aggregation.append(dict(year=year,treatment=treatment,depth_header=seasonal[4][j+k].value,
                    plot_cells=[row[j+k].coordinate for row in rows],
                    reported_mean_cell=meanrow[j+k].coordinate,reported_sd_cell=sdrow[j+k].coordinate,
                    reported_mean=meanrow[j+k].value,reconstructed_mean=mean,
                    mean_difference=mean-meanrow[j+k].value,reported_sd=sdrow[j+k].value,
                    reconstructed_sample_sd=sd,sd_difference=sd-sdrow[j+k].value,
                    exact_stored_numeric_match=abs(mean-meanrow[j+k].value)<1e-10 and abs(sd-sdrow[j+k].value)<1e-10))
            for depth,n in ((105,4),(135,5)):
                summary=summarize_fc_plots([[r[j+k].value for k in range(n)] for r in rows],[15]+[30]*(n-1))
                assert abs(summary['sample_sd_fc_storage_mm']**2-summary['covariance_stock_variance_mm2'])<1e-8
                stocks.append(dict(year=year,treatment=treatment,depth_cm=depth,plot_ids=[p for _,_,p in identities],
                    blocks=[b for _,b,_ in identities],summary=summary,
                    scope='static same-plot FC dispersion; not daily SWC, change or model-residual SE'))
            if year==2010 and treatment in (2,3):
                data=list(w[f'Tmnt{treatment}']);forms=list(f[f'Tmnt{treatment}'])
                measured=[(i,row) for i,row in enumerate(data,1) if i>=5 and isinstance(row[0].value,(int,float)) and 1<=row[0].value<=365 and all(isinstance(c.value,(int,float)) for c in row[4:8])]
                index=next(i for i,(number,row) in enumerate(measured) if number==57)
                neighbors=[]
                for number,row in measured[max(0,index-1):index+2]:
                    stock=sum(c.value*d*.1 for c,d in zip(row[4:8],[15,30,30,30]))
                    fcstock=next(s for s in stocks if s['year']==year and s['treatment']==treatment and s['depth_cm']==105)['summary']['mean_fc_storage_mm']
                    neighbors.append(dict(date=(date(year,1,1)+timedelta(days=int(row[0].value)-1)).isoformat(),
                        source_row=number,water_stock_mm=stock,plot_derived_mean_fc_stock_mm=fcstock,
                        reported_swd_mm=row[29].value,reconstructed_swd_mm=fcstock-stock,
                        residual_mm=fcstock-stock-row[29].value if isinstance(row[29].value,(int,float)) else None,
                        cells=[dict(cell=c.coordinate,value=c.value,formula=forms[number-1][c.column-1].value if forms[number-1][c.column-1].data_type=='f' else None) for c in [*row[4:8],row[29]]]))
                cases.append(dict(year=year,treatment=treatment,neighbors=neighbors,
                    fc_summary_reconstruction_explains_difference=False,daily_plot_swc_available=False,
                    error_cell_identified=False,correction_applied=False))
    assert len(plot_records)==96 and len(aggregation)==168 and len(stocks)==48
    source_method=PdfReader(source/'LIRF_Methodology_r1.pdf').pages[10].extract_text()
    contract=dict(common_depths_cm=[105,135],primary_candidate='observed-date treatment-mean volumetric water stock',
        daily_records_independent=False,depth_records_independent=False,field_replicates_per_treatment=4,
        split_unit='entire LIRF2008-2011 study; retain independent-validation role',
        retain_block_and_year_identity=True,static_fc_sd_is_daily_swc_sd=False,
        unknowns=['daily plot-level SWC and covariance','temporal measurement covariance','instrument/calibration errors for stock changes','native field input/cultivar/initial state mapping'],
        fixed_error_tolerance_for_model_comparison_mm=None,model_scoring_allowed=False,
        adjusted_daily_etc_independent_validation_target=False,
        unresolved_two_swd_rows_preserved=True,deep_profile_definition_resolved=False,
        independent_study_count_increase=0,research_ready=False,main_training_allowed=False)
    for name,value in [('plot_fc_records',plot_records),('fc_mean_sd_reconstruction',aggregation),('plot_fc_storage_dispersion',stocks),
        ('swd_discrepancy_cases',cases),('water_comparison_contract',contract),('methodology_water_balance',dict(physical_page=11,text=source_method))]:write_json(run/f'{name}.json',value)
    report=dict(passed=True,plot_fc_records=96,source_fc_values=672,mean_and_sd_pairs=168,
        exact_stored_mean_sd_pairs=sum(r['exact_stored_numeric_match'] for r in aggregation),
        exact_2010_2011_pairs=sum(r['exact_stored_numeric_match'] for r in aggregation if r['year']>=2010),
        static_fc_stock_summaries=48,unresolved_swd_cases=2,
        aggregation_differences_by_year={str(y):dict(max_mean_percent=max(abs(r['mean_difference']) for r in aggregation if r['year']==y),max_sd_percent=max(abs(r['sd_difference']) for r in aggregation if r['year']==y)) for y in range(2008,2012)},
        source_sha256={item['file']:item['sha256'] for item in read(source/'verification.json')['files'] if item['file'].startswith('LIRF_Maize_') or item['file']=='LIRF_Methodology_r1.pdf'},
        source_values_corrected=0,model_error_tolerance_selected=False,new_native_simulations=0,new_training_runs=0,
        research_ready=False,main_training_allowed=False,
        scope='FC aggregation, paired-depth static dispersion and unresolved-source contract; not field validation')
    write_json(run/'verification.json',report)
    write_json(run/'derived_files_sha256.json',{p.name:sha256(p) for p in run.iterdir() if p.is_file()})
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
