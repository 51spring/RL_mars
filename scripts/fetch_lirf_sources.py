"""Acquire the public USDA LIRF dataset without modifying original workbooks."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
from urllib.request import urlopen, Request
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256

FILES={
 'DataDictionary_r1.xlsx':44334605,'LIRF_Methodology_r1.pdf':44334608,
 'LIRF_Maize_2008.xlsx':44334614,'LIRF_Maize_2009.xlsx':44334617,
 'LIRF_Maize_2010.xlsx':44334623,'LIRF_Maize_2011.xlsx':44334626,
 'LIRF_Weather_2008.xlsx':44334629,'LIRF_Weather_2009.xlsx':44334641,
 'LIRF_Weather_2010.xlsx':44334647,'LIRF_Weather_2011.xlsx':44334650,
 'LIRF_Soils.xlsx':44334653}

def main():
    run=new_run(ROOT,'lirf_public_sources')
    print(run,flush=True)
    def get(item):
        name,identifier=item
        url=f'https://ndownloader.figshare.com/files/{identifier}'
        try:
            with urlopen(Request(url,headers={'User-Agent':'MARS-research-source-audit/1.0'}),timeout=45) as response:
                data=response.read()
                expected=b'%PDF' if name.endswith('.pdf') else b'PK'
                if not data.startswith(expected):raise ValueError('Unexpected file signature')
                path=run/name;path.write_bytes(data)
                result=dict(file=name,url=url,status=response.status,final_url=response.url,
                    bytes=len(data),sha256=sha256(path),acquired=True)
        except Exception as exc:
            result=dict(file=name,url=url,acquired=False,error=repr(exc))
        print(name+': '+str(result['acquired']),flush=True)
        return result
    with ThreadPoolExecutor(max_workers=4) as pool:files=list(pool.map(get,FILES.items()))
    write_json(run/'verification.json',dict(passed=all(f['acquired'] for f in files),files=files,
        metadata_source='https://catalog.data.gov/dataset/usda-ars-colorado-maize-water-productivity-dataset-2008-2011',
        dataset_doi='10.15482/USDA.ADC/1254006',scope='public source acquisition only',
        independent_agronomic_validation=False,research_ready=False,main_training_allowed=False))

if __name__=='__main__':main()
