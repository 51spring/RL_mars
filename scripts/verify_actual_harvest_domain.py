"""New generic soils and native planting failure; retain unsupported cases."""
import json
import os
from pathlib import Path
import shutil
import sys
import psutil
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.domain_inputs import soil_profile,diagnostic_soil_input
from mars_env.actual_harvest_contract import check_actual_contract
from mars_env.sequence_audit import analyze_handoff
from mars_env.ear_diagnostics import EarProtocol
from mars_env.integrated_n import analyze_integrated_n
from mars_env.dssat_backend import DssatBackend
from mars_env.audits import enable_audit_outputs
from mars_env.input_metadata import canonical_ufga_metadata
from verify_sequence_handoff import run_case,normal
from verify_c_harvest_accounting import run_case as run_c
from verify_harvest_n_candidate import crop_trace,crop_output,independent_n
from verify_crop_failure import deep_planting

BINARIES={'control':'/opt/dssat_pdi/mars_ear_audit_dscsm048',
          'candidate':'/opt/dssat_pdi/mars_actual_harvest_dscsm048'}


def failure_case(folder,binary):
    folder.mkdir(parents=True)
    transform=lambda t:deep_planting(canonical_ufga_metadata(enable_audit_outputs(t)))
    backend=DssatBackend(run_dssat_location=binary,filex_transform=transform)
    backend._instrumentation=EarProtocol();backend._runtime_log_path=str(folder/'runtime.log')
    trace=[]
    try:
        state=backend.reset(123456)
        for step in range(400):
            trace.append(normal(state))
            state,done,outcome=backend.step(0,0)
            if done:
                trace.append(normal(state));break
        else:raise RuntimeError('Deep planting did not terminate')
        source=Path(backend._env._tmp_folder)
        for p in source.iterdir():
            if p.is_file():shutil.copy2(p,folder/p.name)
        write_json(folder/'trace.json',trace)
        result={'reason':outcome.reason,'grain_kg_ha':outcome.harvested_grain_kg_ha,
            'steps':step+1,'harvest_records':normal(state['mars_sequence_harvests']),
            'contract_applicable':False,'scope':'crop failure bypass; no claim of zero-population harvest support',
            'warning':(folder/'WARNING.OUT').read_text()}
        if outcome.reason!='crop_failure' or outcome.harvested_grain_kg_ha!=0:
            raise ValueError('Expected proven native failure with zero harvested grain')
        write_json(folder/'failure_diagnostic.json',result)
        return result
    finally:backend.close()


def main():
    run=new_run(ROOT,'actual_harvest_domain');print('RUN_DIR='+str(run),flush=True)
    soil_path=Path('/opt/dssat_pdi/Soil/SOIL.SOL');soil_text=soil_path.read_text(errors='replace')
    profiles={identifier:soil_profile(soil_text,identifier) for identifier in ('IB00000004','IB00000010')}
    write_json(run/'soil_profiles.json',profiles)
    cases=[];errors=[];date_sources=[];native_runs=0
    try:
        for identifier,profile in profiles.items():
            transform=lambda template,p=profile:diagnostic_soil_input(template,p)
            for managed in (False,True):
                stem=f'{identifier}_m{int(managed)}'
                date_case=run_c(run/(stem+'_date'),123456,managed,.03,100,0,
                    binary=BINARIES['control'],input_transform=transform)
                native_runs+=1;date=int(date_case['harvest']['date'])
                date_sources.append({'name':stem,'harvest_date':date})
                for mode in ('Q','F'):
                    name=stem+'_'+mode;pair={}
                    for label,binary in BINARIES.items():
                        os.environ['MARS_SEQUENCE_BINARY']=binary;folder=run/name/label
                        try:
                            d=run_case(folder,mode,100,0,.03,seed=123456,managed=managed,
                                fallow_start=date,instrumentation=EarProtocol(),input_transform=transform)
                            native_runs+=1
                            h=d['harvests'][0]
                            ear=next(r for r in reversed(d['ear_records']) if r['dynamic']==6)
                            d['v2_contract']=check_actual_contract(h,ear)
                            d['handoff']=analyze_handoff(d)
                            d['plant_n']=independent_n(folder,d)['plant_n']
                            if label=='candidate':
                                trace=json.loads((folder/'trace.json').read_text())
                                d['integrated_n']=analyze_integrated_n(folder,d,trace)
                            write_json(folder/'contract_diagnostics.json',d)
                            pair[label]=d
                        except Exception as exc:
                            errors.append({'case':name,'label':label,'exception':repr(exc)})
                            write_json(folder/'domain_error.json',errors[-1])
                    if len(pair)==2:
                        exact=(crop_trace(run/name/'control')==crop_trace(run/name/'candidate')
                            and pair['control']['ear_records']==pair['candidate']['ear_records']
                            and all(crop_output(run/name/'control',file)==crop_output(run/name/'candidate',file)
                                    for file in ('Summary.OUT','PlantGro.OUT','PlantN.OUT')))
                        c=pair['candidate'];n=c['integrated_n']
                        passed=(exact and c['v2_contract']['passed'] and c['handoff']['handoff_passed']
                            and c['plant_n']['plant_n_inventory_balance_within_tolerance']
                            and n['combined_model_n_evidence_passed'] and n['fallow_initial_inventory_passed']
                            and n['final_inventory_passed'])
                        cases.append({'name':name,'soil_id':identifier,'managed':managed,'mode':mode,
                            'passed':passed,'crop_outputs_and_direct_organs_exact':exact,
                            'candidate_contract':c['v2_contract'],
                            'integrated_n':{k:v for k,v in n.items() if k!='rows'}})
                    write_json(run/'partial_results.json',{'cases':cases,'errors':errors})
                    if psutil.Process().children(recursive=True):raise RuntimeError('Simulator child leaked')
                    print(name+' retained',flush=True)
        failures={}
        for label,binary in BINARIES.items():
            failures[label]=failure_case(run/('deep_planting_'+label),binary);native_runs+=1
        failure_exact=(failures['control']['reason']==failures['candidate']['reason']
            and failures['control']['grain_kg_ha']==failures['candidate']['grain_kg_ha']
            and crop_trace(run/'deep_planting_control')==crop_trace(run/'deep_planting_candidate'))
        if psutil.Process().children(recursive=True):raise RuntimeError('Failure simulator child leaked')
        passed=len(cases)==8 and all(c['passed'] for c in cases) and not errors and failure_exact
        write_json(run/'verification.json',{'passed':passed,'scope':'generic soil diagnostic transfer, modeled N and native planting-failure bypass; not field or multiyear validation',
            'contract_version':'standing_stock_actual_yield_v2','cases':cases,'errors':errors,
            'native_runs':native_runs,'qf_pairs':len(cases),'c_date_sources':date_sources,
            'failure_cases':failures,'failure_trajectory_exact':failure_exact,
            'soil_file_sha256':sha256(soil_path),'soil_profile_artifact_sha256':sha256(run/'soil_profiles.json'),
            'binary_sha256':{k:sha256(v) for k,v in BINARIES.items()},
            'default_image_changed':False,'whole_elemental_carbon_verified':False,
            'zero_population_harvest_supported':False,'multiyear_validated':False,
            'independent_agronomic_validation':False,'research_ready':False})
        print('DOMAIN_CHECKS_PASSED='+str(passed),flush=True)
        if not passed:raise SystemExit(1)
    except Exception as exc:
        write_json(run/'failure.json',{'passed':False,'exception':repr(exc),'native_runs_completed':native_runs,'errors':errors})
        raise


if __name__=='__main__':main()
