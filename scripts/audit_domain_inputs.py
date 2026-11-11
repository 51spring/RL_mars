"""Independently verify loaded native soil/water from preserved output."""
import argparse
import json
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.domain_inputs import verify_effective_layers


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('source',type=Path);args=parser.parse_args()
    source=args.source.resolve();report=json.loads((source/'verification.json').read_text())
    profiles=json.loads((source/'soil_profiles.json').read_text())
    assert report['passed'] and sha256(source/'soil_profiles.json')==report['soil_profile_artifact_sha256']
    run=new_run(ROOT,'domain_effective_inputs');cases=[]
    for case in report['cases']:
        profile=profiles[case['soil_id']]
        for label in ('control','candidate'):
            folder=source/case['name']/label
            diagnostics=json.loads((folder/'contract_diagnostics.json').read_text())
            for filename,digest in diagnostics['files'].items():assert sha256(folder/filename)==digest
            overview=(folder/'OVERVIEW.OUT').read_text(encoding='latin-1')
            loaded=re.findall(r'^ SOIL\s+: (\S+)',overview,re.M)
            assert loaded and set(loaded)=={case['soil_id']},'Native soil ID differs'
            summary=overview.split('*SUMMARY OF SOIL AND GENETIC INPUT PARAMETERS',1)[1].split('SOIL ALBEDO',1)[0]
            layers=[]
            for line in summary.splitlines():
                m=re.match(r'^\s*(\d+)-\s*(\d+)\s+(.+)$',line)
                if m:
                    values=list(map(float,m[3].split()))
                    layers.append(dict(top=int(m[1]),bottom=int(m[2]),SLLL=values[0],
                        SDUL=values[1],SSAT=values[2],SH2O=values[4]))
            verify_effective_layers(profile,layers)
            filex_lines=(folder/'MARS8201.SQX').read_text().splitlines()
            begin=next(i for i,l in enumerate(filex_lines) if l.startswith('@C  ICBL'))
            initial=[]
            for line in filex_lines[begin+1:]:
                if not re.match(r'^\s*1\s+\d+\s+',line):break
                tokens=line.split();initial.append((int(tokens[1]),float(tokens[2])))
            assert [d for d,_ in initial]==[p['SLB'] for p in profile['layers']]
            for layer in layers:
                entered=next(w for d,w in initial if d>=layer['bottom'])
                assert abs(layer['SH2O']-entered)<=.00051,'Actual FileX/native initial water differs'
            warning=(folder/'WARNING.OUT').read_text(encoding='latin-1')
            cases.append({'case':case['name'],'label':label,'native_soil_id':loaded,
                'layer_count':len(layers),'source_layer_count':len(profile['layers']),
                'native_subdivision_permitted_within_source_layers':True,'loaded_soil_and_water_verified':True,
                'actual_filex_initial_water_checked':True,'filex_sha256':sha256(folder/'MARS8201.SQX'),
                'warning_sha256':sha256(folder/'WARNING.OUT'),
                'warnings':{'minimum_organic_carbon_estimated':'minimum value of OC' in warning,
                    'humus_cn_reset_to_10':'C:N ratio of 10.0 will be used' in warning,
                    'surface_mulch_effects_not_modeled':'No mulch effects' in warning}})
    write_json(run/'verification.json',{'passed':True,'source_report':str(source/'verification.json'),
        'source_report_sha256':sha256(source/'verification.json'),'cases':cases,
        'loaded_soil_cases':len(cases),'overview_precision_absolute':.00051,
        'scope':'native effective soil ID, layer water limits and entered initial water; warnings retained',
        'organic_carbon_and_n_initialization_warning_is_not_calibration':True,
        'new_native_runs':0,'independent_agronomic_validation':False,'research_ready':False})
    print(run)
