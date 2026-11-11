"""Acquire public candidate landing pages and one explicit USDA workbook."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import re
import sys
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256


def main():
    run=new_run(ROOT,'field_calibration_candidates');print(run,flush=True)
    urls={
        'nebraska_article.json':'https://api.figshare.com/v2/articles/33116162',
        'nebraska_Manuscript_data.xlsx':'https://ndownloader.figshare.com/files/67135049',
        'waterN_mendeley.html':'https://data.mendeley.com/datasets/6zj7pzftwg/1',
        'kenya_mendeley.html':'https://data.mendeley.com/datasets/tdw54wgvbf/1',
        'lirf_extension_ssrn.html':'https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7552188'}
    def fetch(item):
        name,url=item
        try:
            with urlopen(Request(url,headers={'User-Agent':'MARS-public-candidate-screen/1.0'}),timeout=40) as response:
                data=response.read(32*1024*1024+1);status=response.status
            assert len(data)<=32*1024*1024
            if name.endswith('.xlsx'):assert data.startswith(b'PK')
            if name.endswith('.json'):json.loads(data)
            (run/name).write_bytes(data)
            return dict(file=name,url=url,acquired=True,status=status,bytes=len(data),sha256=sha256(run/name))
        except Exception as exc:return dict(file=name,url=url,acquired=False,error=repr(exc),bypass_attempted=False)
    with ThreadPoolExecutor(max_workers=5) as pool:files=list(pool.map(fetch,urls.items()))
    landing_structures=[]
    for name in ('waterN_mendeley.html','kenya_mendeley.html'):
        p=run/name
        if not p.exists():continue
        html=p.read_text(encoding='utf-8')
        scripts=re.findall(r'<script\b([^>]*)>(.*?)</script>',html,re.S|re.I)
        for index,(attrs,body) in enumerate(scripts):
            if 'json' in attrs.lower() or '__NEXT_DATA__' in attrs:
                try:
                    parsed=json.loads(body);target=run/f'{name}_script{index}.json';write_json(target,parsed)
                    landing_structures.append(dict(file=name,script=index,json_file=target.name,attributes=attrs))
                except ValueError:pass
        (run/(name+'.script_inventory.json')).write_text(json.dumps([dict(attributes=a,body_prefix=b[:180]) for a,b in scripts],indent=2),encoding='utf-8')
    write_json(run/'landing_structures.json',landing_structures)
    passed=any(f['acquired'] and f['file']=='nebraska_Manuscript_data.xlsx' for f in files)
    write_json(run/'verification.json',dict(passed=passed,files=files,new_candidates_not_promoted=True,
        existing_independent_roles_changed=False,research_ready=False,main_training_allowed=False,
        scope='public candidate-file acquisition with individual failures retained; no calibration eligibility inferred'))
    print(json.dumps(dict(files=[{k:v for k,v in f.items() if k in ('file','acquired','error','bytes')} for f in files],structures=landing_structures),indent=2))


if __name__=='__main__':main()
