"""Preserve official published DOME engine and source for diagnostic execution."""
from pathlib import Path
import sys
from urllib.request import urlopen
import zipfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256


def main():
    run=new_run(ROOT,'dome_runtime');print(run,flush=True)
    base='https://repo.maven.apache.org/maven2/org/agmip/dome/1.4.15/dome-1.4.15'
    files=[]
    for suffix in ('.jar','-sources.jar','.pom'):
        with urlopen(base+suffix,timeout=40) as response:data=response.read()
        path=run/('dome-1.4.15'+suffix);path.write_bytes(data)
        files.append(dict(file=path.name,url=base+suffix,sha256=sha256(path)))
    with zipfile.ZipFile(run/'dome-1.4.15-sources.jar') as archive:
        for member in archive.infolist():
            if member.is_dir():continue
            target=(run/'source'/member.filename).resolve()
            assert target.is_relative_to((run/'source').resolve())
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(archive.read(member))
    write_json(run/'verification.json',dict(passed=True,version='1.4.15',files=files,
        scope='official DOME binary and source acquisition, not historical package-engine identity',research_ready=False))


if __name__=='__main__':main()
