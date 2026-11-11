"""Preserve public USDA/AgMIP modelling-package bytes and API provenance."""
import json
from pathlib import Path
import sys
from urllib.request import urlopen
import zipfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256


def main():
    run=new_run(ROOT,'lirf_model_package');print(run,flush=True)
    try:
        url='https://api.figshare.com/v2/articles/24660264'
        with urlopen(url,timeout=45) as response:data=response.read()
        (run/'article.json').write_bytes(data);metadata=json.loads(data)
        item=next(f for f in metadata['files'] if f['name']=='agmip_download.zip')
        with urlopen(item['download_url'],timeout=45) as response:package=response.read()
        (run/'agmip_download.zip').write_bytes(package)
        assert len(package)==item['size']
        members=[]
        with zipfile.ZipFile(run/'agmip_download.zip') as archive:
            for member in archive.infolist():
                # No extractall: reject traversal and keep exact bytes in an owned directory.
                target=(run/'package'/member.filename).resolve()
                assert target.is_relative_to((run/'package').resolve())
                if member.is_dir():continue
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes(archive.read(member))
                members.append(dict(name=member.filename,bytes=member.file_size,sha256=sha256(target)))
        write_json(run/'verification.json',dict(passed=True,api_url=url,
            dataset_doi='10.15482/USDA.ADC/1212385',title=metadata['title'],
            download_url=item['download_url'],package_sha256=sha256(run/'agmip_download.zip'),
            metadata_sha256=sha256(run/'article.json'),members=members,
            scope='public model-package acquisition only; calibration provenance not yet qualified',
            independent_agronomic_validation=False,research_ready=False,main_training_allowed=False))
        print(json.dumps(members,indent=2))
    except Exception as exc:
        write_json(run/'failure.json',dict(passed=False,exception=repr(exc),research_ready=False));raise


if __name__=='__main__':main()
