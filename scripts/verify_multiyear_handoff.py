"""Two-year Q sequence: native boundaries, crop contracts, first-year regression."""
import json
import os
from pathlib import Path
import shutil
import sys
import psutil
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.sequence_audit import SequenceAuditBackend,sequence_filex
from mars_env.multiyear_audit import two_year_filex,audit_boundaries
from mars_env.ear_diagnostics import EarProtocol
from mars_env.actual_harvest_contract import check_actual_contract
from mars_env.carbon_audit import carbon_runs,audit_soil_carbon
from mars_env.audits import shift_yrdoy
from verify_sequence_handoff import normal


def run_sequence(folder,grain,stover,two_years,*,input_transform=None,filex_builder=None,native_launcher=None,managed=True):
    folder.mkdir(parents=True)
    backend=SequenceAuditBackend(grain_percent=grain,stover_percent=stover)
    backend.filex_transform=(lambda t:two_year_filex(t,grain,stover)) if two_years else (
        lambda t:sequence_filex(t,grain,stover,'Q'))
    if filex_builder is not None:backend.filex_transform=filex_builder
    if native_launcher is not None:backend.run_dssat_location=str(native_launcher)
    if input_transform is not None:
        original_transform=backend.filex_transform
        backend.filex_transform=lambda t:input_transform(original_transform(t))
    backend._instrumentation=EarProtocol();backend._runtime_log_path=str(folder/'runtime.log')
    trace=[];actions=[]
    try:
        state=backend.reset(123456)
        for _ in range(1200):
            trace.append(normal(state))
            run=int(state['mars_sequence_soils'][-1]['run'])
            planting={1:1982057,3:1983057}.get(run)
            date,dap=int(state['yrdoy']),int(state['dap'])
            active=planting is not None and date>=planting
            if active and shift_yrdoy(planting,dap)!=date:raise ValueError('Planting-relative native action calendar differs')
            water=10 if managed and active and dap in (10,20,30,40,50,60,70,80) else 0
            nitrogen={40:27,45:35,80:54}.get(dap,0) if managed and active else 0
            damage=.03 if active and dap in (30,31,32,33,34) else 0
            actions.append(dict(run=run,date=date,dap=dap,water_mm=water,nitrogen_kg_ha=nitrogen,damage=damage))
            state,done,_=backend.step_damage(water,nitrogen,damage)
            if done:trace.append(normal(state));break
        else:raise RuntimeError('Multiyear diagnostic exceeded1200steps')
        result={'harvests':normal(state['mars_sequence_harvests']),
            'soils':normal(state['mars_sequence_soils']),'ear_records':normal(state['mars_ear_records']),
            'steps':len(actions),'two_years':two_years}
        return result,trace,actions
    finally:
        if backend._env is not None:
            source=Path(backend._env._tmp_folder)
            if source.exists():
                for p in source.iterdir():
                    if p.is_file():shutil.copy2(p,folder/p.name)
        write_json(folder/'trace.json',trace);write_json(folder/'actions.json',actions)
        backend.close()


def main():
    # Diagnostic-local runtime setting: flush all Fortran output units before
    # PDI blocks/owned-process cleanup. Default PPO images/settings unchanged.
    os.environ['GFORTRAN_UNBUFFERED_ALL']='y'
    run=new_run(ROOT,'multiyear_handoff');print('RUN_DIR='+str(run),flush=True)
    write_json(run/'effective_runtime.json',{'GFORTRAN_UNBUFFERED_ALL':'y',
        'scope':'this diagnostic process and its native children only'})
    os.environ['MARS_SEQUENCE_MODE']='Q'
    os.environ['MARS_SEQUENCE_BINARY']='/opt/dssat_pdi/mars_actual_harvest_dscsm048'
    cases=[]
    try:
        for grain,stover in ((100,0),(50,50)):
            name=f'g{grain}_s{stover}';out={}
            for label,long in (('one_year',False),('two_year',True)):
                folder=run/name/label;d,trace,actions=run_sequence(folder,grain,stover,long)
                write_json(folder/'diagnostics.json',d)
                rows=carbon_runs((folder/'SoilCBal.OUT').read_text(encoding='latin-1'))
                final_row=rows[max(rows)][-1]
                if int(final_row['YEAR'])*1000+int(final_row['DOY'])!=int(trace[-1]['yrdoy']):
                    raise ValueError('Terminal soil carbon output coverage is incomplete')
                d['soil_carbon_arithmetic']=audit_soil_carbon(rows)
                for crop_run in ((1,3) if long else (1,)):
                    h=next(h for h in d['harvests'] if h['run']==crop_run)
                    ear=next(e for e in d['ear_records'] if e['dynamic']==6 and e['date']==h['date'])
                    contract=check_actual_contract(h,ear)
                    if not contract['passed']:raise ValueError('Crop harvest boundary failed')
                    if abs(h['grain_fraction']-grain/100)>2**-24 or abs(h['stover_fraction']-stover/100)>2**-24:
                        raise ValueError('Native harvest fractions differ')
                    selected=[a for a in actions if a['run']==crop_run]
                    if sum(a['water_mm'] for a in selected)!=80 or sum(a['nitrogen_kg_ha'] for a in selected)!=116:
                        raise ValueError('Annual management schedule missing or duplicated')
                if long:
                    d['boundaries']=audit_boundaries(d)
                    if not d['boundaries']['passed']:raise ValueError('Multiyear handoff failed')
                    if set(rows)!={1,2,3,4}:raise ValueError('Four native output runs not completed')
                    if int(trace[-1]['yrdoy'])!=1984029:raise ValueError('Two-year terminal date differs')
                write_json(folder/'analysis.json',d)
                out[label]={'diagnostics':d,'carbon_rows':rows}
                if psutil.Process().children(recursive=True):raise RuntimeError('Simulator child leaked after close')
                print(name+' '+label+' completed',flush=True)
            short,long=out['one_year'],out['two_year']
            first_crop_exact=short['diagnostics']['harvests'][0]==long['diagnostics']['harvests'][0]
            first_cycle_soil_c_exact=all(short['carbon_rows'][r]==long['carbon_rows'][r] for r in (1,2))
            if not first_crop_exact or not first_cycle_soil_c_exact:raise ValueError('First-year prefix regression differs')
            cases.append({'name':name,'grain_percent':grain,'stover_percent':stover,
                'first_crop_harvest_exact':first_crop_exact,'first_cycle_soil_carbon_outputs_exact':first_cycle_soil_c_exact,
                'two_year_harvests':long['diagnostics']['harvests'],
                'boundary_audit':long['diagnostics']['boundaries'],
                'soil_carbon_arithmetic':long['diagnostics']['soil_carbon_arithmetic']})
            write_json(run/'partial_results.json',cases)
        write_json(run/'verification.json',{'passed':True,'scope':'two-year Q-mode crop/fallow residue boundary and crop harvest contracts; not full multiyear N/C or agronomic validation',
            'native_runs':4,'two_year_sequences':2,'one_year_prefix_controls':2,'cases':cases,
            'seed':123456,'mode':'Q','site_soil_cultivar':['UFGA0002','IBMZ910014','IB0035'],
            'binary_sha256':sha256(os.environ['MARS_SEQUENCE_BINARY']),
            'owned_children_after_close':0,'multiyear_full_n_balance_verified':False,
            'native_io':{'GFORTRAN_UNBUFFERED_ALL':'y','terminal_soil_carbon_coverage_complete':True},
            'whole_elemental_carbon_verified':False,'independent_agronomic_validation':False,'research_ready':False})
        print('MULTIYEAR_HANDOFF_PASSED',flush=True)
    except Exception as exc:
        write_json(run/'failure.json',{'passed':False,'exception':repr(exc),'completed_cases':cases,'research_ready':False})
        raise


if __name__=='__main__':main()
