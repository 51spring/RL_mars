"""Create reproducible source locations/units without promoting missing C fluxes."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256


if __name__=='__main__':
    catalog=ROOT/'configs/balance_observability.json'
    data=json.loads(catalog.read_text());rows=[]
    for item in data['items']:
        row=dict(item)
        if 'source' in item:
            p=ROOT/'vendor/dssat-pdi-source'/item['source'];text=p.read_text(encoding='latin-1')
            hits=[i for i,l in enumerate(text.splitlines(),1) if item['anchor'] in l]
            if not hits:raise ValueError('Source drift: '+item['id'])
            row.update(source_sha256=sha256(p),source_lines=hits)
        rows.append(row)
    run=new_run(ROOT,'balance_observability')
    write_json(run/'verification.json',{'passed':True,'scope':'source/units/measurement catalog only',
        'catalog_sha256':sha256(catalog),'items':rows,
        'unobserved':[r['id'] for r in rows if r['status']=='not_separately_observed'],
        'whole_elemental_carbon_verified':False,'whole_crop_soil_n_verified':False,'research_ready':False})
    print(run)
