"""Acquire explicitly linked public references; retain failed access, no bypass."""
from concurrent.futures import ThreadPoolExecutor
import json
from html import unescape
from pathlib import Path
import re
import sys
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256

def main():
    run=new_run(ROOT,'nebraska_reference_sources');print(run,flush=True)
    urls={
        'Schmer2020.pdf':'https://digitalcommons.unl.edu/cgi/viewcontent.cgi?article=2414&context=agronomyfacpub',
        'Sindelar2019a.pdf':'https://digitalcommons.unl.edu/cgi/viewcontent.cgi?article=2280&context=agronomyfacpub',
        'schmer_landing.html':'https://digitalcommons.unl.edu/agronomyfacpub/1425/',
        'sindelar_landing.html':'https://digitalcommons.unl.edu/agronomyfacpub/1286/',
        'li_landing.html':'https://digitalcommons.unl.edu/usdaarsfacpub/2628/',
        'schmer_ars.html':'https://www.ars.usda.gov/research/publications/publication/?seqNo115=368850',
        'sindelar_ars.html':'https://www.ars.usda.gov/research/publications/publication/?seqNo115=354236'}
    def fetch(item):
        name,url=item
        try:
            with urlopen(Request(url,headers={'User-Agent':'MARS-public-source-audit/1.0'}),timeout=40) as response:
                data=response.read(24*1024*1024+1);status=response.status;content_type=response.headers.get('Content-Type')
            assert len(data)<=24*1024*1024
            is_pdf=data.startswith(b'%PDF')
            if name.endswith('.pdf') and not is_pdf:
                target=run/(name+'.nonpdf_response.html');target.write_bytes(data)
                return dict(file=target.name,url=url,status=status,content_type=content_type,pdf_acquired=False,
                    response_saved=True,sha256=sha256(target),bytes=len(data),bypass_attempted=False)
            target=run/name;target.write_bytes(data)
            return dict(file=name,url=url,status=status,content_type=content_type,pdf_acquired=is_pdf,
                response_saved=True,sha256=sha256(target),bytes=len(data),bypass_attempted=False)
        except Exception as exc:return dict(file=name,url=url,response_saved=False,pdf_acquired=False,error=repr(exc),bypass_attempted=False)
    with ThreadPoolExecutor(max_workers=4) as pool:files=list(pool.map(fetch,urls.items()))
    links=[]
    for name in ('schmer_landing.html','sindelar_landing.html','li_landing.html'):
        p=run/name
        if not p.exists():continue
        html=p.read_text(encoding='utf-8')
        links.extend(dict(source=name,url=unescape(u)) for u in re.findall(r'(?:href|content)=[\"\x27]([^\"\x27]+)',html)
            if u.startswith(('https://','http://','/')) and any(s in u.lower() for s in ('viewcontent','supp','additional','download','arsuserfiles')))
    write_json(run/'linked_resources.json',links)
    write_json(run/'verification.json',dict(passed=True,scope='bounded public acquisition audit; failures and non-PDF responses retained',
        files=files,actual_reference_pdfs=sum(f['pdf_acquired'] for f in files),
        supplementary_file_acquired=False,research_ready=False,main_training_allowed=False))
    print(json.dumps(files,indent=2))

if __name__=='__main__':main()
