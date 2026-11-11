"""Public primary calibration papers, pinned without model parameter replacement."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256


def main():
    run=new_run(ROOT,'lirf_calibration_sources');print(run,flush=True)
    urls={
        'Ma2012.pdf':'https://www.ars.usda.gov/ARSUserFiles/30100500/Publications%202010-2019/569%202011%20Nielsen%20-%20Calibrating%20RZWQM2%20model%20for%20maize%20responses%20to%20deficit%20irrigation.PDF',
        'Fang2017.pdf':'https://www.ars.usda.gov/ARSUserFiles/3495/114.%20Fang%20ASABE%20SI-2%20%282%29.pdf'}
    def get(item):
        name,url=item
        try:
            with urlopen(Request(url,headers={'User-Agent':'MARS-provenance-audit/1.0'}),timeout=45) as response:data=response.read(32*1024*1024+1)
            assert len(data)<=32*1024*1024 and data.startswith(b'%PDF')
            (run/name).write_bytes(data)
            return dict(file=name,url=url,acquired=True,bytes=len(data),sha256=sha256(run/name))
        except Exception as exc:return dict(file=name,url=url,acquired=False,error=repr(exc))
    with ThreadPoolExecutor(max_workers=2) as pool:files=list(pool.map(get,urls.items()))
    passed=all(f['acquired'] for f in files)
    write_json(run/'verification.json',dict(passed=passed,files=files,scope='primary calibration-source acquisition only',research_ready=False,main_training_allowed=False))
    print([(f['file'],f['acquired']) for f in files])
    if not passed:raise RuntimeError('Primary source acquisition incomplete')


if __name__=='__main__':main()
