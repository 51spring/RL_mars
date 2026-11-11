"""Audit preserved real v2 crop/fallow outputs, retaining every failed day."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.integrated_n import analyze_integrated_n


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('evidence',type=Path);args=parser.parse_args()
    source=args.evidence.resolve();index=json.loads((source/'verification.json').read_text())
    source_manifest=json.loads((source/'manifest.json').read_text())
    assert index['passed'] and index['contract_version']=='standing_stock_actual_yield_v2'
    run=new_run(ROOT,'integrated_crop_soil_n');print(run,flush=True);cases=[]
    (run/'source_native_config.yaml').write_bytes((source/'config.yaml').read_bytes())
    (run/'source_native_manifest.json').write_bytes((source/'manifest.json').read_bytes())
    for case in index['cases']:
        folder=source/case['name']/'candidate'
        diagnostics=json.loads((folder/'contract_diagnostics.json').read_text())
        trace=json.loads((folder/'trace.json').read_text())
        for filename,digest in diagnostics['files'].items():assert sha256(folder/filename)==digest
        try:
            result=analyze_integrated_n(folder,diagnostics,trace)
        except Exception as exc:
            write_json(run/'failure.json',{'passed':False,'case':case['name'],'exception':repr(exc),'source':str(source),'research_ready':False})
            raise
        write_json(run/(case['name']+'.json'),result)
        summary={k:v for k,v in result.items() if k!='rows'}
        summary.update(name=case['name'],seed=case['seed'],managed=case['managed'],mode=case['mode'],
            source_diagnostics_sha256=sha256(folder/'contract_diagnostics.json'),
            source_tables_sha256={name:sha256(folder/name) for name in ('SoilNoBal.OUT','SoilNiBal.OUT','MgmtEvent.OUT')})
        cases.append(summary);print(case['name']+' inventory='+str(result['daily_inventory_passed']),flush=True)
    passed=all(c['combined_model_n_evidence_passed'] and c['fallow_initial_inventory_passed'] and c['final_inventory_passed'] for c in cases)
    locations={}
    anchors={'Soil/Inorganic_N/SOILNI.for':["!       Update with yesterday's plant N uptake",'SNO3(L) = SNO3(L) - UNO3(L)','SNH4(L) = SNH4(L) - UNH4(L)'],
        'Soil/CERES_OrganicMatter/SoilOrg.for':['SenE   = SENESCE % ResE','DltFON(L) = DltFON(L) + SenE(L,N)'],
        'Soil/Inorganic_N/SoilNiBal.for':['WTNUPTODAY = (WTNUP - WTNUPY) * 10.']}
    for relative,patterns in anchors.items():
        p=ROOT/'vendor/dssat-pdi-source'/relative;lines=p.read_text(encoding='latin-1').splitlines()
        hits={s:[i for i,l in enumerate(lines,1) if s in l] for s in patterns}
        assert all(hits.values()),relative
        locations[relative]={'sha256':sha256(p),'source_lines':hits}
    write_json(run/'verification.json',{'passed':passed,'cases':cases,'case_count':len(cases),
        'source_run':str(source),'source_report_sha256':sha256(source/'verification.json'),
        'source_image_id':source_manifest['image_id'],'source_config_sha256':sha256(source/'config.yaml'),
        'source_manifest_sha256':sha256(source/'manifest.json'),
        'scope':'daily modeled crop+soil N, pending uptake/root transfers, harvest and fallow; same v2 allocation',
        'new_native_runs':0,'all_failures_retained':True,'postharvest_modeled_n_inventory_verified':passed,
        'native_boundary_and_daily_inventory_both_required':True,'source_timing_evidence':locations,
        'whole_elemental_carbon_verified':False,'independent_agronomic_validation':False,'research_ready':False})
    print('ALL_DAILY_N_INVENTORIES='+str(passed),flush=True)
