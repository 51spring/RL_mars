"""Explicit F-mode chronology, first-year regression and supported N audit."""
import json
import os
from pathlib import Path
import sys
import tempfile
import psutil
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.f_mode_calendar import f_filex,launcher_text
from mars_env.carbon_audit import carbon_runs,carbon_coverage,audit_soil_carbon
from mars_env.actual_harvest_contract import check_actual_contract
from mars_env.multiyear_n import analyze_multiyear_n
from verify_multiyear_handoff import run_sequence


def main():
    os.environ.update(MARS_SEQUENCE_MODE='F',GFORTRAN_UNBUFFERED_ALL='y',
        MARS_SEQUENCE_BINARY='/opt/dssat_pdi/mars_actual_harvest_dscsm048')
    source=ROOT/'outputs/runs/20261106T073828Z_multiyear_handoff_479f1d6c/verification.json'
    q=json.loads(source.read_text());assert q['passed']
    run=new_run(ROOT,'multiyear_f');print('RUN_DIR='+str(run),flush=True)
    write_json(run/'effective_runtime.json',{'MARS_SEQUENCE_MODE':'F','GFORTRAN_UNBUFFERED_ALL':'y',
        'q_harvest_date_anchor_source':source.relative_to(ROOT).as_posix(),'q_source_sha256':sha256(source)})
    cases=[];errors=[];native_runs=0
    with tempfile.TemporaryDirectory(prefix='mars_f_launcher_') as tmp:
        launchers={}
        for treatments in (2,4):
            text=launcher_text(treatments);path=Path(tmp)/f'F{treatments}.sh'
            path.write_text(text);path.chmod(0o755);launchers[treatments]=path
            (run/f'launcher_F{treatments}.sh').write_text(text)
        for item in q['cases']:
            name=item['name'];grain=item['grain_percent'];stover=item['stover_percent']
            dates={int(h['run']):int(h['date']) for h in item['two_year_harvests']}
            outputs={}
            try:
                for label,long in (('one_year',False),('two_year',True)):
                    folder=run/name/label
                    builder=lambda t,long=long:f_filex(t,grain,stover,dates,two_years=long)
                    d,trace,actions=run_sequence(folder,grain,stover,long,filex_builder=builder,
                        native_launcher=launchers[4 if long else 2])
                    native_runs+=1;write_json(folder/'diagnostics.json',d)
                    rows=carbon_runs((folder/'SoilCBal.OUT').read_text(encoding='latin-1'))
                    coverage=carbon_coverage(rows,int(trace[-1]['yrdoy']))
                    if not coverage['complete']:raise ValueError('Terminal carbon output missing')
                    carbon=audit_soil_carbon(rows)
                    if carbon['days']!=(730 if long else 365):raise ValueError('F calendar coverage differs')
                    for crop_run in ((1,3) if long else (1,)):
                        h=next(h for h in d['harvests'] if h['run']==crop_run)
                        if int(h['date'])!=dates[crop_run]:raise ValueError('F harvest date differs from supplied date anchor')
                        ear=next(e for e in d['ear_records'] if e['dynamic']==6 and e['date']==h['date'])
                        if not check_actual_contract(h,ear)['passed']:raise ValueError('Native F harvest contract failed')
                        if abs(h['grain_fraction']-grain/100)>2**-24 or abs(h['stover_fraction']-stover/100)>2**-24:
                            raise ValueError('F harvest fractions differ')
                        annual=[a for a in actions if a['run']==crop_run]
                        if sum(a['water_mm'] for a in annual)!=80 or sum(a['nitrogen_kg_ha'] for a in annual)!=116:
                            raise ValueError('F annual management differs')
                    n=analyze_multiyear_n(folder,d,trace,actions,mode='F') if long else None
                    if n is not None:
                        write_json(folder/'integrated_n.json',n)
                        if not n['passed']:raise ValueError('F supported N inventory failed')
                    write_json(folder/'coverage.json',coverage)
                    write_json(folder/'source_files.json',{p.name:sha256(p) for p in folder.iterdir() if p.is_file()})
                    outputs[label]={'diagnostics':d,'rows':rows,'n':n,'carbon':carbon}
                    if psutil.Process().children(recursive=True):raise RuntimeError('F simulator child leaked')
                    print(name+' '+label+' passed',flush=True)
                a,b=outputs['one_year'],outputs['two_year']
                if a['diagnostics']['harvests'][0]!=b['diagnostics']['harvests'][0] or any(a['rows'][r]!=b['rows'][r] for r in (1,2)):
                    raise ValueError('F first-year prefix regression differs')
                cases.append({'name':name,'first_year_prefix_exact':True,'measured_F_harvest_dates':dates,
                    'nitrogen':{k:v for k,v in b['n'].items() if k!='rows'},
                    'carbon_output_days':a['carbon']['days']+b['carbon']['days']})
            except Exception as exc:
                error={'case':name,'exception':repr(exc)};errors.append(error)
                write_json(run/name/'failure.json',dict(passed=False,**error));print(str(error),flush=True)
            write_json(run/'partial_results.json',{'cases':cases,'errors':errors,'native_runs':native_runs})
    passed=len(cases)==2 and not errors
    write_json(run/'verification.json',{'passed':passed,'scope':'explicit F-mode two-year chronology and supported modeled N; no generic F agronomy or whole C claim',
        'cases':cases,'errors':errors,'native_runs':native_runs,'mode':'F','seed':123456,
        'site_soil_cultivar':['UFGA0002','IBMZ910014','IB0035'],'q_date_source_sha256':sha256(source),
        'binary_sha256':sha256(os.environ['MARS_SEQUENCE_BINARY']),
        'launcher_sha256':{p.name:sha256(p) for p in run.glob('launcher_*.sh')},
        'default_image_changed':False,'whole_elemental_carbon_verified':False,
        'independent_agronomic_validation':False,'research_ready':False})
    if not passed:raise SystemExit(1)
    print('F_MULTIYEAR_PASSED',flush=True)


if __name__=='__main__':main()
