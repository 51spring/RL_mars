"""Fetch the official, publicly hosted article; no access bypass."""
from pathlib import Path
import sys
from urllib.request import Request, urlopen
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256

def main():
    run=new_run(ROOT,'nebraska_paper');print(run,flush=True)
    url='https://www.ars.usda.gov/ARSUserFiles/30123025/Publications/2023/Li%20etal%202023_EJournalAgronomy_Measured%20and%20simulated%20effects%20of%20residue%20removal%20and%20amelioration%20in%20no-till%20irrigated%20corn.pdf'
    with urlopen(Request(url,headers={'User-Agent':'MARS-public-source-audit/1.0'}),timeout=45) as response:
        data=response.read(32*1024*1024);status=response.status
    assert data.startswith(b'%PDF')
    p=run/'Li2023.pdf';p.write_bytes(data)
    write_json(run/'verification.json',dict(passed=True,url=url,status=status,bytes=len(data),
        source_sha256=sha256(p),scope='public source acquisition only',research_ready=False,main_training_allowed=False))

if __name__=='__main__':main()
