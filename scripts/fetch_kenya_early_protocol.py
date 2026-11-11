"""Fetch the explicitly linked public PDF of an early planting-date record."""
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.parse import urljoin
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256

class Links(HTMLParser):
    def __init__(self):super().__init__();self.pdf=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='link' and a.get('rel')=='item' and a.get('type')=='application/pdf':self.pdf.append(a['href'])

def main():
    run=new_run(ROOT,'kenya_early_protocol_source');print(run,flush=True)
    # This separate URL is linked by the university's own ARM browse page.
    # Do not disable certificate checks on the search-indexed repository host.
    url='https://ir-library.ku.ac.ke/items/a8fa524b-35f8-45fd-97ef-d046b26b94ba'
    files=[]
    try:
        with urlopen(Request(url,headers={'User-Agent':'MARS-public-protocol-audit/1.0'}),timeout=35) as r:data=r.read(16*1024*1024);status=r.status
        p=run/'item.html';p.write_bytes(data);files.append(dict(file=p.name,url=url,status=status,bytes=len(data),sha256=sha256(p)))
        parser=Links();parser.feed(data.decode('utf-8'));assert len(parser.pdf)==1
        link=urljoin(url,parser.pdf[0]);assert link.startswith(('https://repository.ku.ac.ke/','https://ir-library.ku.ac.ke/'))
        with urlopen(Request(link,headers={'User-Agent':'MARS-public-protocol-audit/1.0'}),timeout=35) as r:pdf=r.read(24*1024*1024);status=r.status
        assert pdf.startswith(b'%PDF')
        p=run/'Ngetich2011_planting.pdf';p.write_bytes(pdf);files.append(dict(file=p.name,url=link,status=status,bytes=len(pdf),sha256=sha256(p)))
        acquired=True
    except Exception as exc:
        acquired=False;files.append(dict(error=repr(exc),bypass_attempted=False))
    write_json(run/'verification.json',dict(passed=True,scope='bounded public early-protocol acquisition; qualification pending',pdf_acquired=acquired,files=files,research_ready=False,main_training_allowed=False))
    print(json.dumps(dict(pdf_acquired=acquired,files=[{k:v for k,v in f.items() if k in ('file','status','bytes','error')} for f in files]),indent=2))

if __name__=='__main__':main()
