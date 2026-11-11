"""Explain retained boundary failures using independently stored source fields."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.sequence_audit import rounded_balance


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('evidence',type=Path);args=parser.parse_args()
    source=args.evidence.resolve();index=json.loads((source/'verification.json').read_text())
    results=[]
    for case in index['cases']:
        for label in ('native','candidate'):
            p=source/case['name']/label/'scope_diagnostics.json';d=json.loads(p.read_text())
            h=d['harvests'][0];gf,sf=h['grain_fraction'],h['stover_fraction']
            organ_dm_gap=h['stover_dm']+h['pod_dm']-h['canopy_dm']
            grain_dm_gap=h['grain_dm']/gf-h['all_grain_dm']
            predicted_dm=organ_dm_gap*(1-sf)+grain_dm_gap*(gf-sf)
            organ_n_gap=h['stover_n']+h['grain_n']-h['canopy_n']
            predicted_n=organ_n_gap*(1-sf)+h['harvest_grain_n']-h['grain_n']*gf
            if label=='native':predicted_n+=h['dead_leaf_n_raw']*(1-sf)
            actual=d['export_scope']['actual_export_boundary']
            dm=rounded_balance(actual['dm']['residual'],predicted_dm,
                               abs(actual['dm']['actual'])+abs(actual['dm']['expected']))
            n=rounded_balance(actual['n']['residual'],predicted_n,
                              abs(actual['n']['actual'])+abs(actual['n']['expected']))
            assert dm['passed'] and n['passed'],(case['name'],label,'unexplained component')
            results.append({'case':case['name'],'version':label,'artifact_sha256':sha256(p),
                'organ_dm_gap_kg_ha':organ_dm_gap,'grain_basis_dm_gap_kg_ha':grain_dm_gap,
                'prediction_checks':{'dm':dm,'n':n}})
    anchors={'Plant/CERES-Maize/MZ_GROSUB.for':[
        'BIOMAS = (LFWT + STMWT + EARWT)*PLTPOP','PODWT = EARWT*EARS',
        'YIELD = GRNWT*10.0*EARS','GNUP = GRAINN*EARS*10.0'],
        'Plant/CERES-Maize/MZ_PHENOL.for':['EARS = PLTPOP*(GPP/(G2*0.15))**0.33'],
        'Plant/CERES-SharedFiles/HResCeres.for':['GRNWT * PLTPOP * 10.','PODWT - GRNWT * PLTPOP']}
    sources={}
    for relative,patterns in anchors.items():
        p=ROOT/'vendor/dssat-pdi-source'/relative;lines=p.read_text(encoding='latin-1').splitlines()
        locations={s:[i for i,l in enumerate(lines,1) if s in l] for s in patterns}
        assert all(locations.values()),relative
        sources[relative]={'sha256':sha256(p),'lines':locations}
    run=new_run(ROOT,'harvest_scope_source_audit')
    write_json(run/'verification.json',{'passed':True,'source_run':str(source),
        'source_report_sha256':sha256(source/'verification.json'),'cases':results,'source_locations':sources,
        'scope':'source-component explanation, not physical balance closure or direct EARS measurement',
        'empirical_offsets_fitted':False,'research_ready':False})
    print(run)
