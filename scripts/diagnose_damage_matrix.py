"""Native response matrix: technical transfer diagnostic, not literature validation."""
import json
from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json
from mars_env.leaf_diagnostics import LeafDiagnosticBackend
from mars_env.balances import RemovalLedger,NitrogenInventoryDiagnostic


def case(run,name,water,nitrogen,targets):
    backend=LeafDiagnosticBackend();backend._runtime_log_path=str(run/f'{name}_runtime.log')
    trace=[];pulses=[];pending=list(targets);removals=RemovalLedger();inventory=NitrogenInventoryDiagnostic()
    try:
        state=backend.reset(seed=123456)
        for _ in range(400):
            dap=int(state['dap']);date=int(state['yrdoy']);fraction=0
            if date>=backend.planting_yrdoy and pending and state['vstage']>=pending[0][0]:
                target,fraction=pending.pop(0);pulses.append({'target_vstage':target,'decision_date':date,'dap':dap,'fraction':fraction})
            irrigation=10 if water and date>=backend.planting_yrdoy and dap in (10,20,30,40,50,60,70,80) else 0
            fert={40:27,45:35,80:54}.get(dap,0) if nitrogen and date>=backend.planting_yrdoy else 0
            after,done,outcome=backend.step_damage(irrigation,fert,fraction)
            assert all(np.isfinite(float(after[k])) and after[k]>=0 for k in ('xlai','topwt','grnwt'))
            if date>=backend.planting_yrdoy:
                inventory.append(date,after['mars_plant_audit'])
                diagnostic=after.get('mars_leaf_diagnostic')
                if diagnostic and diagnostic['yrdoy']==date:removals.append(diagnostic)
                trace.append({'date':date,'dap':dap,'vstage':float(state['vstage']),'water':irrigation,'nitrogen':fert,
                    'fraction':fraction,'after_lai':float(after['xlai']),'after_topwt':float(after['topwt']),
                    'after_grain':float(after['grnwt']),'plant_n_residual':inventory.rows[-1]['residual_kg_ha']})
            state=after
            if done:break
        else:raise RuntimeError('Unterminated diagnostic')
        assert not pending,'Requested vegetative stage not reached'
        assert inventory.summary()['plant_n_inventory_balance_within_tolerance']
        write_json(run/f'{name}_trace.json',trace)
        return {'name':name,'water_regime':'scheduled_80mm' if water else 'rainfed','nitrogen_kg_ha':116 if nitrogen else 0,
            'pulses':pulses,'yield_kg_ha':outcome.harvested_grain_kg_ha,'reason':outcome.reason,
            'removal':removals.summary(),'plant_n':inventory.summary()}
    finally:backend.close()


def main():
    run=new_run(ROOT,'damage_response_matrix');print(f'RUN_DIR={run}',flush=True)
    treatments={'control':[],'repeat25':[(3,.25),(8,.25),(12,.25)]}
    treatments.update({f'v{stage}_{int(fraction*100)}':[(stage,fraction)] for stage in (3,8,12) for fraction in (.25,.75)})
    results=[]
    try:
        for water in (False,True):
            for nitrogen in (False,True):
                group=[]
                for label,targets in treatments.items():
                    name=f'w{int(water)}_n{int(nitrogen)}_{label}'
                    result=case(run,name,water,nitrogen,targets);group.append(result);print(name,result['yield_kg_ha'],flush=True)
                control=group[0]['yield_kg_ha']
                for result in group:result['paired_control_yield_ratio']=result['yield_kg_ha']/control if control else None
                results.extend(group)
        write_json(run/'verification.json',{'passed':True,'diagnostic_only':True,'research_ready':False,
            'seed':123456,'cases':results,'agronomic_validation':False,'field_parameters_calibrated':False,
            'note':'Fixed UFGA8201 transfer matrix; not a reproduction of study cultivars/sites/irrigation or calibrated pest pressure'})
    except BaseException as exc:
        write_json(run/'failure.json',{'passed':False,'error':repr(exc)});raise


if __name__=='__main__':main()
