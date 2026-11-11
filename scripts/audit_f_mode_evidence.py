"""Pin F outputs, compare recorded Q/F states, and reject wrong-mode inputs."""
import json
from pathlib import Path
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.multiyear_n import analyze_multiyear_n
from audit_multiyear_n import alter_table


if __name__=='__main__':
    source=ROOT/'outputs/runs/20261106T080958Z_multiyear_f_14b2a9ed'
    qsource=ROOT/'outputs/runs/20261106T073828Z_multiyear_handoff_479f1d6c'
    qprovenance=ROOT/'outputs/runs/20261106T074136Z_multiyear_output_qualification_29bae3c3/verification.json'
    report=json.loads((source/'verification.json').read_text());qindex=json.loads(qprovenance.read_text())
    assert report['passed'] and qindex['passed']
    run=new_run(ROOT,'f_mode_output_qualification');comparisons=[];controls=[];indexes={}
    for case in report['cases']:
        name=case['name']
        for label in ('one_year','two_year'):
            folder=source/name/label;index=folder/'source_files.json'
            for filename,digest in json.loads(index.read_text()).items():assert sha256(folder/filename)==digest
            indexes[name+'/'+label]=sha256(index)
        folder=source/name/'two_year';qfolder=qsource/name/'two_year'
        qp=next(c for c in qindex['complete_new_output_cases'] if c['case']==name and c['label']=='two_year')
        for filename,digest in qp['files'].items():assert sha256(qfolder/filename)==digest
        trace=json.loads((folder/'trace.json').read_text());qtrace=json.loads((qfolder/'trace.json').read_text())
        physical=lambda r:{k:v for k,v in r.items() if not k.startswith('mars_')}
        assert [physical(r) for r in trace]==[physical(r) for r in qtrace]
        assert [r['mars_plant_audit'] for r in trace]==[r['mars_plant_audit'] for r in qtrace]
        comparisons.append({'case':name,'recorded_states':len(trace),'native_non_mars_state_exact':True,
            'recorded_plant_n_audit_exact':True,'compared_native_fields':sorted(physical(trace[0])),
            'q_trace_sha256':sha256(qfolder/'trace.json'),'f_trace_sha256':sha256(folder/'trace.json'),
            'scope':'these recorded state fields and this seed/input only; mode metadata intentionally differs'})
        d=json.loads((folder/'diagnostics.json').read_text());actions=json.loads((folder/'actions.json').read_text())
        for defect in ('year2_initial_no3_plus1','F_data_with_Q_expectation'):
            target=run/'negative_controls'/name/defect;target.mkdir(parents=True)
            for file in ('SoilNoBal.OUT','SoilNiBal.OUT','MgmtEvent.OUT'):shutil.copy2(folder/file,target/file)
            if defect=='year2_initial_no3_plus1':alter_table(target/'SoilNiBal.OUT','NO3',0,1.)
            try:
                result=analyze_multiyear_n(target,d,trace,actions,mode='F' if defect=='year2_initial_no3_plus1' else 'Q')
                rejected=not result['passed'];reason='inventory failed'
            except ValueError as exc:rejected=True;reason=str(exc)
            if not rejected:raise ValueError('F negative control accepted')
            control={'case':name,'defect':defect,'rejected':rejected,'reason':reason,
                'files':{p.name:sha256(p) for p in target.iterdir() if p.is_file()}}
            controls.append(control);write_json(target/'verification.json',control)
    write_json(run/'verification.json',{'passed':True,'scope':'F raw output provenance, recorded Q/F state equivalence and mode/initialization rejection controls',
        'source_F_report_sha256':sha256(source/'verification.json'),'source_Q_report_sha256':sha256(qsource/'verification.json'),
        'source_Q_provenance_sha256':sha256(qprovenance),'F_file_indexes':indexes,
        'comparisons':comparisons,'negative_controls':controls,'new_native_runs':0,
        'whole_elemental_carbon_verified':False,'independent_agronomic_validation':False,'research_ready':False})
    print(run)
