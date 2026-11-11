"""Independent native readback: rejected dates, used coefficients, weather and stocks."""
from collections import defaultdict
import json
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.audits import weather_rows
from mars_env.dssat_backend import read_summary
from mars_env.integrated_n import run_tables
from mars_env.lirf_native_compat import require_supported_native_dates
from qualify_agmip_writer_outputs import table


def main():
    source=ROOT/'outputs/runs/20261106T133233Z_lirf_native_inputs_574604f1'
    run=new_run(ROOT,'lirf_native_qualification');print(run,flush=True)
    native=json.loads((source/'verification.json').read_text());assert native['passed']
    accepted=[];negatives=[];all_weather=[];files={}
    for case in native['cases']:
        folder=source/case['name'];assert not case['timed_out'] and not case['owned_alive_after_wait']
        if case['returncode']==99:
            error=(folder/'ERROR.OUT').read_text(encoding='latin-1')
            assert 'IPSLIN' in error and 'Initial conditions date is defined prior to the start of simulation' in error
            assert not case['summary_exists'] and not case['completed_cycle_marker']
            negatives.append(dict(case=case['name'],kind='initial_date_before_simulation_start',rejected=True));continue
        assert case['returncode']==0 and case['completed_cycle_marker']
        assert len([line for line in (folder/'RunList.OUT').read_text().splitlines() if re.match(r'^\s+1\s+1\s+1\s+1',line)])==1
        summary=read_summary((folder/'Summary.OUT').read_text())
        overview=(folder/'OVERVIEW.OUT').read_text(encoding='latin-1')
        coefficients={key:float(re.search(r'\b'+key+r'\s*:\s*([-\d.]+)',overview)[1])
            for key in ('P1','P2','P5','G2','G3','PHINT')}
        injected='048' in case['name']
        expected=[245.6,.156,704.4,994.,6.239,52.88] if injected else [215.,.4,795.,890.,8.,48.]
        assert list(coefficients.values())==expected
        assert 'STARTING DATE  : JAN  1 2008' in overview
        require_supported_native_dates('20080101','20080101')
        observed=weather_rows((folder/'Weather.OUT').read_text())
        input_rows={int(row.split()[0]):list(map(float,row.split()[1:5])) for row in (folder/'CO01.WTH').read_text().splitlines()
            if re.match(r'^\d{7}\s',row)}
        residuals=[]
        for date,row in observed.items():
            expected_values=input_rows[date]
            for key,value in zip(('SRAD','TMXD','TMND','PRED'),expected_values):
                residuals.append(dict(date=date,field=key,difference=row[key]-value))
        bad=[r for r in residuals if abs(r['difference'])>.05001]
        all_weather.append(dict(case=case['name'],days=len(observed),field_comparisons=len(residuals),
            max_residual=max(abs(r['difference']) for r in residuals),mismatches=len(bad)))
        if not case['name'].startswith('aligned_weather'):
            assert any(r['field']=='SRAD' for r in bad)
            negatives.append(dict(case=case['name'],kind='writer_weather_header_column_mismatch',
                native_cycle_completed_but_weather_not_qualified=True,mismatches=len(bad),example=bad[0]));continue
        assert not bad
        assert summary['PDAT']==2008133 and summary['HDAT']==summary['MDAT']
        assert max(observed)==int(summary['HDAT'])<2008333 and len(observed)==int(summary['HDAT'])%1000
        assert summary['HWAH']>0
        sw=run_tables((folder/'SoilWat.OUT').read_text(),expected_runs=(1,))[1]
        ni=run_tables((folder/'SoilNi.OUT').read_text(),expected_runs=(1,))[1]
        assert len(sw)==len(observed)+1 and len(ni)==len(sw)
        assert int(sw[0]['YEAR'])==2007 and int(sw[0]['DOY'])==365 and int(sw[0]['DAS'])==0
        depths=[5,10,15,15,15,30,30,30,30,20]
        water_keys=['SW'+str(i)+'D' for i in range(1,10)]+['SW10']
        water=sum(float(sw[0][key])*depth*10 for key,depth in zip(water_keys,depths))
        assert abs(water-338.2)<1e-8
        assert float(sw[0]['SW9D'])==float(sw[0]['SW10'])==.155
        assert abs(float(ni[0]['NIAD'])-23.683296)<=.05
        assert abs(float(sw[-1]['IRRC'])-459.1)<=.5 and int(sw[-1]['IR#C'])==16
        assert abs(float(ni[-1]['NAPC'])-134.4)<=.5 and int(ni[-1]['NI#M'])==10
        x=(folder/'COGree01.MZX').read_text();expected_irrig=defaultdict(float);expected_fert=defaultdict(float)
        for row in table(x,'@I IDATE'):expected_irrig[2000000+int(row['IDATE'])]+=float(row['IRVAL'])
        for row in table(x,'@F FDATE'):expected_fert[2000000+int(row['FDATE'])]+=float(row['FAMN'])
        for rows,key,expected_events in ((sw,'IRRC',expected_irrig),(ni,'NAPC',expected_fert)):
            actual={}
            for before,after in zip(rows,rows[1:]):
                delta=float(after[key])-float(before[key])
                if delta:actual[int(after['YEAR'])*1000+int(after['DOY'])]=delta
            assert set(actual)==set(expected_events)
            assert all(abs(actual[day]-expected_events[day])<=1.000001 for day in actual)
        warning=(folder/'WARNING.OUT').read_text(encoding='latin-1')
        assert 'from "L" to "C"' in warning and 'Value changed to 1.0' in warning
        accepted.append(dict(case=case['name'],native_coefficients=coefficients,summary=summary,
            weather_days=len(observed),weather_field_comparisons=len(residuals),weather_mismatches=0,
            initial_water_native_mm=water,printed_input_water_mm=337.7,native_water_adjustment_mm=.5,
            initial_inorganic_n_printed_kg_ha=float(ni[0]['NIAD']),
            native_soil_layers=10,source_soil_layers=9,
            initial_stock_row='2007365 DAS0; daily simulation starts2008001',
            irrigation_applications=16,fertilizer_applications=10,native_defaults_retained=True,
            endogenous_maturity_ends_before_package_endat=True,single_completed_cycle=True))
    assert len(accepted)==2 and len(negatives)==4
    for p in source.rglob('*'):
        if p.is_file() and 'source_snapshot' not in p.parts:files[p.relative_to(source).as_posix()]=sha256(p)
    write_json(run/'raw_files_sha256.json',files)
    write_json(run/'weather_comparisons.json',all_weather)
    write_json(run/'verification.json',dict(passed=True,source_run=source.relative_to(ROOT).as_posix(),
        source_report_sha256=sha256(source/'verification.json'),raw_files_pinned=len(files),native_attempts=6,
        input_date_negatives=2,weather_readback_negatives=2,qualified_single_season_cases=2,
        accepted=accepted,negative_controls=negatives,source_045_file_alone_uses_different_048_coefficients=True,
        header_only_correction_resolves_readback_in_tested_scope=True,
        original_field_inputs_unmodified=True,native_input_scope='explicit diagnostic fixture, Jan1 start, header alignment, optional six-coefficient048 transplantation',
        native_defaults=['PHOTO L->C','SLNF1.0','pH7.0','SLU1 6.0','TAV20C','TAMP5C','bottom water raised toLL'],
        passive_driver_stops_after_flag_done=True,research_ready=False,main_training_allowed=False,
        field_validation_ready=False,scope='native readback/calendar/management/termination diagnostics; not independent agronomic or complete N/C validation'))
    print('NATIVE_READBACK_QUALIFIED',flush=True)


if __name__=='__main__':main()
