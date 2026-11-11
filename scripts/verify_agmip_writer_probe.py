"""Execute published Java writers on isolated source clones, saving every output."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256


def main():
    runtime=ROOT/'outputs/runs/20261106T120134Z_agmip_probe_runtime_6d681648'
    source=ROOT/'outputs/runs/20261106T085314Z_lirf_weather_model_audit_86776d47/decoded_ace.json'
    report=json.loads((runtime/'verification.json').read_text());assert report['passed']
    assert all(sha256(runtime/r['file'])==r['sha256'] for r in report['files'])
    run=new_run(ROOT,'agmip_writer_probe');print(run,flush=True)
    java=shutil.which('java');javac=shutil.which('javac');assert java and javac
    versions={name:subprocess.run([path,'-version'],capture_output=True,text=True,check=True).stderr
        or subprocess.run([path,'-version'],capture_output=True,text=True,check=True).stdout
        for name,path in (('java',java),('javac',javac))}
    helper=ROOT/'scripts/java/AgmipWriterProbe.java'
    shutil.copy2(helper,run/helper.name)
    try:
        for version in ('1.2.18','1.2.21'):
            jars=sorted(p for p in runtime.glob('*.jar') if not p.name.startswith('translator-dssat-')
                or p.name==f'translator-dssat-{version}.jar')
            cp=';'.join(str(p) for p in jars)
            classes=run/f'classes_{version}';classes.mkdir()
            commands=[([javac,'-encoding','UTF-8','-cp',cp,'-d',str(classes),str(helper)],'compile'),
                ([java,'-cp',str(classes)+';'+cp,'AgmipWriterProbe',str(source),str(run/version)],'execute')]
            for command,label in commands:
                result=subprocess.run(command,capture_output=True,text=True,timeout=90)
                (run/f'{version}_{label}.log').write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
                if result.returncode:raise RuntimeError(f'{version} {label} failed, see log')
        write_json(run/'verification.json',dict(passed=True,writer_versions=['1.2.18','1.2.21'],writer_runs=16,
            runtime_evidence=runtime.relative_to(ROOT).as_posix(),runtime_report_sha256=sha256(runtime/'verification.json'),
            source_ace_sha256=sha256(source),caller_sha256=sha256(helper),runtime_versions=versions,
            shared_dependencies_are_historical_exact_build=False,
            scope='actual published Java writer outputs only; output qualification separate; no native DSSAT model',
            native_simulations_executed=0,research_ready=False,main_training_allowed=False))
        print('JAVA_WRITERS_COMPLETED',flush=True)
    except Exception as exc:
        write_json(run/'failure.json',dict(passed=False,error=repr(exc),research_ready=False));raise


if __name__=='__main__':main()
