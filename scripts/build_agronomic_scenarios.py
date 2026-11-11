"""Versioned public study targets, descriptive contrasts and blocked execution."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.agronomic_scenarios import build_registry,readiness,source_contrasts


if __name__=='__main__':
    registry=build_registry(ROOT);contrasts=source_contrasts(registry)
    run=new_run(ROOT,'agronomic_scenarios');print(run)
    write_json(run/'scenarios.json',registry);write_json(run/'observed_contrasts.json',contrasts)
    assessment=[dict(scenario_id=r['scenario_id'],**readiness(r)) for r in registry]
    write_json(run/'readiness_by_scenario.json',assessment)
    protocols=json.loads((ROOT/'configs/agronomic_protocols.json').read_text())
    source_folder=ROOT/protocols['source_run']
    source_metadata=json.loads((source_folder/'sources.json').read_text())
    for name,info in source_metadata.items():
        if 'sha256' in info:assert sha256(source_folder/name)==info['sha256']
    write_json(run/'verification.json',{'passed':True,'scope':'public protocol translation and blocked validation gates; no native simulation or parameter tuning',
        'scenario_count':len(registry),'descriptive_contrasts':len(contrasts),
        'studies':{k:sum(r['study_id']==k for r in registry) for k in protocols['studies']},
        'quantitative_validation_ready':sum(a['ready_for_quantitative_validation'] for a in assessment),
        'calibration_allowed':sum(a['calibration_allowed'] for a in assessment),
        'source_assets':source_metadata,'source_metadata_sha256':sha256(source_folder/'sources.json'),
        'visually_checked_santos_pages':{name:sha256(source_folder/name) for name in ('santos_page-2.png','santos_page-3.png')},
        'protocols_sha256':sha256(ROOT/'configs/agronomic_protocols.json'),
        'new_native_runs':0,'parameters_fitted':False,'independent_agronomic_validation':False,'research_ready':False})
