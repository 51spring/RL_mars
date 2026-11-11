"""Download pinned published writers and shared diagnostic dependencies."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
from urllib.request import urlopen
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
COORDS=[
 ('org.agmip.translators','translator-dssat','1.2.18'),('org.agmip.translators','translator-dssat','1.2.21'),
 ('org.agmip','agmip-core','1.2.4'),('org.agmip','agmip-common-functions','1.3.15'),
 ('org.agmip','ace-lookup','1.2.6'),('org.slf4j','slf4j-api','1.7.36'),
 ('org.slf4j','slf4j-nop','1.7.36'),('org.codehaus.jackson','jackson-mapper-asl','1.9.6'),
 ('org.codehaus.jackson','jackson-core-asl','1.9.6'),('com.google.guava','guava','14.0.1'),
 ('net.sf.opencsv','opencsv','2.3'),('uk.com.robust-it','cloning','1.9.0'),('org.objenesis','objenesis','1.2')]


def main():
    run=new_run(ROOT,'agmip_probe_runtime');print(run,flush=True)
    def get(coord):
        group,name,version=coord;base=f'https://repo.maven.apache.org/maven2/{group.replace(".","/")}/{name}/{version}/{name}-{version}'
        records=[]
        for suffix in ('.jar','.pom'):
            with urlopen(base+suffix,timeout=40) as response:data=response.read()
            path=run/(name+'-'+version+suffix);path.write_bytes(data)
            records.append(dict(file=path.name,url=base+suffix,sha256=sha256(path)))
        return records
    with ThreadPoolExecutor(max_workers=4) as pool:files=[f for group in pool.map(get,COORDS) for f in group]
    write_json(run/'verification.json',dict(passed=True,files=files,
        scope='published1.2.18/1.2.21 writers with pinned shared2022 dependencies; not a historical complete build',research_ready=False))


if __name__=='__main__':main()
