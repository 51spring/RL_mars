"""Generic-soil two-year Q diagnostic with first-cycle controls and N audit."""
import json
import os
from pathlib import Path
import re
import shutil
import sys
import psutil
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.domain_inputs import soil_profile,diagnostic_soil_input,verify_effective_layers
from mars_env.carbon_audit import carbon_runs,carbon_coverage,audit_soil_carbon
from mars_env.actual_harvest_contract import check_actual_contract
from mars_env.multiyear_n import analyze_multiyear_n
from verify_multiyear_handoff import run_sequence
from audit_multiyear_n import alter_table


def effective_soil(folder,profile):
    text=(folder/'OVERVIEW.OUT').read_text(encoding='latin-1')
    ids=re.findall(r'^ SOIL\s+: (\S+)',text,re.M)
    if not ids or set(ids)!={profile['identifier']}:raise ValueError('Loaded soil ID differs')
    part=text.split('*SUMMARY OF SOIL AND GENETIC INPUT PARAMETERS',1)[1].split('SOIL ALBEDO',1)[0]
    rows=[]
    for line in part.splitlines():
        m=re.match(r'^\s*(\d+)-\s*(\d+)\s+(.+)$',line)
        if m:
            values=list(map(float,m[3].split()))
            rows.append(dict(top=int(m[1]),bottom=int(m[2]),SLLL=values[0],SDUL=values[1],SSAT=values[2],SH2O=values[4]))
    verify_effective_layers(profile,rows)
    warning=(folder/'WARNING.OUT').read_text(encoding='latin-1')
    return {'passed':True,'soil_ids':ids,'source_layers':len(profile['layers']),'native_layers':len(rows),
        'warnings':{'humus_cn_reset_to_10':'C:N ratio of 10.0 will be used' in warning,
                    'minimum_organic_carbon_estimated':'minimum value of OC' in warning,
                    'surface_mulch_effects_not_modeled':'No mulch effects' in warning},
        'overview_sha256':sha256(folder/'OVERVIEW.OUT'),'warning_sha256':sha256(folder/'WARNING.OUT')}


def main():
    os.environ.update(GFORTRAN_UNBUFFERED_ALL='y',MARS_SEQUENCE_MODE='Q',
        MARS_SEQUENCE_BINARY='/opt/dssat_pdi/mars_actual_harvest_dscsm048')
    run=new_run(ROOT,'multiyear_generic_soils');print('RUN_DIR='+str(run),flush=True)
    soil_path=Path('/opt/dssat_pdi/Soil/SOIL.SOL');text=soil_path.read_text(encoding='latin-1')
    profiles={i:soil_profile(text,i) for i in ('IB00000004','IB00000010')}
    write_json(run/'soil_profiles.json',profiles)
    write_json(run/'effective_runtime.json',{'GFORTRAN_UNBUFFERED_ALL':'y','scope':'diagnostic process only'})
    cases=[];errors=[];completed_native_runs=0
    for identifier,profile in profiles.items():
        transform=lambda t,p=profile:diagnostic_soil_input(t,p)
        for grain,stover in ((100,0),(50,50)):
            name=f'{identifier}_g{grain}_s{stover}';outputs={}
            try:
                for label,long in (('one_year',False),('two_year',True)):
                    folder=run/name/label
                    d,trace,actions=run_sequence(folder,grain,stover,long,input_transform=transform)
                    completed_native_runs+=1;write_json(folder/'diagnostics.json',d)
                    native_soil=effective_soil(folder,profile)
                    rows=carbon_runs((folder/'SoilCBal.OUT').read_text(encoding='latin-1'))
                    coverage=carbon_coverage(rows,int(trace[-1]['yrdoy']))
                    if not coverage['complete']:raise ValueError('Terminal soil C output missing')
                    carbon=audit_soil_carbon(rows)
                    if carbon['days']!=(730 if long else 365):raise ValueError('Native daily period differs')
                    for crop_run in ((1,3) if long else (1,)):
                        h=next(h for h in d['harvests'] if h['run']==crop_run)
                        ear=next(e for e in d['ear_records'] if e['dynamic']==6 and e['date']==h['date'])
                        if not check_actual_contract(h,ear)['passed']:raise ValueError('Native harvest contract failed')
                        if abs(h['grain_fraction']-grain/100)>2**-24 or abs(h['stover_fraction']-stover/100)>2**-24:
                            raise ValueError('Harvest fractions differ')
                        annual=[a for a in actions if a['run']==crop_run]
                        if sum(a['water_mm'] for a in annual)!=80 or sum(a['nitrogen_kg_ha'] for a in annual)!=116:
                            raise ValueError('Annual management amounts differ')
                    n=analyze_multiyear_n(folder,d,trace,actions) if long else None
                    if n is not None:
                        write_json(folder/'integrated_n.json',n)
                        if not n['passed']:raise ValueError('Two-year N inventory failed')
                    outputs[label]={'diagnostics':d,'rows':rows,'native_soil':native_soil,'carbon':carbon,
                                    'coverage':coverage,'nitrogen':n}
                    write_json(folder/'source_files.json',{p.name:sha256(p) for p in folder.iterdir() if p.is_file()})
                    if psutil.Process().children(recursive=True):raise RuntimeError('Simulator child leaked')
                    print(name+' '+label+' passed',flush=True)
                a,b=outputs['one_year'],outputs['two_year']
                if a['diagnostics']['harvests'][0]!=b['diagnostics']['harvests'][0] or any(a['rows'][r]!=b['rows'][r] for r in (1,2)):
                    raise ValueError('First-year prefix regression differs')
                # Corrupt a copy of the newly covered soil's year-2 inventory.
                source=run/name/'two_year';target=run/name/'negative_initial_no3';target.mkdir()
                for file in ('SoilNoBal.OUT','SoilNiBal.OUT','MgmtEvent.OUT'):shutil.copy2(source/file,target/file)
                alter_table(target/'SoilNiBal.OUT','NO3',0,1.)
                try:
                    bad=analyze_multiyear_n(target,b['diagnostics'],json.loads((source/'trace.json').read_text()),json.loads((source/'actions.json').read_text()))
                    rejected=not bad['passed'];reason='inventory failed'
                except ValueError as exc:rejected=True;reason=str(exc)
                if not rejected:raise ValueError('New-soil initialization negative control accepted')
                negative={'rejected':rejected,'reason':reason,'mutation':'year2 initial NO3 +1kgN/ha',
                    'files':{p.name:sha256(p) for p in target.iterdir() if p.is_file()}}
                write_json(target/'verification.json',negative)
                cases.append({'name':name,'soil_id':identifier,'grain_percent':grain,'stover_percent':stover,
                    'first_year_regression_exact':True,'negative_control':negative,'effective_soil':b['native_soil'],
                    'carbon_output_days':a['carbon']['days']+b['carbon']['days'],
                    'nitrogen':{k:v for k,v in b['nitrogen'].items() if k!='rows'}})
            except Exception as exc:
                error={'case':name,'exception':repr(exc)};errors.append(error)
                write_json(run/name/'failure.json',dict(passed=False,**error))
                print(name+' FAILED '+repr(exc),flush=True)
            write_json(run/'partial_results.json',{'cases':cases,'errors':errors,'completed_native_runs':completed_native_runs})
    passed=len(cases)==4 and not errors
    write_json(run/'verification.json',{'passed':passed,'scope':'two generic soils, two-year Q modeled N and boundaries; not field agronomy or elemental C',
        'cases':cases,'errors':errors,'native_runs':completed_native_runs,'two_year_sequences':4,'one_year_controls':4,
        'soil_file_sha256':sha256(soil_path),'soil_profiles_sha256':sha256(run/'soil_profiles.json'),
        'candidate_binary_sha256':sha256(os.environ['MARS_SEQUENCE_BINARY']),'native_io':'GFORTRAN_UNBUFFERED_ALL=y',
        'seed':123456,'mode':'Q','default_image_changed':False,'whole_elemental_carbon_verified':False,
        'independent_agronomic_validation':False,'research_ready':False})
    if not passed:raise SystemExit(1)
    print('MULTIYEAR_GENERIC_SOILS_PASSED',flush=True)


if __name__=='__main__':main()
