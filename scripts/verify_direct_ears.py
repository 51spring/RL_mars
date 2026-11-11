"""Direct ear/organ measurements and paired no-change regression."""
import itertools
import json
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.ear_diagnostics import EarProtocol,verify_organ_record
from mars_env.sequence_audit import rounded_balance
from verify_sequence_handoff import run_case
from verify_harvest_n_candidate import crop_trace,crop_output


if __name__=='__main__':
    evidence=ROOT/'outputs/runs/20261106T032225Z_harvest_n_scope_90413cc2/verification.json'
    previous=json.loads(evidence.read_text())
    dates={(c['seed'],c['managed'],c['damage']):c['harvest_date'] for c in previous['c_date_sources']}
    run=new_run(ROOT,'direct_ears');print(run,flush=True);cases=[]
    binaries={'control':'/opt/dssat_pdi/mars_harvest_n_candidate_dscsm048',
              'instrumented':'/opt/dssat_pdi/mars_ear_audit_dscsm048'}
    for seed,managed,damage,mode in itertools.product([123456,456789],[False,True],[0.,.03],['Q','F']):
        name=f'{mode}_{seed}_m{int(managed)}_d{damage}';pair={}
        for label,binary in binaries.items():
            os.environ['MARS_SEQUENCE_BINARY']=binary
            pair[label]=run_case(run/name/label,mode,100,0,damage,seed=seed,managed=managed,
                fallow_start=dates[(seed,managed,damage)],instrumentation=EarProtocol())
        def strip_ears(rows):
            return [{k:v for k,v in r.items() if k not in ('mars_ear_records','mars_barrenness_records')} for r in rows]
        assert strip_ears(crop_trace(run/name/'control'))==strip_ears(crop_trace(run/name/'instrumented'))
        for filename in ('Summary.OUT','PlantGro.OUT','PlantN.OUT'):
            assert crop_output(run/name/'control',filename)==crop_output(run/name/'instrumented',filename)
        d=pair['instrumented'];h=d['harvests'][0]
        assert pair['control']['harvests']==d['harvests'] and pair['control']['soils']==d['soils']
        rows=[r for r in d['ear_records'] if r['date']>=1982057 and 1<=r['stage']<=10]
        assert rows and d['barrenness_records']
        checks=[verify_organ_record(r) for r in rows]
        assert all(c['passed'] for c in checks),name
        final=next(r for r in reversed(rows) if r['dynamic']==6)
        assert int(final['date'])==int(h['date'])
        direct=final['ears']/final['population']
        inferred=h['grain_dm']/h['all_grain_dm']
        ratio_check=rounded_balance(direct,inferred,abs(direct)+abs(inferred))
        assert ratio_check['passed']
        first=next((r for r in rows if r['stage'] in (5,6) and r['ears']>0 and
            not rounded_balance(r['ears'],r['population'],r['ears']+r['population'])['passed']),None)
        for b in d['barrenness_records']:
            assert b['population']<=12,'High-density branch not covered by this diagnostic'
            expected=b['population']*(b['gpp']/(b['g2']*.15))**.33 if b['gpp']<b['g2']*.15 else b['population']
            assert rounded_balance(b['ears'],expected,b['ears']+expected)['passed']
        cases.append({'name':name,'seed':seed,'managed':managed,'damage':damage,'mode':mode,
            'output_records_checked':len(rows),'barrenness_records':d['barrenness_records'],
            'first_post_barrenness_divergence':first,'final_direct':final,'direct_inferred_ratio':ratio_check,
            'existing_crop_trace_and_outputs_exact':True,'soil_handoff_exact':True})
        write_json(run/'partial_results.json',cases);print(name+' direct measurements passed',flush=True)
    write_json(run/'verification.json',{'passed':True,'pairs':len(cases),'native_runs':len(cases)*2,'cases':cases,
        'date_evidence_sha256':sha256(evidence),'binary_sha256':{k:sha256(v) for k,v in binaries.items()},
        'instrumentation_only':True,'crop_equations_changed':False,'default_runtime_changed':False,
        'scope':'direct ear and organ basis confirmation, not corrected physical closure',
        'whole_ecosystem_balance_verified':False,'research_ready':False})
