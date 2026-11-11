"""Pin release evidence and independently check a source reconciliation."""
from collections import Counter
from decimal import Decimal, localcontext
import json
from pathlib import Path
import sys
import openpyxl

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256


def main():
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    folder=ROOT/'outputs/runs/20261106T233953Z_nebraska_input_audit_fd40b2ec'
    source=ROOT/'outputs/runs/20261106T232619Z_field_calibration_candidates_9542cf1f/nebraska_Manuscript_data.xlsx'
    paper=ROOT/'outputs/runs/20261106T233714Z_nebraska_paper_384ae31b/Li2023.pdf'
    for name,digest in read(folder/'derived_files_sha256.json').items():assert sha256(folder/name)==digest
    report=read(folder/'verification.json')
    assert sha256(source)==report['source_sha256']['workbook'] and sha256(paper)==report['source_sha256']['paper']
    assert report['endpoint_year_treatment_comparisons']==288 and report['unavailable_grain_slots']==17
    wb=openpyxl.load_workbook(source,read_only=True,data_only=True)
    # Decimal sums/squared deviations independently check the known grain SD conflict.
    vals=[Decimal(str(r[8]))/1000 for r in list(wb['yield_raw'].values)[1:]
          if r[2]==2015 and r[4:7]==('deficit','rye','retention')]
    assert len(vals)==4
    with localcontext() as context:
        context.prec=35
        mean=sum(vals)/len(vals)
        sd=(sum((v-mean)**2 for v in vals)/(len(vals)-1)).sqrt()
    comparisons=read(folder/'raw_summary_comparisons.json')
    conflict=next(r for r in comparisons if (r['endpoint'],r['year'],r['code'])==('grain',2015,'DCN'))
    assert abs(float(mean)-conflict['raw_mean'])<1e-10
    assert abs(float(sd)-conflict['raw_sample_sd'])<1e-10 and conflict['sd_difference_flag']
    assert conflict['reported_sd']==wb['yield_summary']['E8'].value
    assert report['arithmetic_counts']['grain']==dict(comparisons=72,mean_difference_flags=0,sd_difference_flags=9,uncomputable_sd=1)
    precip=read(folder/'precipitation_date_candidates.json')
    assert len(precip)==len({r['date'] for r in precip})==3287
    assert sum(r['method']=='source_header_DD/MM/YYYY' for r in precip)==13
    events=read(folder/'irrigation_repeated_tuple_candidates.json')
    assert len(events)==336 and sum(r['multiplicity'] for r in events)==1344
    assert all(r['multiplicity']==4 and r['amount_mm']==10*r['amount_cm'] and not r['deduplicated_event_qualified'] for r in events)
    dossier=read(folder/'source_input_dossier.json')
    assert len(dossier)==17 and all(r['native_assignment_allowed'] is False for r in dossier)
    wb.close()
    baseline=ROOT/'outputs/runs/20261106T233413Z_field_calibration_screen_release_4284ec69/source_snapshot/configs/agronomic_sources.json'
    current=read(ROOT/'configs/agronomic_sources.json')['studies'];prior=read(baseline)['studies']
    assert {s['id']:s['planned_role'] for s in current}=={s['id']:s['planned_role'] for s in prior}
    assert len(current)==10 and not any(s['quantitative_fit_ready'] for s in current)
    tests=ROOT/'outputs/runs/20261106T234122Z_unit_regressions_5e7244f0/verification.json'
    ready=ROOT/'outputs/runs/20261106T234133Z_readiness_37151f19/readiness.json'
    priority=ROOT/'outputs/runs/20261106T234132Z_agronomic_input_priorities_98dc477c/verification.json'
    t,r=read(tests),read(ready)
    assert t['passed'] and t['tests_run']==204 and not(t['failures'] or t['errors'] or t['skipped'])
    assert r['research_ready'] is False and r['main_training_allowed'] is False and not r['quantitative_fit_ready_studies']
    assert r['agronomic_input_priority_sha256']==sha256(ROOT/'configs/agronomic_input_priorities.json')
    assert read(priority)['roles_changed']==0
    files=[source,paper,folder/'verification.json',folder/'derived_files_sha256.json',tests,ready,priority,
        ROOT/'configs/field_calibration_candidate_screen.json',ROOT/'configs/agronomic_input_priorities.json',
        ROOT/'configs/agronomic_sources.json',ROOT/'docs/NEBRASKA_INPUT_AUDIT.md',ROOT/'docs/FIELD_CALIBRATION_CANDIDATE_SCREEN.md',
        ROOT/'docs/NEXT_STEPS.md',ROOT/'docs/AGRONOMIC_INPUT_PRIORITIES.md',ROOT/'PROGRESS.md',
        ROOT/'scripts/audit_nebraska_inputs.py',ROOT/'scripts/fetch_nebraska_paper.py',Path(__file__)]
    run=new_run(ROOT,'nebraska_input_audit_release')
    write_json(run/'verification.json',dict(passed=True,source_sha256_unchanged=True,
        decimal_source_sd_conflict_verified=True,source_conflicts_resolved=False,
        original_workbook_modified=False,observations_and_roles_unchanged=True,old_workspace_empty=True,
        tests_run=204,active_studies_added=0,native_input_assignments=0,new_native_simulations=0,new_training_runs=0,
        quantitative_fit_ready_studies=0,research_ready=False,main_training_allowed=False,
        evidence_sha256={p.relative_to(ROOT).as_posix():sha256(p) for p in files},
        scope='source audit reproducibility and no-promotion checks, not field-model validation'))
    print(run)


if __name__=='__main__':main()
