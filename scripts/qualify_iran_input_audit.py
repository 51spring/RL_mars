"""Independent decimal/source checks and immutable release evidence."""
from collections import defaultdict
from decimal import Decimal,localcontext
from datetime import date
import json
from pathlib import Path
import sys
import openpyxl
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256

def main():
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    acquired=ROOT/'outputs/runs/20261106T235323Z_iran_public_dataset_d683006d'
    folder=ROOT/'outputs/runs/20261106T235624Z_iran_input_audit_d9e85922'
    source=acquired/read(acquired/'verification.json')['files'][0]['local_file']
    report=read(folder/'verification.json')
    assert sha256(source)==report['source_sha256']
    for name,digest in read(folder/'derived_files_sha256.json').items():assert sha256(folder/name)==digest
    w=openpyxl.load_workbook(source,read_only=True,data_only=True)
    groups=defaultdict(list)
    records=read(folder/'harvest_source_records.json')
    for r in records:
        original=w['harvest'][r['grain_cell']].value
        assert original==r['grain_dry_kg_ha']
        assert r['N0_alias_qualified'] is False
        groups[(r['year'],r['irrigation_method'],r['nitrogen_label_raw'])].append(Decimal(str(original)))
    assert len(records)==36 and len(groups)==12
    for r in read(folder/'grain_group_statistics.json'):
        v=groups[(r['year'],r['irrigation_method'],r['nitrogen_label_raw'])]
        assert len(v)==3
        with localcontext() as c:
            c.prec=40;mean=sum(v)/3;sd=(sum((x-mean)**2 for x in v)/2).sqrt()
        assert abs(float(mean)-r['grain_mean_kg_ha'])<1e-9
        assert abs(float(sd)-r['grain_sample_sd_kg_ha'])<1e-9
    for r in read(folder/'irrigation_amount_reconciliation.json'):
        s=w[f"Gross irrigation depth ({r['year']})"]
        column=9 if r['method']=='M1' else 10
        amounts=[Decimal(str(row[column-1].value)) for row in list(s)[3:]
            if isinstance(row[6].value,(int,float)) and isinstance(row[column-1].value,(int,float))]
        assert abs(float(sum(amounts))-r['event_sum_mm'])<1e-8
        assert r['total_amount_agreement'] and r['event_dates_qualified'] is False
    calendars=read(folder/'irrigation_calendar_audit.json')
    assert calendars[0]['missing_calendar_days']==['2014-10-31']
    assert calendars[0]['weekday_mismatches']==13 and calendars[1]['weekday_mismatches']==29
    # Pin source cells at both boundaries rather than silently fixing the calendar.
    assert w['Gross irrigation depth (2014)']['G112'].value==30
    assert w['Gross irrigation depth (2014)']['G113'].value==1
    assert w['Gross irrigation depth (2014)']['F113'].value=='November'
    assert date(2014,11,1).strftime('%A')!=w['Gross irrigation depth (2014)']['E113'].value
    assert w['Gross irrigation depth (2015)']['G111'].value==18
    assert date(2015,10,18).strftime('%A')!=w['Gross irrigation depth (2015)']['E111'].value
    w.close()
    baseline=ROOT/'outputs/runs/20261106T234905Z_nebraska_reference_access_release_3ab3c222/source_snapshot'
    production=list((ROOT/'src').rglob('*.py'))
    assert all(sha256(p)==sha256(baseline/p.relative_to(ROOT)) for p in production)
    assert sha256(ROOT/'configs/agronomic_sources.json')==sha256(baseline/'configs/agronomic_sources.json')
    ready=ROOT/'outputs/runs/20261106T235800Z_readiness_5c48cbfa/readiness.json'
    priority=ROOT/'outputs/runs/20261106T235759Z_agronomic_input_priorities_362e5889/verification.json'
    r=read(ready)
    assert r['public_studies']==10 and not r['quantitative_fit_ready_studies']
    assert r['research_ready'] is False and r['main_training_allowed'] is False
    assert r['agronomic_input_priority_sha256']==sha256(ROOT/'configs/agronomic_input_priorities.json')
    files=[source,acquired/'verification.json',folder/'verification.json',folder/'derived_files_sha256.json',ready,priority,
        ROOT/'configs/agronomic_sources.json',ROOT/'configs/agronomic_input_priorities.json',ROOT/'configs/field_calibration_candidate_screen.json',
        ROOT/'scripts/fetch_iran_public_dataset.py',ROOT/'scripts/audit_iran_public_dataset.py',Path(__file__),
        ROOT/'docs/IRAN_WATER_N_INPUT_AUDIT.md',ROOT/'docs/NEXT_STEPS.md',ROOT/'docs/AGRONOMIC_INPUT_PRIORITIES.md',
        ROOT/'docs/FIELD_CALIBRATION_CANDIDATE_SCREEN.md',ROOT/'PROGRESS.md']
    run=new_run(ROOT,'iran_input_audit_release')
    write_json(run/'verification.json',dict(passed=True,scope='raw-source/decimal arithmetic and calendar conflict audit; not agronomic fit',
        repository_sha256_unchanged=True,decimal_grain_groups_checked=12,decimal_irrigation_totals_checked=4,
        calendar_conflicts_source_cells_verified=True,source_dates_corrected=False,
        production_python_files_unchanged=len(production),active_registry_unchanged=True,old_workspace_empty=True,
        new_tests_run=0,previous_tests_passed=204,new_native_simulations=0,new_training_runs=0,
        quantitative_fit_ready_studies=0,research_ready=False,main_training_allowed=False,
        evidence_sha256={p.relative_to(ROOT).as_posix():sha256(p) for p in files}))
    print(run)

if __name__=='__main__':main()
