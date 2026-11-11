"""Broaden the experimental candidate; retain every failed physical boundary."""
import itertools
import json
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.harvest_scope import actual_export_boundary
from mars_env.sequence_audit import analyze_handoff
from mars_env.harvest_accounting import harvest_summary
from verify_sequence_handoff import run_case
from verify_c_harvest_accounting import run_case as run_c
from verify_harvest_n_candidate import BINARIES,crop_trace,crop_output,independent_n


if __name__=='__main__':
    run=new_run(ROOT,'harvest_n_scope');print(run,flush=True)
    dates={};c_sources=[];cases=[]
    for seed,managed,damage in itertools.product([123456,456789],[False,True],[0.,.03]):
        name=f'C_seed{seed}_m{int(managed)}_d{damage}'
        result=run_c(run/name,seed,managed,damage,100,0)
        date=int(result['harvest']['date']);dates[(seed,managed,damage)]=date
        c_sources.append({'seed':seed,'managed':managed,'damage':damage,'harvest_date':date,
                          'source':name+'/diagnostics.json'})
        print(name+' date measured',flush=True)
    for seed,managed,damage,mode,grain,stover in itertools.product(
            [123456,456789],[False,True],[0.,.03],['Q','F'],[100,50],[0,100]):
        name=f'{mode}_seed{seed}_m{int(managed)}_d{damage}_g{grain}_s{stover}'
        pair={}
        for label,binary in BINARIES.items():
            os.environ['MARS_SEQUENCE_BINARY']=binary
            folder=run/name/label
            result=run_case(folder,mode,grain,stover,damage,seed=seed,managed=managed,
                            fallow_start=dates[(seed,managed,damage)])
            h=result['harvests'][0]
            assert int(h['date'])==dates[(seed,managed,damage)]
            assert abs(h['grain_fraction']-grain/100)<=2**-24 and abs(h['stover_fraction']-stover/100)<=2**-24
            result['handoff']=analyze_handoff(result)
            result['independent_n']=independent_n(folder,result)
            result['export_scope']=actual_export_boundary(h)
            # Exactly one maize Summary row: fallow changes are outside this check.
            summary_text=(folder/'Summary.OUT').read_text()
            header=next(l for l in summary_text.splitlines() if l.startswith('@') and 'HWAH' in l)
            crop_row=crop_output(folder,'Summary.OUT')
            assert len(crop_row)==1
            output=harvest_summary(header+'\n'+crop_row[0])
            by_dm=result['export_scope']['byproduct_dm_kg_ha']
            assert abs(output['BWAH']-by_dm)<=.5+2**-20*abs(by_dm)
            assert result['handoff']['handoff_passed']
            # Scope failures are data, not reasons to discard or relabel runs.
            write_json(folder/'scope_diagnostics.json',result)
            for filename,digest in result['files'].items():assert sha256(folder/filename)==digest
            pair[label]=result
        assert crop_trace(run/name/'native')==crop_trace(run/name/'candidate')
        for filename in ('Summary.OUT','PlantGro.OUT','PlantN.OUT'):
            assert crop_output(run/name/'native',filename)==crop_output(run/name/'candidate',filename)
        cases.append({'name':name,'seed':seed,'managed':managed,'damage':damage,'mode':mode,
            'grain_percent':grain,'stover_percent':stover,
            'native_export':pair['native']['export_scope'],
            'candidate_export':pair['candidate']['export_scope'],
            'candidate_population_partition_passed':pair['candidate']['handoff']['partition_passed'],
            'first_crop_exact':True,'fallow_date_from_observed_crop':dates[(seed,managed,damage)]})
        write_json(run/'partial_results.json',cases)
        print(name+' audited; qualified='+str(cases[-1]['candidate_export']['scope_qualified']),flush=True)
    qualified=sum(c['candidate_export']['scope_qualified'] for c in cases)
    write_json(run/'verification.json',{'passed':True,
        'scope':'broadened diagnostics; all scope failures retained, no default promotion',
        'qf_pairs':len(cases),'c_date_sources':c_sources,'native_runs':2*len(cases)+len(c_sources),
        'qualified_cases':qualified,'unqualified_cases':len(cases)-qualified,'cases':cases,
        'binary_sha256':{k:sha256(v) for k,v in BINARIES.items()},
        'candidate_broadly_validated':qualified==len(cases),'default_runtime_changed':False,
        'whole_postharvest_system_balance_verified':False,'research_ready':False})
