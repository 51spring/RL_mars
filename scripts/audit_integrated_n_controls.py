"""Apply identical printed precision to old candidate controls; do not relax it."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.integrated_n import analyze_integrated_n


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('evidence',type=Path);args=parser.parse_args()
    source=args.evidence.resolve();index=json.loads((source/'verification.json').read_text());cases=[]
    run=new_run(ROOT,'integrated_n_precision_controls')
    for case in index['cases']:
        folder=source/case['name']/'control'
        d=json.loads((folder/'contract_diagnostics.json').read_text())
        r=analyze_integrated_n(folder,d,json.loads((folder/'trace.json').read_text()))
        cases.append({'name':case['name'],'native_boundary_contract_passed':case['control']['passed'],
            'printed_daily_n_inventory_passed':r['daily_inventory_passed'],
            'final_residual_kg_ha':r['final_residual_kg_ha'],
            'final_roundoff_bound_kg_ha':r['final_roundoff_bound_kg_ha'],
            'max_abs_residual_kg_ha':r['max_abs_residual_kg_ha']})
    write_json(run/'verification.json',{'passed':True,'scope':'precision/sensitivity contrast, not control model validation',
        'source_report_sha256':sha256(source/'verification.json'),'cases':cases,
        'printed_inventory_failed_cases':sum(not c['printed_daily_n_inventory_passed'] for c in cases),
        'native_boundary_failed_cases':sum(not c['native_boundary_contract_passed'] for c in cases),
        'native_boundary_failure_hidden_by_print_precision':[c['name'] for c in cases if not c['native_boundary_contract_passed'] and c['printed_daily_n_inventory_passed']],
        'research_ready':False})
    print(run)
