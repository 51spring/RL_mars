"""Pin the official resource catalog and missing photo/reference PDFs."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import re
import sys
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256


def main():
    run=new_run(ROOT,'lirf_availability_sources');print(run,flush=True)
    urls={
        'official_catalog.html':'https://catalog.data.gov/dataset/usda-ars-colorado-maize-water-productivity-dataset-2008-2011',
        'LIRF_Photo_Log.pdf':'https://ndownloader.figshare.com/files/44334611',
        'Saseendran2015.pdf':'https://www.ars.usda.gov/ARSUserFiles/3495/113.%20Ag%20system%202015%20%282%29.pdf'}
    def fetch(item):
        name,url=item
        try:
            with urlopen(Request(url,headers={'User-Agent':'MARS-public-source-audit/1.0'}),timeout=45) as response:
                data=response.read(64*1024*1024+1)
                assert len(data)<=64*1024*1024
                if name.endswith('.pdf'):assert data.startswith(b'%PDF')
                (run/name).write_bytes(data)
                return dict(file=name,url=url,acquired=True,bytes=len(data),sha256=sha256(run/name))
        except Exception as exc:return dict(file=name,url=url,acquired=False,error=repr(exc))
    with ThreadPoolExecutor(max_workers=3) as pool:files=list(pool.map(fetch,urls.items()))
    passed=all(f['acquired'] for f in files)
    ids=sorted(set(re.findall(r'https://ndownloader\.figshare\.com/files/(\d+)',(run/'official_catalog.html').read_text(encoding='utf-8')))) if (run/'official_catalog.html').exists() else []
    write_json(run/'verification.json',dict(passed=passed,files=files,catalog_resource_ids=ids,
        catalog_resource_count=len(ids),research_ready=False,main_training_allowed=False,
        scope='official public resources and primary-paper acquisition, no availability conclusion from download alone'))
    print(json.dumps(dict(acquired=[f['file'] for f in files if f['acquired']],resource_ids=ids),indent=2))
    if not passed:raise RuntimeError('Some public sources unavailable; retain exact failure')


if __name__=='__main__':main()
