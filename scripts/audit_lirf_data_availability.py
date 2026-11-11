"""Bounded official-file and OOXML inventory; absence is scoped, not universal."""
import json
from pathlib import Path
import posixpath
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
import openpyxl
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,sha256,write_json
S={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'


def main():
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    source=ROOT/'outputs/runs/20261106T083612Z_lirf_public_sources_d90f9eab'
    public=ROOT/'outputs/runs/20261106T143430Z_lirf_availability_sources_018e2462'
    assert read(public/'verification.json')['passed']
    for f in read(public/'verification.json')['files']:assert sha256(public/f['file'])==f['sha256']
    old=read(source/'verification.json')['files']
    for f in old:assert sha256(source/f['file'])==f['sha256']
    ids=set(read(public/'verification.json')['catalog_resource_ids'])
    assert len(ids)==12 and {f['url'].rsplit('/',1)[1] for f in old}|{'44334611'}==ids
    run=new_run(ROOT,'lirf_data_availability');print(run,flush=True)
    inventory=[];comments=[];definitions=[]
    def resolve(part,target):
        path=target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join(posixpath.dirname(part),target))
        assert not path.startswith('../');return path
    for path in sorted(source.glob('*.xlsx')):
        with zipfile.ZipFile(path) as archive:
            names=archive.namelist();workbook=ET.fromstring(archive.read('xl/workbook.xml'))
            relationships={e.attrib['Id']:e.attrib for e in ET.fromstring(archive.read('xl/_rels/workbook.xml.rels'))}
            sheets=[]
            for e in workbook.findall('s:sheets/s:sheet',S):
                part=resolve('xl/workbook.xml',relationships[e.attrib['{'+R+'}id']]['Target'])
                assert part in names
                sheets.append(dict(name=e.attrib['name'],state=e.attrib.get('state','visible'),part=part))
                relpart=posixpath.join(posixpath.dirname(part),'_rels',posixpath.basename(part)+'.rels')
                if relpart not in names:continue
                for rel in ET.fromstring(archive.read(relpart)):
                    if not rel.attrib['Type'].endswith('/comments'):continue
                    target=resolve(part,rel.attrib['Target']);assert target in names
                    for c in ET.fromstring(archive.read(target)).findall('.//s:comment',S):
                        text=''.join(t.text or '' for t in c.findall('.//s:t',S))
                        comments.append(dict(file=path.name,sheet=e.attrib['name'],cell=c.attrib['ref'],
                            part=target,text=text,relevant_to_water_provenance=bool(re.search(r'calibr|soil.water|SWD|FC\s*=|replac|replicat|deviation',text,re.I))))
            special=[name for name in names if any(k in name.lower() for k in ('externallinks/','embeddings/','vbaproject','connections.xml','querytables/'))]
            connection_definitions=[]
            for name in special:
                if name.endswith('connections.xml'):
                    for c in ET.fromstring(archive.read(name)):
                        text=c.find('s:textPr',S)
                        connection_definitions.append(dict(part=name,connection=dict(c.attrib),
                            source_file_basename=text.attrib.get('sourceFile','').replace('\\','/').rsplit('/',1)[-1] if text is not None else None,
                            source_is_local_path_reference=text is not None and bool(re.match(r'^[A-Za-z]:',text.attrib.get('sourceFile',''))),
                            referenced_file_embedded=False,connection_refreshed=False))
                elif 'queryTables/' in name:connection_definitions.append(dict(part=name,query_table=dict(ET.fromstring(archive.read(name)).attrib),connection_refreshed=False))
            inventory.append(dict(file=path.name,sheets=sheets,special_parts=special,connection_definitions=connection_definitions,
                package_relationships_external=[dict(part=n,relationships=[r.attrib for r in ET.fromstring(archive.read(n)) if r.attrib.get('TargetMode')=='External']) for n in names if n.endswith('.rels') and any(r.attrib.get('TargetMode')=='External' for r in ET.fromstring(archive.read(n)))]))
        if path.name=='DataDictionary_r1.xlsx' or path.name=='LIRF_Soils.xlsx' or path.name.startswith('LIRF_Maize_'):
            book=openpyxl.load_workbook(path,read_only=True,data_only=True)
            tabs=book.sheetnames if path.name=='DataDictionary_r1.xlsx' else [s for s in book.sheetnames if s.startswith('Data Description')]
            for tab in tabs:
                for rownum,row in enumerate(book[tab],1):
                    text=' | '.join(str(c.value) for c in row if c.value is not None)
                    if re.search(r'calibr|soil.water|neutron|replicat|standard.deviation',text,re.I):definitions.append(dict(file=path.name,sheet=tab,row=rownum,text=text))
    assert len(inventory)==10
    relevant=[c for c in comments if c['relevant_to_water_provenance']]
    initial=[c for c in comments if 'Initial SWD selected' in c['text']]
    header=[c for c in comments if c['file']=='LIRF_Maize_2010.xlsx' and re.search(r'FC\s*=',c['text'])]
    assert len(header)==24 and len(initial)>=12
    # All target cells are checked after OOXML relationship-to-sheet resolution.
    target=[c for c in comments if c['file']=='LIRF_Maize_2010.xlsx' and c['sheet'] in ('Tmnt2','Tmnt3') and c['cell'] in ('E57','F57','G57','H57','AD57')]
    assert not target
    documents=[]
    for name in ('LIRF_Photo_Log.pdf','Saseendran2015.pdf'):
        pages=[dict(page=i+1,text=p.extract_text()) for i,p in enumerate(PdfReader(public/name).pages)]
        documents.append(dict(file=name,sha256=sha256(public/name),pages=pages))
    method=PdfReader(source/'LIRF_Methodology_r1.pdf')
    calibration=[dict(page=i+1,text=page.extract_text()) for i,page in enumerate(method.pages) if 'calibrat' in page.extract_text().lower()]
    requirements=[
        dict(id='dated_plot_swc',status='not_located_in_checked_public_resources',available='633 observed treatment dates; treatment mean of4 plots',missing='dated per-plot water and measurement sample counts/covariances'),
        dict(id='calibration_raw_pairs',status='narrative_only',available='method pages8-9 site core calibration and annual verification description; photo8 instrumentation',missing='paired relative counts/core volumetric water, coefficients, residual variance and dated verification logs'),
        dict(id='density_cores',status='pooled_statistics_only',available='D2 and other section/block density mean/SD/n',missing='individual dated calibration-core dry mass, volume and water'),
        dict(id='daily_swc_uncertainty',status='not_identified',available='static plotFC values; no substitution for daily SWC error',missing='daily depth/time covariance and instrument/calibration error propagation'),
        dict(id='two_2010_swd_rows',status='unresolved',available='stored cells, adjacent measured dates, no explanatory target-cell comments',missing='upstream per-plot aggregation and provenance'),
        dict(id='initial_water',status='model_selected_not_independent_measurement',available='AC5/AE5 comments select predicted initialSWD to first2/3observations',missing='January1 measured per-plot water profile')]
    actions=[dict(id='technical_input_work',allowed=True,scope='guarded diagnostic profile sensitivity with explicit assumptions, no field-fit claim'),
        dict(id='field_scoring',allowed=False,scope='needs predeclared error handling and defensible field input mapping'),
        dict(id='contact_or_data_request',allowed=False,scope='no messages sent; a concrete missing-data specification can be prepared for user review'),
        dict(id='search_adjacent_studies',allowed=True,scope='source discovery only; do not call same-site later years independent validation without study-overlap audit')]
    for name,value in [('workbook_inventory',inventory),('all_cell_comments',comments),('water_provenance_comments',relevant),
        ('source_definitions',definitions),('public_pdf_text',documents),('method_calibration_pages',calibration),
        ('availability_matrix',requirements),('next_action_boundary',actions)]:write_json(run/f'{name}.json',value)
    report=dict(passed=True,official_resources=12,original_files_pinned=11,new_photo_file_acquired=True,
        xlsx_packages_inventoried=10,worksheet_count=sum(len(i['sheets']) for i in inventory),
        hidden_sheets=sum(s['state']!='visible' for i in inventory for s in i['sheets']),
        special_connection_or_embedded_parts=sum(len(i['special_parts']) for i in inventory),
        comments=len(comments),water_provenance_comments=len(relevant),initial_swd_selection_comments=len(initial),
        header_fc_comments_2010=len(header),explanatory_comments_at_discrepancy_cells=len(target),
        dated_plot_swc_acquired=False,calibration_raw_pairs_acquired=False,daily_swc_uncertainty_identified=False,
        source_sha256_unchanged=True,no_global_nonexistence_claim=True,outreach_messages_sent=0,
        new_native_simulations=0,new_training_runs=0,research_ready=False,main_training_allowed=False,
        source_report_sha256={str((p/'verification.json').relative_to(ROOT)):sha256(p/'verification.json') for p in (source,public)},
        scope='official12resource list and original10XLSX structure/comments plus primary-method/paper/photo review; missing only within checked scope')
    write_json(run/'verification.json',report)
    write_json(run/'derived_files_sha256.json',{p.name:sha256(p) for p in run.iterdir() if p.is_file()})
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
