"""Real C-mode reporting, plant N inventory, and external terminal allocation."""
import itertools
import os
from pathlib import Path
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.audits import enable_audit_outputs
from mars_env.input_metadata import canonical_ufga_metadata
from mars_env.dssat_backend import DssatBackend
from mars_env.sequence_audit import SequenceProtocol,replace_controls
from mars_env.balances import NitrogenInventoryDiagnostic,RemovalLedger
from mars_env.harvest_accounting import c_harvest_allocation,harvest_summary
from verify_sequence_handoff import normal


def transform(template,grain,stover):
    lines=canonical_ufga_metadata(enable_audit_outputs(template)).splitlines()
    replace_controls(lines,'@N HARVEST ',{'HPCNP':grain,'HPCNR':stover})
    return '\n'.join(lines)+'\n'


def run_case(folder,seed,managed,damage,grain,stover,*,binary='/opt/dssat_pdi/mars_sequence_audit_dscsm048',input_transform=None):
    folder.mkdir()
    def apply_input(t):
        t=transform(t,grain,stover)
        return input_transform(t) if input_transform is not None else t
    backend=DssatBackend(run_dssat_location=binary,filex_transform=apply_input)
    backend._instrumentation=SequenceProtocol();backend._runtime_log_path=str(folder/'runtime.log')
    inventory=NitrogenInventoryDiagnostic();removal=RemovalLedger();trace=[]
    try:
        state=backend.reset(seed)
        for _ in range(400):
            trace.append(normal(state));date,dap=int(state['yrdoy']),int(state['dap'])
            active=date>=backend.planting_yrdoy
            water=10 if managed and active and dap in (10,20,30,40,50,60,70,80) else 0
            nitrogen={40:27,45:35,80:54}.get(dap,0) if managed and active else 0
            backend._instrumentation.fraction=damage if active and dap in (30,31,32,33,34) else 0
            state,done,outcome=backend.step(water,nitrogen)
            if active:
                inventory.append(date,state['mars_plant_audit'])
                record=state.get('mars_leaf_diagnostic')
                if record and record['yrdoy']==date:removal.append(record)
            if done:
                trace.append(normal(state));break
        else:raise RuntimeError('C crop did not finish')
        assert outcome.reason=='harvest'
        assert len(state['mars_sequence_harvests'])==1
        h=normal(state['mars_sequence_harvests'][0])
        assert abs(h['grain_fraction']-grain/100)<=2**-24 and abs(h['stover_fraction']-stover/100)<=2**-24
        allocation=c_harvest_allocation(h)
        native=Path(backend._env._tmp_folder)
        for p in native.iterdir():
            if p.is_file():shutil.copy2(p,folder/p.name)
        summary=harvest_summary((folder/'Summary.OUT').read_text())
        for key,value in [('HWAH',allocation['grain_export']['dry_matter_kg_ha']),
                          ('BWAH',allocation['byproduct_export']['dry_matter_kg_ha'])]:
            assert abs(summary[key]-value)<=.5+2**-20*abs(value),(key,'printed harvest mismatch')
        assert inventory.summary()['plant_n_inventory_balance_within_tolerance']
        # External allocation cannot change final native crop or soil stocks.
        assert backend.state['mars_plant_audit']==state['mars_plant_audit']
        write_json(folder/'trace.json',trace);backend.close()
        result={'seed':seed,'managed':managed,'damage':damage,'grain_percent':grain,'stover_percent':stover,
                'harvest':h,'allocation':allocation,'summary':summary,'plant_n':inventory.summary(),
                'plant_n_rows':inventory.rows,'damage_export':removal.summary(),
                'native_after_harvest_plant_n_kg_ha':10*(state['mars_plant_audit']['canopy_n']+
                   state['mars_plant_audit']['rootn']*state['mars_plant_audit']['population']),
                'native_plant_state_physically_harvested':False,
                'files':{p.name:sha256(p) for p in folder.iterdir() if p.is_file()}}
        write_json(folder/'diagnostics.json',result)
        return result
    finally:backend.close()


if __name__=='__main__':
    run=new_run(ROOT,'c_harvest_accounting');print(run,flush=True)
    specs=[(123456,True,d,g,s) for d,g,s in itertools.product([0.,.03],[100,50],[0,50,100])]
    specs += [(456789,False,d,100,0) for d in (0.,.03)]
    cases=[]
    for i,spec in enumerate(specs):
        result=run_case(run/f'case_{i:02d}',*spec)
        cases.append({k:v for k,v in result.items() if k not in ('files','plant_n_rows')})
        print(f'Case {i} C allocation and plant N passed',flush=True)
    write_json(run/'verification.json',{'passed':True,'native_runs':len(cases),'cases':cases,
        'binary_sha256':sha256('/opt/dssat_pdi/mars_sequence_audit_dscsm048'),
        'scope':'C-mode harvest reporting and external allocation; not native physical harvest or ecosystem closure',
        'whole_postharvest_system_balance_verified':False,'whole_elemental_carbon_verified':False,'research_ready':False})
