"""Pin bounded availability findings without claiming global data absence."""
import json
from pathlib import Path
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
import openpyxl
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256


def main():
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    source=ROOT/'outputs/runs/20261106T083612Z_lirf_public_sources_d90f9eab'
    public=ROOT/'outputs/runs/20261106T143430Z_lirf_availability_sources_018e2462'
    folder=ROOT/'outputs/runs/20261106T143732Z_lirf_data_availability_cb685664'
    tests=ROOT/'outputs/runs/20261106T143925Z_unit_regressions_134e191c/verification.json'
    ready=ROOT/'outputs/runs/20261106T144001Z_readiness_a125694d/readiness.json'
    for d in (source,public):
        for f in read(d/'verification.json')['files']:assert sha256(d/f['file'])==f['sha256']
    for name,digest in read(folder/'derived_files_sha256.json').items():assert sha256(folder/name)==digest
    original_ids={f['url'].rsplit('/',1)[1] for f in read(source/'verification.json')['files']}
    assert original_ids|{'44334611'}==set(read(public/'verification.json')['catalog_resource_ids'])
    inventory=read(folder/'workbook_inventory.json');comments=read(folder/'all_cell_comments.json')
    assert len(inventory)==10 and len(comments)==228
    original_comments=[];sheet_count=0;connections=[]
    ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    for item in inventory:
        p=source/item['file'];w=openpyxl.load_workbook(p,read_only=True,data_only=True)
        assert w.sheetnames==[s['name'] for s in item['sheets']]
        assert all(w[s].sheet_state=='visible' for s in w.sheetnames);sheet_count+=len(w.sheetnames)
        with zipfile.ZipFile(p) as archive:
            for part in archive.namelist():
                if re.fullmatch(r'xl/comments\d+\.xml',part):
                    for c in ET.fromstring(archive.read(part)).findall('.//s:comment',ns):
                        original_comments.append((p.name,part,c.attrib['ref'],''.join(t.text or '' for t in c.findall('.//s:t',ns))))
        connections += [c for c in item['connection_definitions'] if 'source_file_basename' in c]
    assert sheet_count==60
    assert sorted(original_comments)==sorted((c['file'],c['part'],c['cell'],c['text']) for c in comments)
    assert len(connections)==4 and all(c['source_file_basename']=='GLY04_CLEAN.csv' and c['source_is_local_path_reference'] and not c['connection_refreshed'] for c in connections)
    w=openpyxl.load_workbook(source/'LIRF_Maize_2010.xlsx',read_only=True,data_only=True)
    rows=list(w['Seasonal']);start=next(i for i,c in enumerate(rows[4]) if c.value=='0 - 15 cm')
    stale=[]
    for c in comments:
        if c['file']!='LIRF_Maize_2010.xlsx' or not re.fullmatch(r'Tmnt[1-6]',c['sheet']) or c['cell'] not in ('E3','F3','G3','H3'):continue
        m=re.search(r'FC\s*=\s*([\d.]+)',c['text']);assert m
        t=int(c['sheet'][-1]);k=ord(c['cell'][0])-ord('E');actual=rows[t+5][start+k]
        assert abs(float(m[1])-actual.value)>.1
        stale.append(dict(sheet=c['sheet'],comment_cell=c['cell'],comment_fc_percent=float(m[1]),
            seasonal_cell=actual.coordinate,seasonal_fc_percent=actual.value,source_corrected=False))
    assert len(stale)==24
    spec=read(ROOT/'docs/LIRF_MISSING_DATA_SPEC.json')
    assert spec['contact_authorized'] is False and spec['messages_sent']==0 and spec['universal_absence_claim'] is False
    assert spec['model_error_tolerance_mm'] is None and spec['research_ready'] is False
    report=read(folder/'verification.json')
    assert report['no_global_nonexistence_claim'] and not report['dated_plot_swc_acquired'] and not report['daily_swc_uncertainty_identified']
    t=read(tests);r=read(ready)
    assert t['passed'] and t['tests_run']==199 and not(t['failures'] or t['errors'] or t['skipped'])
    assert r['research_ready'] is False and r['main_training_allowed'] is False and not r['quantitative_fit_ready_studies']
    files=[folder/'verification.json',folder/'derived_files_sha256.json',public/'verification.json',tests,ready,
        ROOT/'scripts/fetch_lirf_availability_sources.py',ROOT/'scripts/audit_lirf_data_availability.py',Path(__file__),
        ROOT/'configs/lirf_translation_contract.json',ROOT/'configs/agronomic_sources.json',
        ROOT/'docs/LIRF_DATA_AVAILABILITY.md',ROOT/'docs/LIRF_MISSING_DATA_SPEC.json',ROOT/'docs/NEXT_STEPS.md',ROOT/'PROGRESS.md']
    run=new_run(ROOT,'lirf_data_availability_release')
    write_json(run/'fc_comment_disagreements.json',stale)
    write_json(run/'verification.json',dict(passed=True,official_resources=12,worksheets=60,comments_verified=228,
        stale_2010_fc_comments=24,weather_csv_connections_not_refreshed=4,tests_run=199,
        source_sha256_unchanged=True,old_workspace_empty=True,outreach_messages_sent=0,
        no_global_data_absence_claim=True,new_native_simulations=0,new_training_runs=0,
        research_ready=False,main_training_allowed=False,quantitative_fit_ready_studies=0,
        evidence_sha256={str(p.relative_to(ROOT)):sha256(p) for p in files},
        image_evidence_sha256=sha256(ROOT/'outputs/lirf-photo-instruments-09.png'),
        scope='bounded public-file and comment inventory; missing data specification, not field validation'))
    print(run)


if __name__=='__main__':main()
