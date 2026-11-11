"""Real seven-rule DOME execution, guarded diagnostic clone, Java writer export."""
from copy import deepcopy
import csv
import json
from pathlib import Path
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.lirf_export_guard import validate_export,require_export,UNITS
from qualify_agmip_writer_outputs import table


def main():
    runtime=ROOT/'outputs/runs/20261106T120134Z_agmip_probe_runtime_6d681648'
    dome_runtime=ROOT/'outputs/runs/20261106T130416Z_dome_runtime_d5eb61cc'
    source=ROOT/'outputs/runs/20261106T085314Z_lirf_weather_model_audit_86776d47'
    cultivar_path=source/'MZCER045.CUL'
    for folder in (runtime,dome_runtime):
        metadata=json.loads((folder/'verification.json').read_text());assert metadata['passed']
        assert all(sha256(folder/f['file'])==f['sha256'] for f in metadata['files'])
    source_index=json.loads((source/'derived_files_sha256.json').read_text())
    assert all(sha256(source/p)==h for p,h in source_index.items())
    global ACTIVE_RUN
    run=new_run(ROOT,'lirf_dome_boundary');ACTIVE_RUN=run;print(run,flush=True)
    jars=sorted(p for p in runtime.glob('*.jar') if not p.name.startswith('translator-dssat-') or p.name=='translator-dssat-1.2.21.jar')
    jars.append(dome_runtime/'dome-1.4.15.jar');cp=';'.join(str(p) for p in jars)
    helper=ROOT/'scripts/java/DomeInputProbe.java';classes=run/'classes';classes.mkdir()
    shutil.copy2(helper,run/helper.name)
    def command(args,label):
        result=subprocess.run(args,capture_output=True,text=True,timeout=90)
        (run/(label+'.log')).write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
        if result.returncode:raise RuntimeError(label+' failed; see log')
    command([shutil.which('javac'),'-encoding','UTF-8','-cp',cp,'-d',str(classes),str(helper)],'compile')
    java=[shutil.which('java'),'-cp',str(classes)+';'+cp,'DomeInputProbe']
    command(java+['prepare',str(source/'decoded_ace.json'),str(source/'decoded_dome.json'),str(run/'prepared')],'dome_prepare')
    rules=json.loads((run/'prepared/rules.json').read_text())
    generators=json.loads((run/'prepared/generators.json').read_text())
    existing=json.loads((run/'prepared/existing_values.json').read_text())
    missing_endat=json.loads((run/'prepared/missing_endat.json').read_text())
    assert missing_endat['endat']=='20081128'
    linkage_path=ROOT/'outputs/runs/20261106T084700Z_lirf_model_package_f84234e1/package/Greeley CO LIRF Means/Linkage-Machakos-MAZ-0XFX.alnk'
    with linkage_path.open(newline='') as stream:
        linkage=next(row for row in csv.reader(stream) if row and row[0]=='*')
    engine_name=json.loads((run/'prepared/engine_name.json').read_text())
    write_json(run/'linkage_qualification.json',dict(source_sha256=sha256(linkage_path),
        linkage_exname=linkage[1],experiment_exname=rules['exname'],
        exact_experiment_name_match=linkage[1]==rules['exname'],
        linkage_dome_name=linkage[2],selected_engine_name=engine_name,
        dome_name_matches_ignoring_case=linkage[2].casefold()==engine_name.casefold(),
        automatic_link_resolution_performed=False,selection='explicit single package DOME selected for diagnostics'))
    # Metadata annotations can differ by API route; inspect core values directly.
    for e in (rules,generators):
        assert e['sdat']=='20080412' and e['endat']=='20081128'
        assert {k:e['soil'][k] for k in ('sldr','slro','slpf','salb')}==dict(sldr='0.5',slro='60',slpf='0.95',salb='0.13')
        assert all(event['fedep']=='5' for event in e['management']['events'] if event['event']=='fertilizer')
    assert existing['sdat']=='20080101' and existing['soil']['slpf']=='0.77'
    assert next(e for e in existing['management']['events'] if e['event']=='fertilizer')['fedep']=='9'
    cultivar=cultivar_path.read_text(encoding='latin-1')
    blocked=validate_export(rules,UNITS,cultivar,purpose='package_diagnostic',writer_version='1.2.21')
    assert len(blocked)==9 and all('texture must sum' in e for e in blocked)
    write_json(run/'original_export_blocked.json',dict(blocked=True,errors=blocked,writer_invoked=False))
    fixture=deepcopy(rules);ledger=[]
    # Explicit integration fixture only, not automatic correction of field data.
    for i,layer in enumerate(fixture['soil']['soilLayer']):
        for key in ('slcly','slsnd','slsil'):
            old=layer[key];new=str(float(old)*100);layer[key]=new
            ledger.append(dict(path=f'soil.soilLayer[{i}].{key}',before=old,after=new,
                reason='explicit_percent_texture_integration_fixture; not field-validated'))
    args=dict(purpose='package_diagnostic',writer_version='1.2.21')
    require_export(fixture,UNITS,cultivar,**args)
    write_json(run/'diagnostic_assumptions.json',dict(texture_fixture_changes=ledger,
        unused_invalid_slfc1_preserved=True,field_texture_intent_verified=False,
        explicit_single_dome_selection=True,automatic_linkage_file_resolution_verified=False,
        initial_date_vs_simulation_start_qualification='Jan1 initial state with Apr12 simulation start retained; not validated temporal initialization'))
    write_json(run/'diagnostic_fixture.json',fixture)
    negatives=[]
    for name in ('pldp_missing','pldp_minus99','pldp_nan','unit_unknown','no3_missing','no3_minus99','dul_missing',
                 'texture_fraction','cultivar_missing','soil_link_mismatch','weather_link_mismatch','field_validation_purpose'):
        candidate=deepcopy(fixture);units=deepcopy(UNITS);call_args=args.copy();cul=cultivar
        planting=next(e for e in candidate['management']['events'] if e['event']=='planting')
        if name=='pldp_missing':planting.pop('pldp')
        elif name=='pldp_minus99':planting['pldp']='-99'
        elif name=='pldp_nan':planting['pldp']='NaN'
        elif name=='unit_unknown':units['pldp']='unknown'
        elif name=='no3_missing':candidate['initial_conditions']['soilLayer'][0].pop('icno3')
        elif name=='no3_minus99':candidate['initial_conditions']['soilLayer'][0]['icno3']='-99'
        elif name=='dul_missing':candidate['soil']['soilLayer'][0].pop('sldul')
        elif name=='texture_fraction':candidate['soil']['soilLayer'][0]['slcly']='.05'
        elif name=='cultivar_missing':cul=''
        elif name=='soil_link_mismatch':candidate['sid']='wrong'
        elif name=='weather_link_mismatch':candidate['wid']='wrong'
        elif name=='field_validation_purpose':call_args['purpose']='field_validation'
        errors=validate_export(candidate,units,cul,**call_args);assert errors,name
        try:require_export(candidate,units,cul,**call_args)
        except ValueError:pass
        else:raise RuntimeError('Invalid input reached executable gate: '+name)
        negatives.append(dict(name=name,blocked=True,errors=errors,writer_invoked=False))
    write_json(run/'negative_controls.json',negatives)
    # Only the validated, labeled fixture crosses the real writer boundary.
    require_export(json.loads((run/'diagnostic_fixture.json').read_text()),UNITS,cultivar,**args)
    command(java+['export',str(run/'diagnostic_fixture.json'),str(run/'writer_output')],'writer_export')
    out=run/'writer_output';soil=next(out.glob('*.SOL'));filex=next(out.glob('*.MZX'))
    text=filex.read_text();surface=table(soil.read_text(),'@ SCOM')[0]
    assert float(table(text,'@P PDATE')[0]['PLDP'])==5
    assert float(surface['SLPF'])==.95 and float(surface['SLDR'])==.5 and float(surface['SLRO'])==60
    assert all(float(row['FDEP'])==5 for row in table(text,'@F FDATE'))
    # General control has a free-text SNAME field: parse only its numeric prefix.
    general=text.split('@N GENERAL',1)[1].splitlines()[1].split()
    assert general[:2]==['1','GE'] and general[5]=='08103'
    assert float(table(soil.read_text(),'@  SLB')[0]['SLCL'])==5
    shutil.copy2(cultivar_path,out/'MZCER045.CUL')
    weather_files=list(out.glob('*.WTH'));assert len(weather_files)==1
    weather_rows=table(weather_files[0].read_text(),'@DATE')
    assert len(weather_rows)==366
    assert weather_rows[0]['factor']=='2008001' and weather_rows[-1]['factor']=='2008366'
    assert sha256(source/'decoded_ace.json')==source_index['decoded_ace.json']
    write_json(run/'verification.json',dict(passed=True,dome_version='1.4.15',writer_version='1.2.21',
        dome_rules=7,dome_cases=4,rule_route_and_generator_route_values_match=True,fill_preserves_existing_values=True,
        missing_endat_offset200_days_verified=True,
        original_texture_input_blocked=True,negative_controls_rejected=len(negatives),
        explicit_fixture_changes=len(ledger),writer_output_validated=True,
        source_files_unchanged=True,cultivar_coefficients_copied_unchanged=True,
        weather_days_written=366,
        historical_exact_pipeline_verified=False,automatic_linkage_resolution_verified=False,
        native_simulations_executed=0,native_ready=False,research_ready=False,main_training_allowed=False,
        pending=['native cultivar045/048 compatibility','native accepted-input/termination checks',
            'initial-date/start-date semantics','field cultivar/texture/weather/N/irrigation discrepancies'],
        scope='real package DOME rules and guarded explicit diagnostic writer fixture, not field validation',
        evidence={str((p/'verification.json').relative_to(ROOT)):sha256(p/'verification.json') for p in (runtime,dome_runtime,source)}))
    write_json(run/'files_sha256.json',{p.relative_to(run).as_posix():sha256(p) for p in run.rglob('*')
        if p.is_file() and 'source_snapshot' not in p.parts})
    print('DOME_AND_EXPORT_BOUNDARY_PASSED',flush=True)


if __name__=='__main__':
    try:main()
    except Exception as exc:
        if 'ACTIVE_RUN' in globals():write_json(ACTIVE_RUN/'failure.json',dict(passed=False,error=repr(exc),research_ready=False))
        raise
