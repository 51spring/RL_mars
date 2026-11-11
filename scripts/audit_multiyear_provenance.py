"""Pin full output coverage and qualify older buffered carbon samples."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.carbon_audit import carbon_runs,carbon_coverage,audit_soil_carbon


if __name__=='__main__':
    source=ROOT/'outputs/runs/20261106T073828Z_multiyear_handoff_479f1d6c'
    buffered=ROOT/'outputs/runs/20261106T073608Z_multiyear_handoff_5e834581'
    legacy=ROOT/'outputs/runs/20261106T070340Z_actual_harvest_domain_3ef3f2a6'
    native=json.loads((source/'verification.json').read_text());assert native['passed']
    run=new_run(ROOT,'multiyear_output_qualification');cases=[];comparisons=[];older=[]
    for case in native['cases']:
        for label in ('one_year','two_year'):
            folder=source/case['name']/label;trace=json.loads((folder/'trace.json').read_text())
            rows=carbon_runs((folder/'SoilCBal.OUT').read_text(encoding='latin-1'))
            coverage=carbon_coverage(rows,int(trace[-1]['yrdoy']));assert coverage['complete']
            arithmetic=audit_soil_carbon(rows)
            expected_days=730 if label=='two_year' else 365
            assert arithmetic['days']==expected_days
            cases.append({'case':case['name'],'label':label,'coverage':coverage,'days':arithmetic['days'],
                'files':{p.name:sha256(p) for p in folder.iterdir() if p.is_file()}})
    for label in ('one_year','two_year'):
        old=buffered/'g100_s0'/label;new=source/'g100_s0'/label
        assert json.loads((old/'trace.json').read_text())==json.loads((new/'trace.json').read_text())
        trace=json.loads((old/'trace.json').read_text());old_rows=carbon_runs((old/'SoilCBal.OUT').read_text())
        coverage=carbon_coverage(old_rows,int(trace[-1]['yrdoy']))
        comparisons.append({'label':label,'native_states_exact':True,'buffered_coverage':coverage,
            'old_trace_sha256':sha256(old/'trace.json'),'new_trace_sha256':sha256(new/'trace.json'),
            'old_carbon_sha256':sha256(old/'SoilCBal.OUT'),'new_carbon_sha256':sha256(new/'SoilCBal.OUT')})
    index=json.loads((legacy/'verification.json').read_text())
    for case in index['cases']:
        for label in ('control','candidate'):
            folder=legacy/case['name']/label;trace=json.loads((folder/'trace.json').read_text())
            coverage=carbon_coverage(carbon_runs((folder/'SoilCBal.OUT').read_text()),int(trace[-1]['yrdoy']))
            older.append({'case':case['name'],'label':label,**coverage,
                'carbon_sha256':sha256(folder/'SoilCBal.OUT')})
    write_json(run/'verification.json',{'passed':True,'scope':'multiyear complete output provenance and buffered-tail qualification; no whole C/N promotion',
        'native_source_report_sha256':sha256(source/'verification.json'),'native_source':source.relative_to(ROOT).as_posix(),
        'complete_new_output_cases':cases,'complete_new_soil_c_days':sum(c['days'] for c in cases),
        'buffering_controls':comparisons,'older_domain_carbon_coverage':older,
        'older_daily_arithmetic_still_valid':True,'older_final_cumbal_is_last_printed_not_proven_terminal':True,
        'GFORTRAN_UNBUFFERED_ALL':'y','runtime_documentation':'https://gcc.gnu.org/onlinedocs/gfortran/GFORTRAN_005fUNBUFFERED_005fALL.html',
        'new_native_runs':0,'multiyear_full_n_balance_verified':False,'whole_elemental_carbon_verified':False,'research_ready':False})
    print(run)
