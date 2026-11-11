"""Original versus fixed metadata, followed by read-only harvest boundary audit."""
import argparse
import json
import re
from pathlib import Path
import shutil
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.audits import enable_audit_outputs
from mars_env.dssat_backend import DssatBackend
from mars_env.leaf_diagnostics import LeafProtocol
from mars_env.harvest_diagnostics import HarvestBoundaryBackend
from mars_env.input_metadata import canonical_ufga_metadata,field_metadata,summary_metadata
from mars_env.balances import RemovalLedger,NitrogenInventoryDiagnostic


def normal(value):
    if isinstance(value,dict):return {k:normal(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):return [normal(x) for x in value]
    return value.tolist() if hasattr(value,'tolist') else value


def transform(template,variant):
    result=enable_audit_outputs(template)
    if variant!='raw':result=canonical_ufga_metadata(result)
    if variant=='bad_lon':result=field_metadata(result,longitude='BAD')
    if variant=='bad_elev':result=field_metadata(result,elevation='BAD')
    if variant=='missing':result=field_metadata(result,longitude=-999,latitude=-99,elevation=-99)
    if variant=='deep':
        lines=result.splitlines()
        for i,line in enumerate(lines):
            if line.startswith('@P PDATE'):
                row=lines[i+1];spans=list(re.finditer(r'\S+',row));index=line.split().index('PLDP')
                left,right=spans[index-1].end(),spans[index].end()
                lines[i+1]=row[:left]+'100'.rjust(right-left)+row[right:];break
        result='\n'.join(lines)+'\n'
    return result


def run_case(run,name,binary,variant,seed,managed,damage=0.,harvest=False):
    folder=run/name;folder.mkdir()
    factory=HarvestBoundaryBackend if harvest else DssatBackend
    backend=factory(run_dssat_location=binary,filex_transform=lambda t:transform(t,variant))
    if not harvest:backend._instrumentation=LeafProtocol()
    backend._runtime_log_path=str(folder/'runtime.log')
    trace=[];n_inventory=NitrogenInventoryDiagnostic();ledger=RemovalLedger()
    try:
        state=backend.reset(seed)
        for _ in range(400):
            trace.append(normal(state))
            date,dap=int(state['yrdoy']),int(state['dap'])
            water=10 if managed and date>=backend.planting_yrdoy and dap in (10,20,30,40,50,60,70,80) else 0
            nitrogen={40:27,45:35,80:54}.get(dap,0) if managed and date>=backend.planting_yrdoy else 0
            fraction=damage if date>=backend.planting_yrdoy and dap in (30,31,32,33,34) else 0
            backend._instrumentation.fraction=fraction
            after,done,outcome=DssatBackend.step(backend,water,nitrogen)
            if date>=backend.planting_yrdoy:
                n_inventory.append(date,after['mars_plant_audit'])
                record=after.get('mars_leaf_diagnostic')
                if record and record['yrdoy']==date:ledger.append(record)
            state=after
            if done:
                trace.append(normal(state));break
        else:raise RuntimeError('Season did not finish')
        native=backend._env;source=Path(native._tmp_folder)
        native.close(_close_tmp=False)
        for file in source.iterdir():
            if file.is_file() and file.suffix.upper() in ('.OUT','.MZX','.YML'):
                shutil.copy2(file,folder/file.name)
        native._close_tmp_folder()
        write_json(folder/'trace.json',trace)
        warnings=(folder/'WARNING.OUT').read_text()
        report={'steps':len(trace)-1,'summary_metadata':summary_metadata((folder/'Summary.OUT').read_text()),
            'outcome':normal(vars(outcome)),'plant_n':n_inventory.summary(),'removed':ledger.summary(),
            'warnings':warnings,'final_plant_audit':normal(state['mars_plant_audit']),
            'harvest_boundary':normal(state.get('mars_harvest_boundary')),
            'files':{p.name:sha256(p) for p in folder.iterdir() if p.is_file()}}
        assert report['plant_n']['plant_n_inventory_balance_within_tolerance']
        return report,trace
    finally:backend.close()


def main():
    p=argparse.ArgumentParser();p.add_argument('--image-id');args=p.parse_args()
    run=new_run(ROOT,'metadata_harvest',image_id=args.image_id);print(f'RUN_DIR={run}',flush=True)
    cases={};pairs=[]
    try:
        specifications=[(seed,managed,variant,damage) for seed in (123456,456789)
            for managed in (False,True) for variant in ('raw','canonical') for damage in (0.,.03)]
        specifications += [(123456,True,variant,0.) for variant in ('bad_lon','bad_elev','missing','deep')]
        for i,(seed,managed,variant,damage) in enumerate(specifications):
            pair=[]
            for label,binary in [('original','/opt/mars/run_leaf'),('fixed','/opt/mars/run_metadata')]:
                name=f'{i:02d}_{variant}_{label}'
                report,trace=run_case(run,name,binary,variant,seed,managed,damage)
                cases[name]=report;pair.append(trace)
            assert pair[0]==pair[1],f'Metadata patch changed privileged crop/weather state in case {i}'
            fixed=cases[f'{i:02d}_{variant}_fixed'];warning=fixed['warnings'].lower()
            assert 'error transferring variable' not in warning
            assert 'saturated hydraulic conductivity equal to zero' not in warning
            if variant in ('canonical','deep'):
                assert fixed['summary_metadata']=={'XLAT':29.6380,'LONG':-82.3689,'ELEV':40.}
                assert 'error reading latitude' not in warning and 'error reading longitude' not in warning
            if variant=='raw':assert fixed['summary_metadata']=={'XLAT':-82.3689,'LONG':29.6380,'ELEV':40.}
            if variant=='bad_elev':
                assert 'error reading elevation' in warning
                assert fixed['summary_metadata']['XLAT']==29.6380
                assert fixed['summary_metadata']['LONG']==-82.3689
            if variant=='bad_lon':assert 'error reading longitude' in warning
            if variant=='deep':assert fixed['outcome']['reason']=='crop_failure'
            pairs.append({'id':i,'seed':seed,'managed':managed,'variant':variant,'damage':damage,
                          'crop_weather_trace_exact':True,'metadata':fixed['summary_metadata']})
            print(f'Pair {i}: {variant}, managed={managed}, damage={damage} exact',flush=True)
        harvest_cases={}
        for damage in (0.,.03):
            name=f'harvest_{damage}'
            result,trace=run_case(run,name,'/opt/mars/run_boundary','canonical',123456,True,damage,True)
            # Instrumentation has no effect on existing fields; compare native event-free binary.
            control,control_trace=run_case(run,name+'_control','/opt/mars/run_metadata','canonical',123456,True,damage)
            for row in trace:row.pop('mars_harvest_boundary',None)
            assert trace==control_trace,'Read-only harvest diagnostics changed native crop state'
            boundary=result['harvest_boundary'];assert boundary and int(boundary['rnmode'])==ord('C')
            assert abs(boundary['grain_dm']-result['outcome']['harvested_grain_kg_ha'])<=.51
            assert boundary['residue_dm']==boundary['residue_n']==0.,'Unexpected native residues in C mode'
            assert boundary['canopy_n']>=boundary['harvest_grain_n']>=0
            harvest_cases[name]={'boundary':boundary,'removed':result['removed'],
                'diagnostic_trajectory_exact':True,'crop_state_not_physically_harvested':True,
                'native_post_harvest_soil_transfer_in_C_mode':False}
        write_json(run/'verification.json',{'passed':True,'pairs':pairs,'cases':cases,'harvest':harvest_cases,
            'original_vendor_unchanged':True,'metadata_input_correction_applied_to_default_training':False,
            'whole_elemental_carbon_balance_validated':False,'post_harvest_ecosystem_balance_validated':False,
            'research_ready':False})
        print('METADATA_AND_HARVEST_AUDIT_PASSED',flush=True)
    except BaseException as exc:
        write_json(run/'failure.json',{'passed':False,'error':repr(exc),'completed_pairs':pairs});raise


if __name__=='__main__':main()
