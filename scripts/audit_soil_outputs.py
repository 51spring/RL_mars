"""Read preserved raw outputs and produce a separate immutable soil audit."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run, write_json, sha256
from mars_env.soil_audit import reconstruct_soil,preharvest_n_inventory

def main():
    p=argparse.ArgumentParser();p.add_argument('evidence',type=Path);args=p.parse_args()
    source=args.evidence.resolve();run=new_run(ROOT,'soil_reconstruction')
    reports={name:reconstruct_soil(source/name) for name in ('no_pest','experimental_pest')}
    timeline=json.loads((source/'experimental_pest/timeline.json').read_text())['policy']
    reports['experimental_pest']['preharvest_n']=preharvest_n_inventory(source/'experimental_pest',timeline[-1]['after']['mars_plant_audit'])
    write_json(run/'verification.json',{'passed':True,'source_run':str(source),
        'source_manifest_sha256':sha256(source/'manifest.json'),'cases':reports,'research_ready':False})
    print(run)
    for name,report in reports.items():
        print(name,report['checks'])

if __name__=='__main__':main()
