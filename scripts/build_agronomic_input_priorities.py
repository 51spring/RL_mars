"""Synthesize checked evidence, keeping priority distinct from scientific eligibility."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.validation_lineage import independent_lineage_status
from mars_env.agronomic_scenarios import build_registry,source_contrasts


def main():
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    registry=read(ROOT/'configs/agronomic_sources.json')
    plan=read(ROOT/'configs/agronomic_input_priorities.json')
    protocols=read(ROOT/'configs/agronomic_protocols.json')['studies']
    source={s['id']:s for s in registry['studies']}
    assert len(source)==len(plan['studies'])==10
    assert {s['id'] for s in plan['studies']}==set(source)
    assert len({s['id'] for s in plan['studies']})==10
    assert plan['role_changes']==0 and not plan['research_ready'] and not plan['main_training_allowed']
    assert [q['order'] for q in plan['work_queue']]==list(range(1,6))
    assert {s for q in plan['work_queue'] for s in q['studies']}==set(source)
    assert all(q['quantitative_execution_allowed'] is False for q in plan['work_queue'])
    rows=[];evidence={}
    for entry in plan['studies']:
        s=source[entry['id']]
        assert s['quantitative_fit_ready'] is False
        assert len(entry['states'])==len(plan['dimensions'])==8
        assert all(v in plan['states'] for v in entry['states'])
        assert not all(v in ('verified','out_of_scope') for v in entry['states'])
        for ref in entry['local_refs']:
            assert (ROOT/ref).is_file(),ref;evidence[ref]=sha256(ROOT/ref)
        if s['id'] in protocols:assert protocols[s['id']]['role']==s['planned_role']
        for field in ('source_run','evidence','calibration_provenance_audit','measurement_data_availability'):
            ref=s.get(field)
            if ref and (ROOT/ref).exists():
                path=ROOT/ref
                if path.is_dir():path=path/'verification.json'
                if path.is_file():evidence[path.relative_to(ROOT).as_posix()]=sha256(path)
        lineage=independent_lineage_status(ROOT,s)
        rows.append(dict(study_id=s['id'],doi=s['doi'],planned_role=s['planned_role'],
            role_unchanged=True,states=dict(zip(plan['dimensions'],entry['states'])),
            current_use=entry['current_use'],blocker=entry['main_blocker'],next_action=entry['next_action'],
            lineage=lineage,source_access_as_previously_checked=s.get('access'),
            newly_retried_access=False,quantitative_fit_ready=False,model_scoring_allowed=False))
    assert sum(r['lineage']['required'] for r in rows)==6
    assert all(r['lineage']['parameter_lineage_eligible'] is False for r in rows if r['lineage']['required'])
    run=new_run(ROOT,'agronomic_input_priorities');print(run,flush=True)
    write_json(run/'study_input_matrix.json',rows)
    write_json(run/'work_queue.json',plan['work_queue'])
    write_json(run/'new_calibration_screen.json',plan['new_field_calibration_screen'])
    write_json(run/'source_evidence_sha256.json',evidence)
    header=['study','planned_role',*plan['dimensions'],'current_use','next_action']
    table=['| '+' | '.join(header)+' |','| '+' | '.join(['---']*len(header))+' |']
    for row in rows:table.append('| '+' | '.join(str(v).replace('|','/') for v in [row['study_id'],row['planned_role'],*row['states'].values(),row['current_use'],row['next_action']])+' |')
    (run/'study_input_matrix.md').write_text('\n'.join(table)+'\n',encoding='utf-8')
    scenarios=build_registry(ROOT);contrasts=source_contrasts(scenarios)
    assert len(scenarios)==28 and len(contrasts)==16
    report=dict(passed=True,studies=10,dimensions_per_study=8,work_items=5,
        independent_role_lineage_checks=6,independent_role_lineage_qualified=0,
        registered_damage_scenarios=len(scenarios),source_damage_contrasts=len(contrasts),
        other_observations_separate='Rahman9marginals and LIRF96plot_yields/24summaries, not extra independent studies',
        roles_changed=0,states_are_not_validation_scores=True,access_retries=0,new_sources_acquired=0,
        quantitative_fit_ready_studies=0,new_native_simulations=0,new_training_runs=0,
        research_ready=False,main_training_allowed=False,
        config_sha256={p:sha256(ROOT/p) for p in ('configs/agronomic_sources.json','configs/agronomic_protocols.json','configs/agronomic_input_priorities.json')},
        source_evidence_items=len(evidence),
        scope='existing-evidence synthesis and task ordering, not new source access or model/field validation')
    write_json(run/'verification.json',report)
    write_json(run/'derived_files_sha256.json',{p.name:sha256(p) for p in run.iterdir() if p.is_file()})
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
