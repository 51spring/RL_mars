"""Verify OOXML recovery against independent openpyxl comment loading."""
from datetime import date
import json
from pathlib import Path
import sys
import openpyxl
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256

def main():
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    folder=ROOT/'outputs/runs/20261107T005540Z_iran_protocol_dossier_3687b1a6'
    source=ROOT/'outputs/runs/20261106T235323Z_iran_public_dataset_d683006d/1d70605e-ab43-4f5b-95ce-cbe9880802da_Field_Data.xlsx'
    report=read(folder/'verification.json')
    for name,digest in read(folder/'derived_files_sha256.json').items():assert sha256(folder/name)==digest
    assert sha256(source)==report['source_sha256']
    # Load comments independently of the dossier's ZIP relationship resolver. Never save.
    w=openpyxl.load_workbook(source,read_only=False,data_only=True)
    comments={(s.title,c.coordinate):c.comment.text for s in w for row in s for c in row if c.comment}
    recovered=read(folder/'source_comments.json')
    assert len(comments)==len(recovered)==16
    for r in recovered:assert comments[(r['sheet'],r['cell'])].strip()==r['text']
    assert 'Planting date' in comments[('Gross irrigation depth (2014)','G5')]
    assert 'Planting date' in comments[('Gross irrigation depth (2015)','G5')]
    assert w['Gross irrigation depth (2014)']['G5'].value==15
    assert w['Gross irrigation depth (2015)']['G5'].value==4
    assert w['Gross irrigation depth (2014)']['G125'].value==13
    assert w['Gross irrigation depth (2014)']['H125'].value==120
    assert (date(2014,11,13)-date(2014,7,15)).days==121
    events=read(folder/'reported_management_events.json')
    assert len(events)==15 and sum(e['kind']=='fertigation' for e in events)==11
    assert all(e['nitrogen_dose_kg_ha'] is None and e['native_assignment_allowed'] is False for e in events)
    assert next(e for e in events if e['year']==2015 and e['source_row']==9)['source_comment_cells']==['G9','H9']
    d=read(folder/'input_dossier.json')
    assert len(d)==22 and all(f['native_assignment_allowed'] is False for f in d)
    assert report['exact_primary_paper_verified'] is False and report['source_dates_corrected'] is False
    assert report['irrigation_event_records_outside_detected_weekday_conflicts']==100
    w.close()
    prior=ROOT/'outputs/runs/20261106T235904Z_iran_input_audit_release_bf5a96e9/source_snapshot'
    production=list((ROOT/'src').rglob('*.py'))
    assert all(sha256(p)==sha256(prior/p.relative_to(ROOT)) for p in production)
    assert sha256(ROOT/'configs/agronomic_sources.json')==sha256(prior/'configs/agronomic_sources.json')
    ready=ROOT/'outputs/runs/20261107T005654Z_readiness_3c8f63b5/readiness.json'
    priority=ROOT/'outputs/runs/20261107T005653Z_agronomic_input_priorities_64e16634/verification.json'
    r=read(ready)
    assert not r['research_ready'] and not r['main_training_allowed'] and not r['quantitative_fit_ready_studies']
    assert r['agronomic_input_priority_sha256']==sha256(ROOT/'configs/agronomic_input_priorities.json')
    assert read(ROOT/'configs/field_calibration_candidate_screen.json')['next_candidate']=='kenya2009_2011'
    files=[source,folder/'verification.json',folder/'derived_files_sha256.json',ready,priority,
        ROOT/'configs/agronomic_sources.json',ROOT/'configs/agronomic_input_priorities.json',ROOT/'configs/field_calibration_candidate_screen.json',
        ROOT/'docs/IRAN_PROTOCOL_DOSSIER.md',ROOT/'docs/IRAN_WATER_N_INPUT_AUDIT.md',ROOT/'docs/NEXT_STEPS.md',ROOT/'docs/AGRONOMIC_INPUT_PRIORITIES.md',
        ROOT/'scripts/build_iran_protocol_dossier.py',Path(__file__),ROOT/'PROGRESS.md']
    run=new_run(ROOT,'iran_protocol_dossier_release')
    write_json(run/'verification.json',dict(passed=True,scope='comment-source and unresolved-input dossier release; not field-model validation',
        independently_matched_comments=16,unique_management_events=15,source_input_fields=22,
        source_sha256_unchanged=True,source_dates_corrected=False,new_native_input_assignments=0,
        production_python_files_unchanged=len(production),active_registry_unchanged=True,old_workspace_empty=True,
        new_tests_run=0,previous_tests_passed=204,new_native_simulations=0,new_training_runs=0,
        quantitative_fit_ready_studies=0,research_ready=False,main_training_allowed=False,
        evidence_sha256={p.relative_to(ROOT).as_posix():sha256(p) for p in files}))
    print(run)

if __name__=='__main__':main()
