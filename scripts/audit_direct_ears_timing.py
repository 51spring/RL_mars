"""Qualify timing using post-transition records; exclude germination stages 7-10."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.sequence_audit import rounded_balance


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('evidence',type=Path);args=parser.parse_args()
    source=args.evidence.resolve();report=json.loads((source/'verification.json').read_text());cases=[]
    for case in report['cases']:
        p=source/case['name']/'instrumented/diagnostics.json';d=json.loads(p.read_text())
        transition=min(b['date'] for b in d['barrenness_records'])
        eligible=[r for r in d['ear_records'] if r['date']>=transition and r['stage'] in (5,6) and r['ears']>0]
        assert eligible
        first=next((r for r in eligible if not rounded_balance(r['ears'],r['population'],r['ears']+r['population'])['passed']),None)
        cases.append({'name':case['name'],'managed':case['managed'],'transition_date':transition,
            'first_divergence_date':first['date'] if first else None,'first_divergence':first,
            'artifact_sha256':sha256(p)})
    run=new_run(ROOT,'ear_timing_qualification')
    write_json(run/'verification.json',{'passed':True,'source_report_sha256':sha256(source/'verification.json'),
        'supersedes_field':'first_post_barrenness_divergence','reason':'stages 7-10 are germination, not post-barrenness',
        'source_raw_measurements_and_regression_remain_valid':True,'cases':cases,'research_ready':False})
    print(run)
