"""Read-only public candidate screen; candidate admission is not fit readiness."""
from collections import Counter,defaultdict
from datetime import datetime
import hashlib
import json
from pathlib import Path
import statistics
import sys
import openpyxl
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256


def main():
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    source=ROOT/'outputs/runs/20261106T232619Z_field_calibration_candidates_9542cf1f'
    metadata=read(source/'verification.json');assert metadata['passed']
    for item in metadata['files']:
        if item['acquired']:assert sha256(source/item['file'])==item['sha256']
    article=read(source/'nebraska_article.json')
    entry=next(f for f in article['files'] if f['id']==67135049)
    workbook=source/'nebraska_Manuscript_data.xlsx'
    assert workbook.stat().st_size==entry['size']
    assert hashlib.md5(workbook.read_bytes()).hexdigest()==entry['computed_md5']
    w=openpyxl.load_workbook(workbook,read_only=True,data_only=True)
    f=openpyxl.load_workbook(workbook,read_only=True,data_only=False)
    expected=['yield_raw','yield_summary','N2O_raw','N2O_summary','metadata','precipitation','irrigation']
    assert w.sheetnames==expected
    run=new_run(ROOT,'field_calibration_screen');print(run,flush=True)
    inventory=[]
    for name in expected:
        ws=w[name]
        inventory.append(dict(sheet=name,rows=ws.max_row,columns=ws.max_column,
            headings=[dict(cell=c.coordinate,value=c.value) for c in next(iter(ws)) if c.value is not None],
            state=ws.sheet_state,formula_count=sum(c.data_type=='f' for row in f[name] for c in row)))
    groups=defaultdict(list);identities=set();records=[]
    for row in list(w['yield_raw'])[1:]:
        assert len(row)==12 and isinstance(row[8].value,(float,int))
        key=(str(row[0].value),int(row[2].value));assert key not in identities;identities.add(key)
        assert isinstance(row[1].value,datetime)
        record=dict(unit_id=str(row[0].value),date=row[1].value.date().isoformat(),year=int(row[2].value),
            treatment=row[3].value,irrigation=row[4].value,cover_crop=row[5].value,stover=row[6].value,
            grain_dry_matter_kg_ha=row[8].value,source_row=row[0].row,source_cell=row[8].coordinate,
            experimental_unit_role_unverified=True)
        records.append(record);groups[(record['year'],record['treatment'])].append(record)
    summaries=[]
    for (year,treatment),rows in sorted(groups.items()):
        vals=[r['grain_dry_matter_kg_ha'] for r in rows]
        summaries.append(dict(year=year,treatment=treatment,n=len(rows),mean_kg_ha=statistics.fmean(vals),
            sample_sd_kg_ha=statistics.stdev(vals) if len(vals)>1 else None,
            unit_ids=[r['unit_id'] for r in rows],source_cells=[r['source_cell'] for r in rows],
            source_grouping_only=True,model_uncertainty_threshold_selected=False))
    assert len(records)==271 and len(groups)==72
    # Profile original types/missing tokens, without turning blank irrigation into zero.
    tables={}
    for name,value_index in [('precipitation',1),('irrigation',2)]:
        rows=list(w[name])[1:]
        tables[name]=dict(rows=len(rows),date_type_counts=dict(Counter(type(r[0].value).__name__ for r in rows)),
            missing_or_nonnumeric_amounts=sum(not isinstance(r[value_index].value,(float,int)) for r in rows),
            missing_tokens=dict(Counter(str(r[value_index].value) for r in rows if not isinstance(r[value_index].value,(float,int)))),
            missing_zero_equivalence_established=False,date_parsing_applied=False)
    snapshots=[]
    for candidate,name in [('waterN2014_2015','waterN_mendeley.html'),('kenya2009_2011','kenya_mendeley.html')]:
        text=(source/name).read_text(encoding='utf-8');marker='window.INITIAL_STATE = '
        state,_=json.JSONDecoder().raw_decode(text[text.index(marker)+len(marker):])
        snapshot=state['dataset']['snapshot']
        assert snapshot['is_confidential'] is False and snapshot['is_metadata_only'] is False
        snapshots.append(dict(candidate_id=candidate,snapshot=snapshot,
            file_list_state=state['files'],file_payload_acquired=False,
            empty_loading_list_is_not_evidence_of_no_files=True))
    candidates=[
        dict(id='nebraska_residue2010_2018',doi='10.15482/USDA.ADC/33116162.v1',
            source_article_doi='10.1016/j.eja.2023.126807',candidate_role='base_crop_water_n_calibration_candidate',
            decision='advance_to_input_qualification',evidence='actual7sheetXLSX;271drygrain rows/72year-treatment groups;precipitation and irrigation tables',
            scope='postharvest stover/cover-crop/irrigation experiment, not live defoliation',
            blockers=['complete daily TMAX/TMIN/SRAD not in acquired workbook','full soil/initial state and cultivar/input calibration exposure unqualified',
                'planting/fertilizer schedules not qualified; do not infer N rates from treatment codes',
                'irrigation blanks/date types and raw-versus-summary uncertainty need qualification',
                'unit IDs/block/repeated-year design and dry-weight method need source confirmation']),
        dict(id='waterN2014_2015',doi='10.17632/6zj7pzftwg.1',candidate_role='base_crop_water_n_calibration_candidate',
            decision='pending_public_file_inventory',evidence='public version1 metadata describes2irrigation methods xN0/150/300 and3blocks over2years',
            scope='no assigned leaf damage identified in checked metadata',
            blockers=['file payload not acquired; file-list loader is pending','dry-grain basis/uncertainty/full daily inputs/cultivar exposure unqualified']),
        dict(id='kenya2009_2011',doi='10.17632/tdw54wgvbf.1',candidate_role='base_crop_phenology_water_calibration_candidate',
            decision='pending_public_file_inventory',evidence='public version1 metadata describes5seasons/same physical plots,dates,contrasts and covariance analyses',
            scope='rainfed sowing comparison, not assigned leaf damage',
            blockers=['file payload not acquired; no raw-versus-derived result qualification','dry-grain basis/full weather and soil/cultivar inputs/exposure unqualified',
                'same plots across seasons require dependence preservation']),
        dict(id='lirf_extension2008_2024',doi='10.2139/ssrn.7552188',candidate_role='existing_LIRF_availability_followup_only',
            decision='overlap_followup_not_new_calibration_study',evidence='new author-record title/abstract discovered in public search; direct source fetch403',
            scope='overlaps existingheldoutLIRF2008-2011; no new independent count',
            blockers=['preprint/full dataset payload and public consolidated data URL not acquired',
                'raw measurement availability claims not verified from files','existing independence/parameter-lineage gate still applies'])]
    for c in candidates:c.update(quantitative_fit_ready=False,native_execution_allowed=False,independent_study_count_increment=0)
    for name,data in [('workbook_inventory',inventory),('nebraska_grain_source_records',records),
        ('nebraska_group_statistics',summaries),('nebraska_daily_table_profiles',tables),('mendeley_metadata_snapshots',snapshots),('candidate_decisions',candidates)]:write_json(run/f'{name}.json',data)
    write_json(run/'source_metadata_notes.json',dict(workbook_metadata=[dict(row=i,text=row[0].value) for i,row in enumerate(w['metadata'],1) if row[0].value is not None],
        stover_removal_not_live_leaf_damage=True,missing_data_not_zero=True,new_candidates_not_added_to_active_study_registry=True,
        previous_LIRF_absence_statements_scoped_to_older_checked_resources=True,new_LIRF_lead_requires_followup=True))
    report=dict(passed=True,candidates_screened=4,new_external_candidates=3,existing_study_overlap_leads=1,
        advanced_to_input_qualification=1,active_studies_added=0,actual_workbooks_acquired=1,
        actual_grain_rows=271,year_treatment_groups=72,group_size_histogram=dict(Counter(len(v) for v in groups.values())),
        workbook_source_sha256=sha256(workbook),workbook_md5_matches_repository=True,
        source_acquisition_report_sha256=sha256(source/'verification.json'),
        no_live_damage_calibration_dataset_qualified=True,quantitative_fit_ready_candidates=0,
        roles_changed=False,new_native_simulations=0,new_training_runs=0,research_ready=False,main_training_allowed=False,
        scope='candidate screening from primary metadata and read-only workbook values; one candidate for further input qualification, no fitting or scoring')
    write_json(run/'verification.json',report)
    write_json(run/'derived_files_sha256.json',{p.name:sha256(p) for p in run.iterdir() if p.is_file()})
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
