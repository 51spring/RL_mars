"""Five predeclared passive native probes; never select a field parameter."""
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import psutil
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.lirf_temperature import station_temperature_fixture


def main():
    source=ROOT/'outputs/runs/20261106T133233Z_lirf_native_inputs_574604f1/aligned_weather_048'
    climate_path=ROOT/'outputs/runs/20261106T135234Z_lirf_evidence_ledger_eaaf34b5/temperature_descriptions.json'
    climate=json.loads(climate_path.read_text())
    run=new_run(ROOT,'lirf_temperature');print('RUN_DIR='+str(run),flush=True)
    cases=[dict(name='missing_defaults',tav=None,amp=None),dict(name='explicit_defaults',tav=20.,amp=5.),
        dict(name='period_mean_only',tav=climate['pooled_daily_mean_air_c'],amp=5.),
        dict(name='period_full_range',tav=climate['pooled_daily_mean_air_c'],amp=climate['pooled_full_monthly_range_c']),
        dict(name='period_half_range',tav=climate['pooled_daily_mean_air_c'],amp=climate['pooled_half_monthly_range_c'])]
    write_json(run/'predeclared_plan.json',dict(cases=cases,climate_sha256=sha256(climate_path),
        field_parameter_selection_allowed=False,output_precision_c=.1,station_fixture_decimal_places=2,
        purpose='WTH readback, explicit-vs-default regression and descriptive sensitivity only',
        contrasts=['missing_defaults vs explicit_defaults: exact numeric regression',
            'explicit_defaults vs period_mean_only: TAV sensitivity',
            'period_mean_only vs full/half: AMP sensitivity at fixed TAV'],
        unchanged=['weather daily rows','soil','management','six explicit048 cultivar coefficients','native image'],
        module='METMP D explicitly pinned; omitted original METMP resolves to D in IPSIM',
        stop_rule='five completed cycles or first error; no yield-dependent case selection'))
    binary=Path('/opt/dssat_pdi/mars_actual_harvest_dscsm048')
    assert sha256(binary)==json.loads((source/'effective_inputs.json').read_text())['binary_sha256']
    managed={Path('/opt/dssat_pdi/Genotype/MZCER048.CUL'):source/'effective_MZCER048.CUL',
        Path('/opt/dssat_pdi/Soil/nu.SOL'):source/'nu.SOL',
        Path('/opt/dssat_pdi/Weather/CO01.WTH'):source/'CO01.WTH'}
    prior={p:p.read_bytes() if p.exists() else None for p in managed}
    results=[]
    try:
        for p,s in managed.items():p.write_bytes(s.read_bytes())
        for case in cases:
            folder=run/case['name'];folder.mkdir()
            for name in ('COGree01.MZX','CO01.WTH','nu.SOL','MZCER045.CUL','dssat-pdi.yml'):
                shutil.copy2(source/name,folder/name)
            text=(folder/'COGree01.MZX').read_text();lines=text.splitlines()
            for i,line in enumerate(lines):
                if line.startswith('@N METHODS'):
                    row=lines[i+1];assert not row[85:86].strip()
                    lines[i+1]=row.ljust(85)+'D';lines[i]=line.ljust(81)+'METMP'
                if line.startswith('@N OUTPUTS'):
                    row=lines[i+1];assert row[79:80]=='N'
                    lines[i+1]=row[:79]+'D'+row[80:]
            (folder/'COGree01.MZX').write_text('\n'.join(lines)+'\n')
            if case['tav'] is not None:
                p=folder/'CO01.WTH';p.write_text(station_temperature_fixture(p.read_text(),case['tav'],case['amp']))
            Path('/opt/dssat_pdi/Weather/CO01.WTH').write_bytes((folder/'CO01.WTH').read_bytes())
            write_json(folder/'effective_inputs.json',dict(case=case,binary_sha256=sha256(binary),
                genotype_sha256=sha256(Path('/opt/dssat_pdi/Genotype/MZCER048.CUL')),
                files={n:sha256(folder/n) for n in ('COGree01.MZX','CO01.WTH','nu.SOL','dssat-pdi.yml')},
                METMP='D',VBOSE='D',rl_actions=False))
            with (folder/'native.log').open('w') as log:
                process=subprocess.Popen([str(binary),'C','COGree01.MZX','1'],cwd=folder,
                    env={**os.environ,'GFORTRAN_UNBUFFERED_ALL':'y'},stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                try:process.wait(timeout=45)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid,signal.SIGKILL);process.wait();raise RuntimeError('Native timeout')
            item=dict(name=case['name'],returncode=process.returncode,
                completed=(folder/'native_completed.json').exists(),owned_process_alive=psutil.pid_exists(process.pid),
                soil_temperature_output=(folder/'SoilTemp.OUT').exists())
            write_json(folder/'execution.json',item);results.append(item);print(json.dumps(item),flush=True)
            assert item['returncode']==0 and item['completed'] and not item['owned_process_alive'] and item['soil_temperature_output']
        write_json(run/'raw_files_sha256.json',{str(p.relative_to(run)):sha256(p) for c in cases for p in (run/c['name']).iterdir() if p.is_file()})
        write_json(run/'verification.json',dict(passed=True,native_runs=5,cases=results,
            source_inputs={str(p.relative_to(ROOT)):sha256(p) for p in managed.values()},
            native_parameters_promoted=False,research_ready=False,main_training_allowed=False,
            scope='execution only; independent output qualification required'))
    except Exception as exc:
        write_json(run/'failure.json',dict(passed=False,error=repr(exc),completed_cases=results));raise
    finally:
        for p,data in prior.items():
            if data is None:p.unlink(missing_ok=True)
            else:p.write_bytes(data)


if __name__=='__main__':main()
