"""Acquire dated CoAgMET QC observations around the three source gaps."""
from concurrent.futures import ThreadPoolExecutor
from datetime import date,timedelta
import json
from pathlib import Path
import sys
from urllib.request import urlopen
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256


def main():
    run=new_run(ROOT,'lirf_station_windows');print(run,flush=True)
    doc_url='https://coagmet.colostate.edu/data/doc.html'
    with urlopen(doc_url,timeout=40) as response:(run/'api_documentation.html').write_bytes(response.read())
    requests=[]
    for target in ('2009-10-02','2010-07-16','2011-08-11'):
        day=date.fromisoformat(target)
        for station in ('gly04','ksy01'):
            start,end=(day-timedelta(days=3)).isoformat(),(day+timedelta(days=3)).isoformat()
            url=f'https://coagmet.colostate.edu/data/daily/{station}.json?from={start}&to={end}&units=m&fields=tMax,tMin,solarRad'
            requests.append((f'{station}_{target}.json',url))
    def get(item):
        name,url=item
        try:
            with urlopen(url,timeout=40) as response:data=response.read()
            decoded=json.loads(data);assert decoded['units']=='m' and decoded['frequency']=='daily'
            (run/name).write_bytes(data)
            return dict(file=name,url=url,acquired=True,sha256=sha256(run/name))
        except Exception as exc:return dict(file=name,url=url,acquired=False,error=repr(exc))
    with ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(get,requests))
    write_json(run/'verification.json',dict(passed=all(r['acquired'] for r in results),requests=results,
        documentation_url=doc_url,documentation_sha256=sha256(run/'api_documentation.html'),
        scope='current official QC data retrieval; no original workbook replacement',research_ready=False))
    print(json.dumps(results,indent=2))


if __name__=='__main__':main()
