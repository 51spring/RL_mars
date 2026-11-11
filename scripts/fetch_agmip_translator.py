"""Pin present and historical-candidate official translator source snapshots."""
from concurrent.futures import ThreadPoolExecutor
import io
import json
from pathlib import Path
import sys
from urllib.request import Request,urlopen
import zipfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256


def fetch(url):
    with urlopen(Request(url,headers={'User-Agent':'MARS-source-audit'}),timeout=45) as response:return response.read()


def main():
    run=new_run(ROOT,'agmip_translator_sources');print(run,flush=True)
    try:
        urls={
            'current':'https://api.github.com/repos/agmip/translator-dssat/commits/master',
            'historical_candidate':'https://api.github.com/repos/agmip/translator-dssat/commits?until=2015-12-31T23:59:59Z&per_page=1'}
        def get(item):
            label,url=item;folder=run/label;folder.mkdir()
            raw=fetch(url);(folder/'commit.json').write_bytes(raw)
            commit=json.loads(raw);commit=commit[0] if isinstance(commit,list) else commit
            revision=commit['sha'];archive=fetch(f'https://codeload.github.com/agmip/translator-dssat/zip/{revision}')
            (folder/'source.zip').write_bytes(archive);files={}
            with zipfile.ZipFile(io.BytesIO(archive)) as z:
                for member in z.infolist():
                    if member.is_dir():continue
                    relative=Path(*Path(member.filename).parts[1:])
                    target=(folder/'source'/relative).resolve()
                    assert target.is_relative_to((folder/'source').resolve())
                    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(member))
                    files[relative.as_posix()]=sha256(target)
            result=dict(label=label,revision=revision,date=commit['commit']['committer']['date'],
                api_url=url,archive_sha256=sha256(folder/'source.zip'),files=files)
            write_json(folder/'index.json',result);return result
        with ThreadPoolExecutor(max_workers=2) as pool:records=list(pool.map(get,urls.items()))
        write_json(run/'verification.json',dict(passed=True,snapshots=records,
            historical_candidate_is_proven_package_exporter=False,
            scope='public official source acquisition only; two snapshots do not prove the package exporter version',research_ready=False))
        print(json.dumps([{k:r[k] for k in ('label','revision','date')} for r in records],indent=2))
    except Exception as exc:
        write_json(run/'failure.json',dict(passed=False,error=repr(exc),research_ready=False));raise


if __name__=='__main__':main()
