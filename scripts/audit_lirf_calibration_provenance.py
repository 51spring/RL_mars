"""Coefficient comparison and publication-specific data exposure, no fitting."""
import csv
import json
from pathlib import Path
import shutil
import sys
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256


def main():
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    package=ROOT/'outputs/runs/20261106T084700Z_lirf_model_package_f84234e1'
    decoded=ROOT/'outputs/runs/20261106T085314Z_lirf_weather_model_audit_86776d47'
    papers=ROOT/'outputs/runs/20261106T144434Z_lirf_calibration_sources_a5f2fc47'
    existing=ROOT/'outputs/runs/20261106T143430Z_lirf_availability_sources_018e2462'
    native=ROOT/'outputs/runs/20261106T133233Z_lirf_native_inputs_574604f1'
    assert read(papers/'verification.json')['passed']
    for item in read(papers/'verification.json')['files']:assert sha256(papers/item['file'])==item['sha256']
    for item in read(existing/'verification.json')['files']:assert sha256(existing/item['file'])==item['sha256']
    assert sha256(package/'agmip_download.zip')==read(package/'verification.json')['package_sha256']
    assert sha256(package/'article.json')==read(package/'verification.json')['metadata_sha256']
    for name,digest in read(decoded/'derived_files_sha256.json').items():assert sha256(decoded/name)==digest
    metadata=read(package/'article.json')
    assert metadata['resource_doi']=='10.1016/j.agwat.2011.11.005'
    run=new_run(ROOT,'lirf_calibration_provenance');print(run,flush=True)
    keys=('P1','P2','P5','G2','G3','PHINT')
    row=next(r for r in (decoded/'MZCER045.CUL').read_text(encoding='latin-1').splitlines() if r.startswith('IB1068 '))
    oldrow=next(r for r in (native/'original_MZCER048.CUL').read_text(encoding='latin-1').splitlines() if r.startswith('IB1068 '))
    values=list(map(float,row[36:].split()))
    default=[float(oldrow[36+i*6:42+i*6]) for i in range(6)]
    assert values==[245.6,.156,704.4,994.,6.239,52.88,244.6,43.07]
    vectors=dict(package_045=values[:6],native_default_048=default,
        saseendran2015_table3_greeley=[260.,.60,620.,990.,7.80,40.],
        fang2017_table2_initial=[245.6,.1562,704.4,994.1,6.239,52.89],
        fang2017_table2_final=[262.,.14,570.9,1060.,12.,48.2])
    comparisons=[dict(source=name,coefficients=dict(zip(keys,v)),
        package_minus_source=dict(zip(keys,[a-b for a,b in zip(values,v)])),
        exact_numeric_matches=sum(a==b for a,b in zip(values,v)),
        numerical_similarity_proves_identity_or_calibration_independence=False)
        for name,v in vectors.items() if name!='package_045']
    assert next(c for c in comparisons if c['source']=='fang2017_table2_initial')['exact_numeric_matches']==3
    source_docs=[]
    for path,selection in ((papers/'Ma2012.pdf',[1,2,3,4,5]),(papers/'Fang2017.pdf',[1,2,6,7]),(existing/'Saseendran2015.pdf',[3,4,5,6])):
        pages=PdfReader(path).pages
        source_docs.append(dict(file=str(path.relative_to(ROOT)),sha256=sha256(path),
            pages=[dict(physical_page=i,text=pages[i-1].extract_text()) for i in selection],
            scanned_text_requires_render_qualification=path.name=='Ma2012.pdf'))
    papers_ledger=[
        dict(id='ma2012',doi='10.1016/j.agwat.2011.11.005',package_metadata_relationship='IsSupplementTo',
            physical_page=2,printed_page=142,model='RZWQM2 with DSSAT4.0 crop modules',
            initial_calibration='2008 maximum irrigationT1',
            feedback_exposure='other2008 treatments and2009/2010 were evaluated; parameters recalibrated if responses inadequate',
            further_search='ordered plant-parameter search with field-estimated soil retention',
            untouched_whole_study_validation_established=False,exact_package_coefficients_identified=False),
        dict(id='saseendran2015',doi='10.1016/j.agsy.2014.11.005',model='CERES4.0 crop inRZWQM2',
            calibration='2008 maximum irrigation yield',reported_validation='remaining2008 treatments and all2009-2011 treatments',
            physical_pages=[3,4],results_pool_calibration_and_validation=True,
            whole_study_independent_validation=False,coefficient_vector_equal_to_package=False),
        dict(id='fang2017',doi='10.13031/trans.12405',model='RZWQM with PEST',physical_pages=[6,7],
            experiment_years=[2012,2013],calibration='100/100 and40/40 treatments in both years; growth/yield/water/stages',
            reported_evaluation='other5 treatments; cropN outcomes discussed across treatments',
            initial_parameters_reference='Ma2012/Fang2014 at2008-2011 site and DeJonge2011 local area',
            initial_values_similar_but_not_identical_to_package=True,
            proves_exact_package_lineage=False,same_site_later_years_automatically_independent=False)]
    ace=read(decoded/'decoded_ace.json');scope=read(decoded/'model_package_scope.json')
    csvpath=next((package/'package').rglob('metadata.csv'))
    csvrows=list(csv.reader(csvpath.read_text(encoding='utf-8').splitlines()))
    assert len(ace['experiments'])==scope['experiments']==1 and scope['treatment']=='corn_2008_100ET'
    contract=dict(study_id='usda_lirf2008_2011',planned_role='independent_validation_base_crop_water_response',
        role_status='conditional_candidate_not_qualified',study_split_unit='entireLIRF2008-2011',
        whole_study_holdout_changed=False,calibration_on_LIRF_outcomes_allowed=False,
        exact_package_parameter_lineage_verified=False,parameter_calibration_exposure='unknown_for_exact_package',
        independent_validation_allowed=False,current_use_allowed='source/input diagnostics only',
        same_id_IB1068_proves_cultivar_identity=False,coefficient_similarity_proves_external_calibration=False,
        published_validation_label_is_current_independence_proof=False,
        package_unmapped_trailing_values=values[6:],trailing_values_assigned=False,
        unresolved=['exact package optimization/calibration data and freeze history','DEKALB521 vs field52-59 identity',
            'DSSAT045/RZWQM vs048 agronomic portability','soil/management/initial-state field mapping and uncertainty'],
        requirements_to_restore_candidate_eligibility=['document exact parameter lineage and data exposure',
            'if LIRF outcomes informed parameters, do not label whole study independent validation',
            'freeze source/model settings before eligible external-study comparison',
            'satisfy field input/measurement/endpoint contracts separately'],
        new_independent_studies_added=0,research_ready=False,main_training_allowed=False)
    for name,data in [('coefficient_comparisons',dict(package=dict(zip(keys,values)),native_row=oldrow,package_row=row,comparisons=comparisons)),
        ('publication_data_exposure',papers_ledger),('source_document_pages',source_docs),('validation_role_contract',contract),
        ('package_metadata_scope',dict(resource_doi=metadata['resource_doi'],related_materials=metadata['related_materials'],
            repository_temporal_fields=[f for f in metadata['custom_fields'] if f['name'].startswith('Temporal')],
            actual_payload=scope,metadata_csv_rows=csvrows))]:write_json(run/f'{name}.json',data)
    for name in ('lirf-ma2012-2.png','lirf-fang2017-07.png'):shutil.copy2(ROOT/'outputs'/name,run/name)
    report=dict(passed=True,coefficient_variants_compared=5,coefficients_per_variant=6,
        exact_package_fang_initial_matches=3,publication_exposure_ledgers=3,actual_package_experiments=1,
        package_calibration_lineage_verified=False,whole_study_independence_verified=False,
        validation_role='conditional_candidate_not_qualified',split_changed=False,new_independent_studies=0,
        cultivar_or_native_parameters_replaced=0,new_native_simulations=0,new_training_runs=0,
        research_ready=False,main_training_allowed=False,
        evidence_sha256={str(p.relative_to(ROOT)):sha256(p) for p in (package/'article.json',package/'agmip_download.zip',decoded/'MZCER045.CUL',native/'original_MZCER048.CUL',papers/'verification.json',existing/'verification.json')},
        scope='source numerical comparison and calibration exposure audit; no identity/provenance inference from similarity or validation score')
    write_json(run/'verification.json',report)
    write_json(run/'derived_files_sha256.json',{p.name:sha256(p) for p in run.iterdir() if p.is_file()})
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
