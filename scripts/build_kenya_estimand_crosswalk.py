"""Preserve fitted estimands and their own uncertainty; no observation promotion."""
from collections import Counter,defaultdict
import csv
from decimal import Decimal
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256

def main():
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    source=ROOT/'outputs/runs/20261107T011325Z_kenya_public_dataset_f18ec4ef'
    links=ROOT/'outputs/runs/20261107T012059Z_kenya_protocol_sources_72dfbf08'
    retrieval=ROOT/'outputs/runs/20261107T012133Z_kenya_linked_fulltext_e59c8d07'
    acquired=read(source/'verification.json');tables={};source_files={}
    for entry in acquired['files']:
        p=source/entry['local_file'];assert sha256(p)==entry['sha256']
        with p.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
        prefix=entry['filename'][:2];tables[prefix]=rows;source_files[prefix]=entry['local_file']
    base=lambda response:response.removesuffix(' (productive seasons)')
    def key(row):
        return (row.get('Site/context',row.get('Site')),base(row['Response']),row['Season'],row['Sowing treatment'],row['Variety'])
    def contrast_key(row):
        return (row.get('Site/context',row.get('Site')),base(row['Response']),row['Season'],row['Variety'],row['Contrast'])
    primary={key(r):(line,r) for line,r in enumerate(tables['07'],2) if r['Model']!='duma_cross_site_stover'}
    assert len(primary)==189
    comparisons=[]
    for line,r in enumerate(tables['08'],2):
        original_line,p=primary[key(r)]
        deltas={field:str(Decimal(p[field])-Decimal(r[field])) for field in ('Estimated marginal mean','SE','df','Lower 95% CI','Upper 95% CI')}
        comparisons.append(dict(key=key(r),primary_model=p['Model'],primary_response=p['Response'],season_specific_response=r['Response'],
            primary_csv_line=original_line,season_specific_csv_line=line,primary_SE=p['SE'],season_specific_SE=r['SE'],
            primary_df=p['df'],season_specific_df=r['df'],deltas_primary_minus_season_specific=deltas,
            mean_agrees_at_reporting_resolution=abs(Decimal(deltas['Estimated marginal mean']))<=Decimal('0.0000001'),
            SE_differs_at_reporting_resolution=abs(Decimal(deltas['SE']))>Decimal('0.0000001'),
            df_differs=Decimal(p['df'])!=Decimal(r['df']),uncertainties_interchangeable=False))
    primary_contrasts={contrast_key(r):(line,r) for line,r in enumerate(tables['09'],2) if r['Model']!='duma_cross_site_stover'}
    assert len(primary_contrasts)==126
    contrast_comparisons=[]
    for line,r in enumerate(tables['10'],2):
        original_line,p=primary_contrasts[contrast_key(r)]
        delta=Decimal(p['Estimate'])-Decimal(r['Estimate']);se_delta=Decimal(p['SE'])-Decimal(r['SE'])
        contrast_comparisons.append(dict(key=contrast_key(r),primary_csv_line=original_line,season_specific_csv_line=line,
            estimate_delta=str(delta),SE_delta=str(se_delta),primary_SE=p['SE'],season_specific_SE=r['SE'],
            estimates_agree=abs(delta)<=Decimal('0.0000001'),SE_differs=abs(se_delta)>Decimal('0.0000001'),
            SE_may_not_be_replaced_by_independent_EMM_formula=True))
    # Validate contrast orientation against its own fitted mean table, including
    # the separately fitted cross-site model, without deriving contrast SE.
    model_means={(r['Model'],r['Site/context'],r['Response'],r['Season'],r['Sowing treatment'],r['Variety']):r for r in tables['07']}
    orientation=[]
    for line,r in enumerate(tables['09'],2):
        first,second=r['Contrast'].split(' - ')
        def mean(t):return Decimal(model_means[(r['Model'],r['Site/context'],r['Response'],r['Season'],t,r['Variety'])]['Estimated marginal mean'])
        delta=mean(first)-mean(second)-Decimal(r['Estimate'])
        orientation.append(dict(csv_line=line,model=r['Model'],contrast=r['Contrast'],mean_difference_minus_estimate=str(delta),
            orientation_agrees=abs(delta)<=Decimal('0.0000001')))
    failure_contexts=defaultdict(lambda:dict(total=0,failed=0,with_grain=0))
    for r in tables['18']:
        c=failure_contexts[(r['Site'],r['Season'])]
        c['total']+=int(r['Plots']);c['failed']+=int(r['Grain-failure plots']);c['with_grain']+=int(r['Plots with grain'])
    productive_seasons={r['Season'] for r in tables['07'] if r['Model']=='machanga_productive_grain'}
    assert productive_seasons=={'SR09','LR10'}
    coverage=[]
    for (site,season),c in sorted(failure_contexts.items()):
        represented=any(r['Site/context']==site and r['Season']==season and base(r['Response'])=='Corrected grain yield' for r in tables['07'])
        coverage.append(dict(site=site,season=season,**c,represented_in_primary_grain_mean_table=represented,
            response_scope='productive_seasons_only' if site=="Machang'a" else 'five_seasons',
            raw_grain_values_not_reconstructed=True))
    model_scopes=[]
    grouped=defaultdict(list)
    for line,r in enumerate(tables['07'],2):grouped[r['Model']].append((line,r))
    for model,records in sorted(grouped.items()):
        model_scopes.append(dict(model=model,rows=len(records),sites=sorted({r['Site/context'] for _,r in records}),
            responses=sorted({r['Response'] for _,r in records}),seasons=sorted({r['Season'] for _,r in records}),
            varieties_raw=sorted({r['Variety'] for _,r in records}),source_lines=[line for line,_ in records],
            extra_independent_observations=0))
    xml=ET.fromstring((retrieval/'article.xml').read_bytes())
    tags={element.tag.rsplit('}',1)[-1] for element in xml.iter()}
    fulltext_available=bool(tags & {'originalText','body','sections'})
    assert 'coredata' in tags and not fulltext_available
    crossref=read(links/'crossref.json')['message']
    assert crossref['DOI'].lower()=='10.1016/j.eja.2026.128364'
    publisher_entry=next(e for e in read(links/'verification.json')['files'] if e['file']=='publisher.html')
    assert not publisher_entry['acquired'] and '403' in publisher_entry['error']
    run=new_run(ROOT,'kenya_estimand_crosswalk');print(run,flush=True)
    for name,data in [('EMM_primary_vs_season_specific',comparisons),('contrast_primary_vs_season_specific',contrast_comparisons),
        ('contrast_orientation_checks',orientation),('grain_failure_estimand_coverage',coverage),('primary_model_scopes',model_scopes)]:write_json(run/f'{name}.json',data)
    write_json(run/'protocol_linkage.json',dict(article_doi=crossref['DOI'],title=crossref['title'],
        article_PII='S1161030126003837',publisher_indexed_data_availability_url='https://www.sciencedirect.com/science/article/pii/S1161030126003837',
        indexed_dataset_backlink='https://data.mendeley.com/datasets/tdw54wgvbf/1',
        bibliography_link_scope='publisher-indexed Data availability links this dataset; DOI title/authors confirmed from Crossref; not a full protocol retrieval',
        issue_date_as_registered=crossref['published'],license_start_as_registered=crossref.get('license'),
        publisher_HTML_status=403,official_API_HTTP_status=200,official_API_payload='coredata_only',full_protocol_acquired=False,
        fulltext_element_names=sorted(tags),native_inputs_from_article_assigned=0,
        source_sha256={p.name:sha256(p) for p in (links/'crossref.json',links/'datacite.json',retrieval/'article.xml')}))
    excluded=[r for r in coverage if not r['represented_in_primary_grain_mean_table']]
    report=dict(passed=True,scope='fitted-estimand/uncertainty and conditional-season scope audit, not raw crop-model validation',
        matched_EMM_rows=len(comparisons),EMM_mean_review_differences=sum(not r['mean_agrees_at_reporting_resolution'] for r in comparisons),
        EMM_SE_differences=sum(r['SE_differs_at_reporting_resolution'] for r in comparisons),EMM_df_differences=sum(r['df_differs'] for r in comparisons),
        matched_contrast_rows=len(contrast_comparisons),contrast_estimate_review_differences=sum(not r['estimates_agree'] for r in contrast_comparisons),
        contrast_SE_differences=sum(r['SE_differs'] for r in contrast_comparisons),
        oriented_primary_contrasts=len(orientation),contrast_orientation_review_differences=sum(not r['orientation_agrees'] for r in orientation),
        primary_model_scopes=len(model_scopes),cross_site_extra_EMM_rows=30,
        productive_seasons=sorted(productive_seasons),excluded_contexts=len(excluded),
        excluded_context_plot_seasons=sum(r['total'] for r in excluded),excluded_context_failed_plot_seasons=sum(r['failed'] for r in excluded),
        excluded_context_with_grain_plot_seasons=sum(r['with_grain'] for r in excluded),
        article_bibliographic_link_located=True,full_protocol_acquired=False,moisture_correction_basis_verified=False,
        raw_plot_grain_yield_acquired=False,active_studies_added=0,new_native_input_assignments=0,new_native_simulations=0,new_training_runs=0,
        quantitative_fit_ready=False,research_ready=False,main_training_allowed=False,
        next_task='Search official university repository for Ngetich original field protocol/AquaCrop study; verify overlap, input/calibration lineage and grain-correction basis without assuming same experiment')
    write_json(run/'verification.json',report)
    write_json(run/'derived_files_sha256.json',{p.name:sha256(p) for p in run.iterdir() if p.is_file()})
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
