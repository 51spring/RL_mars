"""Passive-PDI native input probes in a disposable root-owned container."""
import json
import os
import re
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import psutil
from jinja2 import Template
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.ear_diagnostics import EarProtocol
from mars_env.dssat_backend import terminal_template
from mars_env.lirf_native_compat import align_y4k_weather_header,require_supported_native_dates


def main():
    source=ROOT/'outputs/runs/20261106T131246Z_lirf_dome_boundary_8e93a2f4'
    assert json.loads((source/'verification.json').read_text())['passed']
    index=json.loads((source/'files_sha256.json').read_text())
    assert all(sha256(source/name)==h for name,h in index.items())
    global ACTIVE_RUN
    run=new_run(ROOT,'lirf_native_inputs');ACTIVE_RUN=run;print('RUN_DIR='+str(run),flush=True)
    binary=Path('/opt/dssat_pdi/mars_actual_harvest_dscsm048')
    genotype=Path('/opt/dssat_pdi/Genotype/MZCER048.CUL')
    original=genotype.read_bytes();(run/'original_MZCER048.CUL').write_bytes(original)
    oldrow=next(line for line in original.decode('latin-1').splitlines() if line.startswith('IB1068 '))
    packaged=next(line for line in (source/'writer_output/MZCER045.CUL').read_text(encoding='latin-1').splitlines() if line.startswith('IB1068 '))
    values=[float(packaged[36+i*6:42+i*6]) for i in range(6)]
    assert values==[245.6,.156,704.4,994.,6.239,52.88]
    newrow=oldrow[:36]+''.join(f'{value:6.3f}' if i in (1,4) else f'{value:6.2f}' if i==5 else f'{value:6.1f}' for i,value in enumerate(values))
    # Local fixture files in both cwd and configured simulator search locations.
    soil_path=Path('/opt/dssat_pdi/Soil/nu.SOL');weather_path=Path('/opt/dssat_pdi/Weather/CO01.WTH')
    prior={p:p.read_bytes() if p.exists() else None for p in (soil_path,weather_path)}
    soil_path.write_bytes((source/'writer_output/nu.SOL').read_bytes())
    weather_path.write_bytes((source/'writer_output/CO01.WTH').read_bytes())
    template=(ROOT/'vendor/gym_dssat_pdi/gym-dssat-pdi/gym_dssat_pdi/envs/configs/maize/dssat_pdi.jinja2').read_text()
    template=EarProtocol().patch_template(terminal_template(template))
    # This PDI build deliberately restarts after flag_done. End the owned
    # diagnostic process at that completed-cycle event, before flag_undone.
    passive=Template(template.split('plugins:',1)[0]).render()+'''\nplugins:
  pycall:
    on_event:
      flag_done:
        exec: |
          import json, os
          with open('native_completed.json', 'w') as completed:
              json.dump({'native_cycle_complete': True, 'event': 'flag_done'}, completed)
          os._exit(0)
'''
    cases=[]
    try:
        for label,compat,jan1,header in (('legacy_file_only',False,False,False),('explicit_048_coefficients',True,False,False),
            ('jan1_legacy_file_only',False,True,False),('jan1_explicit_048_coefficients',True,True,False),
            ('aligned_weather_legacy',False,True,True),('aligned_weather_048',True,True,True)):
            folder=run/label;folder.mkdir()
            for path in (source/'writer_output').iterdir():shutil.copy2(path,folder/path.name)
            filex=folder/'COGree01.MZX';lines=filex.read_text().splitlines()
            for i,line in enumerate(lines):
                if line.startswith('@N OUTPUTS'):
                    row=lines[i+1]
                    for key in ('WAOUT','NIOUT','MIOUT'):
                        spans=list(re.finditer(r'\S+',row));span=spans[line.split().index(key)]
                        row=row[:span.start()]+'Y'+row[span.end():]
                    lines[i+1]=row;break
            filex.write_text('\n'.join(lines)+'\n')
            if jan1:
                require_supported_native_dates('20080101','20080101')
                filex=folder/'COGree01.MZX';text=filex.read_text()
                assert text.count('S 08103  2150')==1
                filex.write_text(text.replace('S 08103  2150','S 08001  2150'))
            if header:
                weather=folder/'CO01.WTH';weather.write_text(align_y4k_weather_header(weather.read_text()))
            weather_path.write_bytes((folder/'CO01.WTH').read_bytes())
            (folder/'dssat-pdi.yml').write_text(passive)
            if compat:
                changed=original.decode('latin-1').replace(oldrow,newrow)
                genotype.write_text(changed,encoding='latin-1')
            else:genotype.write_bytes(original)
            (folder/'effective_MZCER048.CUL').write_bytes(genotype.read_bytes())
            write_json(folder/'effective_inputs.json',dict(binary_sha256=sha256(binary),
                genotype_sha256=sha256(genotype),native_048_row=newrow if compat else oldrow,
                package_045_row=packaged,coefficients_048_injected=compat,
                six_coefficient_reader_source='vendor/dssat-pdi-source/InputModule/IPVAR.for MZCER case',
                native_genotype_search_path=str(genotype),unmapped_package_trailing_values=packaged[72:].strip(),
                simulation_start_change='20080412 -> 20080101; preserve source initial date' if jan1 else None,
                weather_header_alignment_only=header,
                passive_pdi=True,rl_actions=False,source_fixture=source.relative_to(ROOT).as_posix()))
            env={**os.environ,'GFORTRAN_UNBUFFERED_ALL':'y'}
            timed_out=False;owned=[]
            with (folder/'native.log').open('w') as log:
                process=subprocess.Popen([str(binary),'C','COGree01.MZX','1'],cwd=folder,env=env,
                    stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                try:
                    try:owned=[psutil.Process(process.pid)]
                    except psutil.NoSuchProcess:pass
                    process.wait(timeout=45)
                except subprocess.TimeoutExpired:
                    timed_out=True;os.killpg(process.pid,signal.SIGKILL);process.wait()
            alive=[]
            for p in owned:
                if p.is_running():alive.append(p.pid)
            item=dict(name=label,returncode=process.returncode,timed_out=timed_out,
                owned_alive_after_wait=alive,summary_exists=(folder/'Summary.OUT').exists(),
                overview_exists=(folder/'OVERVIEW.OUT').exists(),
                expected_returncode=0 if jan1 else 99,
                completed_cycle_marker=(folder/'native_completed.json').exists())
            write_json(folder/'execution.json',item);cases.append(item);print(json.dumps(item),flush=True)
        passed=all(not c['timed_out'] and not c['owned_alive_after_wait']
            and c['returncode']==c['expected_returncode']
            and (c['expected_returncode']!=0 or c['completed_cycle_marker']) for c in cases)
        write_json(run/'verification.json',dict(passed=passed,
            scope='native diagnostic attempts completed and retained; scientific/input acceptance qualification separate',
            native_runs=len(cases),cases=cases,source_report_sha256=sha256(source/'verification.json'),
            diagnostics_output_flags_enabled=['WAOUT','NIOUT','MIOUT'],
            binary_sha256=sha256(binary),research_ready=False,main_training_allowed=False,native_ready=False))
        if not passed:raise RuntimeError('Native diagnostic outcome differed; retained outputs require qualification')
    except Exception as exc:
        write_json(run/'failure.json',dict(passed=False,error=repr(exc),completed_cases=cases,research_ready=False));raise
    finally:
        genotype.write_bytes(original)
        for path,data in prior.items():
            if data is not None:path.write_bytes(data)
            elif path.exists():path.unlink()


if __name__=='__main__':
    try:main()
    except Exception as exc:
        if 'ACTIVE_RUN' in globals() and not (ACTIVE_RUN/'failure.json').exists():
            write_json(ACTIVE_RUN/'failure.json',dict(passed=False,error=repr(exc),research_ready=False))
        raise
