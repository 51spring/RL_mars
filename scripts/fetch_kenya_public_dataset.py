"""Use the anonymous endpoints exposed by the official Mendeley client."""
from pathlib import Path
import hashlib
import json
import re
import sys
from urllib.parse import urlencode,urlparse
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
DATASET='tdw54wgvbf';VERSION=1

def main():
    discovery=ROOT/'outputs/runs/20261106T235213Z_iran_public_api_discovery_0c8dd185'
    bundle=discovery/'datasets_bundle.js'
    assert sha256(bundle)=='d03ed6d08268c0c04db358f5fbbfdced5689ed27cbbd59a29f3ee79519483edf'
    client=bundle.read_text(encoding='utf-8')
    assert '/datasets/${t}/files?folder_id=${i}&version=${n}' in client
    run=new_run(ROOT,'kenya_public_dataset');print(run,flush=True)
    base=f'https://data.mendeley.com/public-api/datasets/{DATASET}'
    acquired=[]
    def get_json(url,name):
        with urlopen(Request(url,headers={'User-Agent':'MARS-public-data-audit/1.0',
                'Accept':'application/vnd.mendeley-public-dataset.1+json'}),timeout=40) as r:
            payload=r.read(16*1024*1024+1);status=r.status
        assert len(payload)<=16*1024*1024
        parsed=json.loads(payload);p=run/name;p.write_bytes(payload)
        acquired.append(dict(file=name,url=url,status=status,bytes=len(payload),sha256=sha256(p)))
        return parsed
    snapshot=get_json(base+'/snapshot/1','snapshot.json')
    assert snapshot['id']==DATASET and snapshot['version']==VERSION
    assert snapshot['is_confidential'] is False
    folders=get_json(base+'/folders/1','folders.json')
    assert isinstance(folders,list) and len(folders)<100
    files=[]
    for folder in ['root']+[f['id'] for f in folders]:
        for page in range(10):
            q=urlencode(dict(folder_id=folder,version=VERSION,**{'$start':page*1000,'$limit':1000}))
            batch=get_json(base+'/files?'+q,f'files_{folder}_{page}.json')
            assert isinstance(batch,list)
            files.extend(batch)
            if len(batch)<1000:break
        else:raise ValueError('File pagination exceeded explicit bound')
    assert len({f['id'] for f in files})==len(files)
    downloaded=[];total=0
    for f in files:
        name=f['filename'];details=f['content_details'];url=details['download_url']
        item=dict(id=f['id'],filename=name,metadata_status=f['status'],declared_size=details['size'],acquired=False)
        try:
            assert f['status']=='COMPLETED' and 0<details['size']<=32*1024*1024
            assert total+details['size']<=128*1024*1024
            assert urlparse(url).scheme=='https'
            local=re.sub(r'[^A-Za-z0-9_.-]','_',name)
            target=run/f"{f['id']}_{local}"
            assert target.resolve().parent==run.resolve()
            with urlopen(Request(url,headers={'User-Agent':'MARS-public-data-audit/1.0'}),timeout=45) as r:
                content=r.read(32*1024*1024+1);status=r.status
            assert len(content)==details['size']
            target.write_bytes(content);digest=sha256(target)
            if details.get('sha256_hash'):assert digest==details['sha256_hash']
            if details.get('sha1_hash'):assert hashlib.sha1(content).hexdigest()==details['sha1_hash']
            total+=len(content)
            item.update(acquired=True,local_file=target.name,bytes=len(content),sha256=digest,
                repository_sha256_checked=bool(details.get('sha256_hash')),repository_sha1_checked=bool(details.get('sha1_hash')),http_status=status)
        except Exception as exc:item.update(error=repr(exc),bypass_attempted=False)
        downloaded.append(item)
    write_json(run/'verification.json',dict(passed=True,scope='public version1 metadata/file acquisition; individual failures retained; not calibration qualification',
        dataset_id=DATASET,version=VERSION,doi='10.17632/tdw54wgvbf.1',
        client_source_sha256=sha256(bundle),metadata_acquired=acquired,files=downloaded,
        listed_files=len(files),acquired_files=sum(d['acquired'] for d in downloaded),
        folders=len(folders),total_downloaded_bytes=total,active_studies_added=0,
        quantitative_fit_ready=False,research_ready=False,main_training_allowed=False))
    print(json.dumps(dict(listed=len(files),acquired=sum(d['acquired'] for d in downloaded),
        files=[{k:v for k,v in d.items() if k in ('filename','local_file','acquired','bytes','error')} for d in downloaded]),indent=2))

if __name__=='__main__':main()
