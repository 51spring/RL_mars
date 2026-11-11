"""Bounded public-primary-source search; retain failures without bypass attempts."""
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.parse import urljoin
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256


class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.href=None;self.label=''
    def handle_starttag(self,tag,attrs):
        if tag=='a':self.href=dict(attrs).get('href');self.label=''
    def handle_data(self,data):
        if self.href:self.label+=data
    def handle_endtag(self,tag):
        if tag=='a' and self.href:self.links.append((self.label.strip(),self.href));self.href=None


def main():
    run=new_run(ROOT,'fang_lineage_sources');print(run,flush=True)
    urls={
        'publisher_landing.html':'https://acsess.onlinelibrary.wiley.com/doi/10.2134/advagricsystmodel5.c1',
        'ARS_2014_publications.html':'https://www.ars.usda.gov/research/publications/publications-at-this-location/?filterYear=2014&locpubs=yes&modecode=30-12-20-00',
        'RZWQM_publication_list.pdf':'https://www.ars.usda.gov/ARSUserFiles/30123025/software/rzwqmpub.pdf',
        'Zhang2021.pdf':'https://www.ars.usda.gov/ARSUserFiles/3495/111.%20Zhang%20Huihui%20AWM%202021.pdf'}
    def fetch(item):
        name,url=item
        try:
            with urlopen(Request(url,headers={'User-Agent':'MARS-primary-lineage-audit/1.0'}),timeout=40) as response:
                data=response.read(32*1024*1024+1);status=response.status
            assert len(data)<=32*1024*1024
            if name.endswith('.pdf'):assert data.startswith(b'%PDF')
            (run/name).write_bytes(data)
            return dict(file=name,url=url,acquired=True,status=status,bytes=len(data),sha256=sha256(run/name))
        except Exception as exc:return dict(file=name,url=url,acquired=False,error=repr(exc),retry_or_bypass_attempted=False)
    with ThreadPoolExecutor(max_workers=4) as pool:files=list(pool.map(fetch,urls.items()))
    path=run/'ARS_2014_publications.html'
    discovered=[]
    if path.exists():
        parser=Links();parser.feed(path.read_text(encoding='utf-8'))
        for label,url in parser.links:
            if 'quantifying' in label.lower() and 'yield' in label.lower():discovered.append(dict(label=label,url=urljoin(urls[path.name],url)))
        for i,item in enumerate(discovered):
            if item['url'].startswith('https://www.ars.usda.gov/'):
                result=fetch((f'ARS_record_{i}.html',item['url']));files.append(result)
                if result['acquired']:
                    parser=Links();parser.feed((run/result['file']).read_text(encoding='utf-8'))
                    item['outbound_links']=[dict(label=label,url=urljoin(item['url'],url)) for label,url in parser.links
                        if '.pdf' in url.lower() or 'full text' in label.lower() or '10.2134' in url]
    write_json(run/'discovered_records.json',discovered)
    write_json(run/'verification.json',dict(passed=any(f['acquired'] and f['file']=='Zhang2021.pdf' for f in files),
        files=files,discovered_ARS_records=len(discovered),chapter_fulltext_acquired=False,
        research_ready=False,main_training_allowed=False,scope='bounded public-primary-source acquisition; partial retrieval and chapter access failures retained'))
    print(json.dumps(dict(files=[{k:v for k,v in f.items() if k in ('file','acquired','error')} for f in files],records=discovered),indent=2))


if __name__=='__main__':main()
