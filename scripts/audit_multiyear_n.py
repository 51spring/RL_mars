"""Audit archived complete two-year outputs and deliberate negative controls."""
import copy
import json
from pathlib import Path
import re
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.multiyear_n import analyze_multiyear_n


def alter_table(path,column,das,increment):
    lines=path.read_text().splitlines();run=None;header=None;changed=0
    for i,line in enumerate(lines):
        m=re.match(r'^\*RUN\s+(\d+)',line)
        if m:run=int(m[1])
        if line.startswith('@YEAR'):header=line[1:].split()
        elif run==3 and header and re.match(r'^\s*\d{4}\s+\d{3}\s',line):
            spans=list(re.finditer(r'\S+',line));tokens=[m.group() for m in spans]
            if int(tokens[header.index('DAS')])==das:
                token=spans[header.index(column)];value=f'{float(token.group())+increment:.3f}'
                lines[i]=line[:token.start()]+value.rjust(token.end()-token.start())+line[token.end():];changed+=1
    if changed!=1:raise ValueError('Expected one negative-control row')
    path.write_text('\n'.join(lines)+'\n')


if __name__=='__main__':
    source=ROOT/'outputs/runs/20261106T073828Z_multiyear_handoff_479f1d6c'
    provenance=ROOT/'outputs/runs/20261106T074136Z_multiyear_output_qualification_29bae3c3/verification.json'
    native=json.loads((source/'verification.json').read_text());qualified=json.loads(provenance.read_text())
    assert native['passed'] and qualified['passed']
    run=new_run(ROOT,'multiyear_integrated_n');print(run,flush=True);cases=[];controls=[]
    try:
        for case in native['cases']:
            name=case['name'];folder=source/name/'two_year'
            pinned=next(c for c in qualified['complete_new_output_cases'] if c['case']==name and c['label']=='two_year')
            for filename,digest in pinned['files'].items():assert sha256(folder/filename)==digest
            d=json.loads((folder/'diagnostics.json').read_text());trace=json.loads((folder/'trace.json').read_text())
            actions=json.loads((folder/'actions.json').read_text())
            result=analyze_multiyear_n(folder,d,trace,actions)
            write_json(run/(name+'.json'),result)
            cases.append(dict(name=name,**{k:v for k,v in result.items() if k!='rows'}))
            print(name+' inventory='+str(result['passed']),flush=True)
            for defect in ('second_crop_initial_no3','missing_second_crop_fertilizer','second_crop_uptake_lag','missing_first_crop_seed_credit'):
                target=run/'negative_controls'/name/defect;target.mkdir(parents=True)
                for filename in ('SoilNoBal.OUT','SoilNiBal.OUT','MgmtEvent.OUT'):shutil.copy2(folder/filename,target/filename)
                changed_actions=copy.deepcopy(actions)
                changed_trace=trace
                if defect=='second_crop_initial_no3':alter_table(target/'SoilNiBal.OUT','NO3',0,1.)
                elif defect=='second_crop_uptake_lag':alter_table(target/'SoilNiBal.OUT','RNUP',1,.1)
                elif defect=='missing_second_crop_fertilizer':
                    event=next(a for a in changed_actions if a['run']==3 and a['nitrogen_kg_ha']>0)
                    event['nitrogen_kg_ha']=0
                else:
                    changed_trace=copy.deepcopy(trace)
                    harvest_date=int(next(h for h in d['harvests'] if h['run']==1)['date'])
                    index=next(i for i,a in enumerate(actions) if a['run']==1 and a['date']==harvest_date)
                    changed_trace[index+1]['mars_plant_audit']['seed_n']=0.
                    write_json(target/'trace.json',changed_trace)
                write_json(target/'actions.json',changed_actions)
                try:
                    bad=analyze_multiyear_n(target,d,changed_trace,changed_actions)
                    rejected=not bad['passed'];reason='daily inventory failed' if rejected else 'unexpectedly accepted'
                except ValueError as exc:rejected=True;reason=str(exc)
                control={'case':name,'defect':defect,'rejected':rejected,'reason':reason,
                    'mutated_files_sha256':{p.name:sha256(p) for p in target.iterdir() if p.is_file()}}
                controls.append(control);write_json(target/'verification.json',control)
                if not rejected:raise ValueError('Negative control unexpectedly accepted')
        passed=all(c['passed'] for c in cases) and all(c['rejected'] for c in controls)
        write_json(run/'verification.json',{'passed':passed,'cases':cases,'negative_controls':controls,
            'scope':'two-year Q-mode cumulative modeled N and initialization boundaries for two fixed harvest allocations',
            'source_native_report':source.relative_to(ROOT).as_posix()+'/verification.json',
            'source_native_report_sha256':sha256(source/'verification.json'),
            'source_native_manifest_sha256':sha256(source/'manifest.json'),'source_provenance_sha256':sha256(provenance),
            'source_native_image_id':json.loads((source/'manifest.json').read_text())['image_id'],
            'new_native_runs':0,'multiyear_modeled_n_verified_in_tested_scope':passed,
            'byproduct_n_is_defined_allocation':True,'initial_offset_inferred':False,'residual_offsets_fitted':False,
            'whole_elemental_carbon_verified':False,'independent_agronomic_validation':False,'research_ready':False})
        if not passed:raise SystemExit(1)
    except Exception as exc:
        write_json(run/'failure.json',{'passed':False,'exception':repr(exc),'completed_cases':cases,'research_ready':False})
        raise
