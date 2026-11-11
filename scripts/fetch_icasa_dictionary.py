"""Pin official ICASA definitions to a commit for source-input audits."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sys
from urllib.parse import quote
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256


def fetch(url):
    with urlopen(Request(url,headers={'User-Agent':'MARS-source-audit'}),timeout=40) as response:
        return response.read()


def main():
    run=new_run(ROOT,'icasa_dictionary');print(run,flush=True)
    try:
        commit=fetch('https://api.github.com/repos/DSSAT/ICASA-Dictionary/commits/main')
        (run/'commit.json').write_bytes(commit);revision=json.loads(commit)['sha']
        tree=fetch(f'https://api.github.com/repos/DSSAT/ICASA-Dictionary/git/trees/{revision}?recursive=1')
        (run/'tree.json').write_bytes(tree)
        paths=[r['path'] for r in json.loads(tree)['tree'] if r['path'].startswith('CSV/') and r['path'].endswith('.csv')]
        def get(path):
            url=f'https://raw.githubusercontent.com/DSSAT/ICASA-Dictionary/{revision}/'+quote(path)
            data=fetch(url);target=run/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
            return dict(path=path,url=url,sha256=sha256(target))
        with ThreadPoolExecutor(max_workers=4) as pool:files=list(pool.map(get,paths))
        write_json(run/'verification.json',dict(passed=True,revision=revision,files=files,
            scope='current official definitions only; not proof of historical2015 exporter conventions',research_ready=False))
        print('CSV_FILES='+str(len(files)))
    except Exception as exc:
        write_json(run/'failure.json',dict(passed=False,error=repr(exc),research_ready=False));raise


if __name__=='__main__':main()
