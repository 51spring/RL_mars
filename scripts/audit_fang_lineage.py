"""Bounded chapter lineage findings and evidence-backed non-promotion."""
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,sha256,write_json


class Text(HTMLParser):
    def __init__(self):super().__init__();self.parts=[]
    def handle_data(self,data):self.parts.append(data)


def main():
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    source=ROOT/'outputs/runs/20261106T145526Z_fang_lineage_sources_00e0e4ee'
    prior=ROOT/'outputs/runs/20261106T144720Z_lirf_calibration_provenance_94510be8'
    metadata=read(source/'verification.json');assert metadata['passed']
    for f in metadata['files']:
        if f['acquired']:assert sha256(source/f['file'])==f['sha256']
    assert not next(f for f in metadata['files'] if f['file']=='publisher_landing.html')['acquired']
    for name,digest in read(prior/'derived_files_sha256.json').items():assert sha256(prior/name)==digest
    parser=Text();parser.feed((source/'ARS_record_0.html').read_text(encoding='utf-8'))
    text=' '.join(' '.join(parser.parts).split())
    assert '10.2134/advagricsystmodel5.c1' in text
    assert 'from 2008 to 2011' in text and 'calibrated for corn growth' in text
    start=text.index('Technical Abstract:')
    abstract=text[start:start+2200]
    package=read(prior/'coefficient_comparisons.json')['package'];keys=list(package)
    initial=[245.6,.1562,704.4,994.1,6.239,52.89]
    final=[245.6,.1560,890.,868.1,5.7510,52.88]
    comparisons=[]
    for label,values in [('Zhang2021_table5_initial',initial),('Zhang2021_table5_final',final)]:
        comparisons.append(dict(source=label,coefficients=dict(zip(keys,values)),
            matching_keys=[k for k,v in zip(keys,values) if package[k]==v],
            package_minus_source={k:package[k]-v for k,v in zip(keys,values)},
            exact_full_row_match=all(package[k]==v for k,v in zip(keys,values)),
            inferred_package_origin=False))
    assert all(len(c['matching_keys'])==3 and not c['exact_full_row_match'] for c in comparisons)
    pages=PdfReader(source/'Zhang2021.pdf').pages
    documents=[dict(physical_page=i,text=pages[i-1].extract_text()) for i in (1,2,3,4)]
    assert all(token in documents[-1]['text'] for token in ('0.1562','0.1560','868.1','52.88'))
    role=read(prior/'validation_role_contract.json')
    role.update(dict(exact_package_parameter_lineage_verified=False,independent_validation_allowed=False,
        fang2014_chapter_fulltext_acquired=False,fang2014_ARS_abstract_available=True,
        fang2014_coefficient_vector=None,coefficient_replacement_allowed=False,
        no_cross_table_cherry_picking=True))
    run=new_run(ROOT,'fang_lineage_audit');print(run,flush=True)
    write_json(run/'chapter_evidence_status.json',dict(doi='10.2134/advagricsystmodel5.c1',
        official_record='https://www.ars.usda.gov/research/publications/publication/?seqNo115=308258',
        official_publication_url='http://handle.nal.usda.gov/10113/60869',
        metadata_and_abstract_acquired=True,chapter_fulltext_acquired=False,
        publisher_response='HTTP403',publication_list_response='HTTP404',
        fulltext_access_bypass_attempted=False,coefficient_vector=None,
        calibration_scope_from_official_abstract='Greeley2008-2011 across irrigation treatments',
        exact_treatment_selection_objective_and_freeze_history_verified=False,
        official_abstract_text=abstract))
    write_json(run/'related_coefficient_comparisons.json',dict(package=package,comparisons=comparisons,
        published_site_years=[2012,2013,2015],relation='later same-site study citing Fang2017, not exact package lineage proof',
        measurement_error_50mm_for_0_200cm_not_adopted_for_2008_upper_profile=True))
    write_json(run/'Zhang2021_source_pages.json',documents)
    write_json(run/'validation_role_contract.json',role)
    report=dict(passed=True,study_id='usda_lirf2008_2011',
        chapter_doi_verified=True,chapter_abstract_calibration_years=[2008,2009,2010,2011],
        chapter_fulltext_acquired=False,chapter_coefficient_vector_identified=False,
        related_complete_coefficient_vectors_compared=2,exact_package_row_matches=0,
        package_calibration_lineage_verified=False,whole_study_independence_verified=False,
        independent_validation_allowed=False,study_split_changed=False,new_independent_studies=0,
        original_coefficients_changed=0,new_native_simulations=0,new_training_runs=0,
        research_ready=False,main_training_allowed=False,
        source_reports_sha256={str((p/'verification.json').relative_to(ROOT)):sha256(p/'verification.json') for p in (source,prior)},
        source_files_sha256={str(p.relative_to(ROOT)):sha256(p) for p in (source/'ARS_record_0.html',source/'Zhang2021.pdf')},
        scope='bounded public chapter metadata/abstract and related-table audit; no fulltext/lineage/independence promotion')
    write_json(run/'verification.json',report)
    write_json(run/'derived_files_sha256.json',{p.name:sha256(p) for p in run.iterdir() if p.is_file()})
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
