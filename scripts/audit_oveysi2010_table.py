"""Qualify manually/visually checked factorial means without fitting parameters."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256


if __name__=='__main__':
    table=ROOT/'configs/oveysi2010_table4_grain.json'
    data=json.loads(table.read_text());source=ROOT/data['source_artifact']
    source_record=json.loads((source.parent/'source.json').read_text())
    assert sha256(source)==source_record['sha256']
    rows=data['rows'];expected={(w,f'D{i}') for w in ('W1','W2') for i in range(1,6)}
    assert len(rows)==10 and {(r['water'],r['defoliation']) for r in rows}==expected
    assert not data['standard_errors_available'] and not data['raw_replicates_available']
    assert not data['quantitative_fit_ready']
    checks=[]
    for factor in data['reported_table3_grain_marginals']:
        values=[r['grain_t_ha'] for r in rows if factor in (r['water'],r['defoliation'])]
        mean=sum(values)/len(values);reported=data['reported_table3_grain_marginals'][factor]
        delta=mean-reported
        checks.append({'factor':factor,'cell_average':mean,'reported_marginal':reported,
            'difference_t_ha':delta,'combined_one_decimal_rounding_bound_t_ha':.1,
            'rounding_edge_case':abs(delta)>=.1-1e-12})
    images=[source.parent/f'table_page-{page}.png' for page in (4,5)]
    assert all(p.exists() for p in images)
    run=new_run(ROOT,'public_factorial_means')
    write_json(run/'verification.json',{'passed':True,'scope':'visual transcription and evidence qualification only',
        'source_url':data['source'],'table_sha256':sha256(table),'source_pdf_sha256':sha256(source),
        'rendered_pages':{str(p.relative_to(ROOT)):sha256(p) for p in images},
        'factorial_cells':10,'dry_grain_basis_verified':True,'marginal_audit':checks,
        'rounding_edge_cases_require_review':[r['factor'] for r in checks if r['rounding_edge_case']],
        'uncertainty_identifiable':False,'quantitative_fit_ready':False,
        'study_role':'independent validation candidate; no calibration or tuning',
        'research_ready':False})
    print(run)
