"""Check actual published Java outputs against source-only assumptions."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.lirf_input_audit import initial_inventory


def table(text,marker):
    lines=text.splitlines();idx=next(i for i,line in enumerate(lines) if line.startswith(marker))
    header=lines[idx].split();keys=header[1:] if header[0]=='@' else ['factor']+header[1:]
    rows=[]
    for line in lines[idx+1:]:
        if not line.strip() or line.startswith(('@','*','!')):break
        values=line.split();assert len(values)==len(keys),(marker,values,keys)
        rows.append(dict(zip(keys,values)))
    assert rows;return rows


def normalized(text):
    return '\n'.join(line for line in text.splitlines() if not line.startswith('!This soil file is created by'))


def main():
    source=ROOT/'outputs/runs/20261106T115915Z_agmip_translator_sources_efefb662'
    probe=ROOT/'outputs/runs/20261106T120239Z_agmip_writer_probe_d5efe8e9'
    ace_source=ROOT/'outputs/runs/20261106T085314Z_lirf_weather_model_audit_86776d47/decoded_ace.json'
    report=json.loads((probe/'verification.json').read_text());assert report['passed']
    assert sha256(ace_source)==report['source_ace_sha256']
    snapshots=json.loads((source/'verification.json').read_text());assert snapshots['passed']
    run=new_run(ROOT,'agmip_writer_qualification');print(run,flush=True)
    results=[];index={};source_checks=[]
    for snapshot in snapshots['snapshots']:
        label=snapshot['label'];folder=source/label/'source'
        assert all(sha256(folder/name)==digest for name,digest in snapshot['files'].items())
        package=folder/'src/main/java/org/agmip/translators/dssat'
        soil=(package/'DssatSoilOutput.java').read_text(encoding='utf-8')
        x=(package/'DssatXFileOutput.java').read_text(encoding='utf-8')
        assert '"slfc1"' not in soil and '"slsnd"' not in soil
        assert 'formatNumStr(5, soilRecord, "slcly", defValR)' in soil
        assert 'pldpBD.divide(new BigDecimal("10"))' in x
        source_checks.append(dict(label=label,revision=snapshot['revision'],
            soil_writer_sha256=sha256(package/'DssatSoilOutput.java'),
            x_writer_sha256=sha256(package/'DssatXFileOutput.java'),
            pldp_divided_by10=True,slfc1_not_written=True,sand_not_written=True,
            clay_silt_no_explicit_rescaling_in_output_expression=True,
            package_exporter_identity_verified=False))
    ace=json.loads(ace_source.read_text());raw=initial_inventory(ace['soils'][0]['soilLayer'],ace['experiments'][0]['initial_conditions']['soilLayer'])
    for version in ('1.2.18','1.2.21'):
        folder=probe/version;outputs={}
        for case in sorted(folder.iterdir()):
            if not case.is_dir():continue
            files=list(case.iterdir());assert len(files)==2
            soil_file=next(p for p in files if p.suffix=='.SOL')
            x_file=next(p for p in files if p.suffix=='.MZX')
            soil=soil_file.read_text();x=x_file.read_text()
            outputs[case.name]=dict(soil=soil,x=x,
                soil_rows=table(soil,'@  SLB'),planting=table(x,'@P PDATE')[0],
                initial=table(x,'@C  ICBL'),surface=table(soil,'@ SCOM')[0])
            for p in files:index[p.relative_to(probe).as_posix()]=sha256(p)
        original=outputs['original']
        assert float(original['planting']['PLDP'])==5
        assert float(original['soil_rows'][0]['SLCL'])==.05
        assert float(original['soil_rows'][0]['SLSI'])==.1
        assert original['surface']['SLPF']=='-99'
        for label in ('slfc1_corrected_probe','slfc1_removed_probe'):
            assert normalized(outputs[label]['soil'])==normalized(original['soil'])
            assert normalized(outputs[label]['x'])==normalized(original['x'])
        assert float(outputs['texture_times100_probe']['soil_rows'][0]['SLCL'])==5
        assert float(outputs['texture_times100_probe']['soil_rows'][0]['SLSI'])==10
        assert outputs['missing_pldp']['planting']['PLDP']=='-99'
        assert float(outputs['sentinel_pldp']['planting']['PLDP'])==-9.9
        assert outputs['missing_initial_no3']['initial'][0]['SNO3']=='-99'
        assert outputs['missing_dul']['soil_rows'][0]['SDUL']=='-99'
        printed_soil=[dict(sllb=s['SLB'],slbdm=s['SBDM']) for s in original['soil_rows']]
        printed_initial=[dict(icbl=s['ICBL'],ich2o=s['SH2O'],icnh4=s['SNH4'],icno3=s['SNO3']) for s in original['initial']]
        printed=initial_inventory(printed_soil,printed_initial)
        results.append(dict(version=version,diagnostic_cases=8,soil_layers_written=len(printed_soil),initial_layers_written=len(printed_initial),
            pldp_mm50_written_as_cm5=True,explicit_missing_pldp_minus99_written_as_minus9_9=True,
            absent_pldp_initial_no3_and_dul_written_as_minus99=True,
            slfc1_perturbations_have_no_effect_on_both_output_files=True,
            fraction_texture_not_rescaled=True,raw_soil_surface_slpf_written_as_minus99=True,
            dome_rules_applied_by_probe=False,raw_initial_water_mm=raw['water_mm'],
            printed_initial_water_mm=printed['water_mm'],water_rounding_difference_mm=printed['water_mm']-raw['water_mm'],
            printed_initial_mineral_n_kg_ha=printed['mineral_n_kg_ha']))
    assert len(index)==32
    write_json(run/'output_files_sha256.json',index)
    write_json(run/'verification.json',dict(passed=True,probe_evidence=probe.relative_to(ROOT).as_posix(),
        probe_report_sha256=sha256(probe/'verification.json'),source_evidence=source.relative_to(ROOT).as_posix(),
        writer_versions=['1.2.18','1.2.21'],diagnostic_cases=16,output_files=32,source_checks=source_checks,cases=results,
        source_field_slfc1_invalid_but_unused_in_pinned_soil_writers=True,
        effective_texture_units_still_unresolved=True,
        full_ace_dome_pipeline_or_historical_exact_build_verified=False,
        automatically_corrected_source_or_promoted_research_inputs=False,
        native_simulations_executed=0,research_ready=False,main_training_allowed=False,
        scope='real Java writer output and source rules; not native model or field validation'))
    print(json.dumps(results,indent=2))


if __name__=='__main__':main()
