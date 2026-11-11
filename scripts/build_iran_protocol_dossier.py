"""Recover source cell comments and keep reported dates separate from qualification."""
from collections import Counter,defaultdict
from datetime import date
import json
from pathlib import Path
import posixpath
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
RID='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'

def main():
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    acquired=ROOT/'outputs/runs/20261106T235323Z_iran_public_dataset_d683006d'
    prior=ROOT/'outputs/runs/20261106T235624Z_iran_input_audit_d9e85922'
    linked=ROOT/'outputs/runs/20261107T005307Z_iran_protocol_link_sources_908cd3bd'
    path=acquired/read(acquired/'verification.json')['files'][0]['local_file']
    assert sha256(path)==read(prior/'verification.json')['source_sha256']
    link_acquisition=read(linked/'verification.json')
    dentry=next(f for f in link_acquisition['files'] if f['file']=='datacite.json')
    assert dentry['sha256']==sha256(linked/'datacite.json')
    dc=read(linked/'datacite.json')['data']['attributes']
    assert dc['types']['resourceTypeGeneral']=='Dataset'
    relations=dc['relatedIdentifiers']
    assert len(relations)==1 and relations[0]['relationType']=='IsVersionOf'
    calendars=read(prior/'irrigation_calendar_audit.json')
    rows={(c['year'],r['source_row']):r for c in calendars for r in c['records']}
    comments=[];package={}
    def resolve(owner,target):
        return target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join(posixpath.dirname(owner),target))
    with zipfile.ZipFile(path) as z:
        wb=ET.fromstring(z.read('xl/workbook.xml'))
        rels={r.get('Id'):resolve('xl/workbook.xml',r.get('Target')) for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        package=dict(hidden_sheets=[s.get('name') for s in wb.findall('m:sheets/m:sheet',NS) if s.get('state','visible')!='visible'],
            embedded_objects=[n for n in z.namelist() if n.startswith('xl/embeddings/')],
            external_link_parts=[n for n in z.namelist() if n.startswith('xl/externalLinks/')],
            defined_names=len(wb.findall('m:definedNames/m:definedName',NS)),external_relationships=0)
        for name in z.namelist():
            if name.endswith('.rels'):
                package['external_relationships']+=sum(r.get('TargetMode')=='External' for r in ET.fromstring(z.read(name)))
        for sheet in wb.findall('m:sheets/m:sheet',NS):
            sheetfile=rels[sheet.get(RID)]
            relfile=posixpath.join(posixpath.dirname(sheetfile),'_rels',posixpath.basename(sheetfile)+'.rels')
            if relfile not in z.namelist():continue
            for relation in ET.fromstring(z.read(relfile)):
                if not relation.get('Type','').endswith('/comments'):continue
                commentfile=resolve(sheetfile,relation.get('Target'))
                for comment in ET.fromstring(z.read(commentfile)).findall('m:commentList/m:comment',NS):
                    cell=comment.get('ref');text=''.join(comment.find('m:text',NS).itertext()).strip()
                    kind=('planting' if 'Planting date' in text else 'harvest' if 'Harvest date' in text
                        else 'fertigation' if 'Fertigation' in text else 'fertilizer_note' if 'کوددهی' in text else 'other')
                    year=int(re.search(r'\((\d{4})\)',sheet.get('name')).group(1))
                    row_number=int(re.search(r'\d+',cell).group())
                    original=rows[(year,row_number)]
                    comments.append(dict(sheet=sheet.get('name'),cell=cell,comment_part=commentfile,
                        text=text,kind=kind,year=year,source_row=row_number,
                        reported_date_candidate=original['calendar_date_candidate'],DAP=original['DAP'],
                        source_weekday=original['source_weekday'],weekday_matches=original['weekday_matches'],
                        source_dates_corrected=False,native_assignment_allowed=False))
    assert len(comments)==16
    management=defaultdict(list)
    for c in comments:management[(c['year'],c['source_row'])].append(c)
    events=[]
    for (year,row),group in sorted(management.items()):
        c=group[0];kinds={g['kind'] for g in group}
        kind='fertigation' if 'fertigation' in kinds else c['kind']
        events.append(dict(year=year,source_row=row,kind=kind,reported_date=c['reported_date_candidate'],
            source_comment_cells=[g['cell'] for g in group],DAP=c['DAP'],weekday_matches=c['weekday_matches'],
            nitrogen_dose_kg_ha=None,nitrogen_material=None,native_assignment_allowed=False))
    planting={e['year']:e['reported_date'] for e in events if e['kind']=='planting'}
    harvest={e['year']:e for e in events if e['kind']=='harvest'}
    assert planting=={2014:'2014-07-15',2015:'2015-07-04'}
    harvest_checks=[]
    for year,h in sorted(harvest.items()):
        elapsed=(date.fromisoformat(h['reported_date'])-date.fromisoformat(planting[year])).days
        harvest_checks.append(dict(year=year,reported_date=h['reported_date'],reported_DAP=h['DAP'],
            elapsed_days_since_commented_planting=elapsed,DAP_delta=elapsed-h['DAP'],
            weekday_matches=h['weekday_matches'],native_assignment_allowed=False))
    irrigation=read(prior/'irrigation_event_candidates.json')
    coverage=[]
    for year in (2014,2015):
        year_events=[e for e in irrigation if e['year']==year]
        invalid_rows={r['source_row'] for c in calendars if c['year']==year for r in c['records'] if not r['weekday_matches']}
        conflicting=sum(int(re.search(r'\d+',e['source_cell']).group()) in invalid_rows for e in year_events)
        coverage.append(dict(year=year,numeric_event_records=len(year_events),
            first_date=min(e['date_candidate'] for e in year_events),last_date=max(e['date_candidate'] for e in year_events),
            calendar_weekday_conflicting_event_records=conflicting,
            missing_DAP_events=sum(e['DAP'] is None for e in year_events),
            native_schedule_qualified=False))
    # Explicit claims and source scope: none of these are assigned to a native model.
    fields=[
        ('paper_link','unresolved',dict(datacite_relations=relations,mendeley_related_links=read(acquired/'snapshot.json')['related_links']),
         'Version relation only; no exact primary protocol verified'),
        ('location','unresolved',None,'Institution is not field coordinates/elevation'),
        ('cultivar','unresolved',None,'Identity/genetic coefficients absent in checked package'),
        ('calibration_lineage','unresolved',None,'No exact coefficient exposure or independent-validation qualification'),
        ('planting_dates','source_reported',planting,'Explicit planting cell comments; newly recovered, not merely DAP extrapolation'),
        ('harvest_dates','conflicting',harvest_checks,'2014 elapsed121 vsDAP120;2015 elapsed134 matchesDAP134 but weekday conflicts'),
        ('annual_N_rate_labels','partial',dict(legend={'N0':0,'N1':150,'N2':300},raw=['No','N1','N2']),
         'No/N0 likely alias retained as inference, not source correction'),
        ('fertilizer_material','unresolved',None,'No material/concentration qualification'),
        ('fertigation_dates','source_reported',[e for e in events if e['kind']=='fertigation'],
         'Six dates2014/five2015 from comments; same-day H9 duplicate not a second application'),
        ('fertilizer_splits','unresolved',None,'Annual total divided equally among dates would be an unsupported assumption'),
        ('irrigation_amounts','partial',read(prior/'irrigation_amount_reconciliation.json'),'Four gross totals reconciled, efficiency unspecified'),
        ('irrigation_timing','partial',coverage,'Numeric event rows outside detected weekday conflicts; whole calendar and protocol not qualified'),
        ('soil_water_limits','partial',dict(depth_cm=[0,20,40,60],FC_vol_percent=[24.5,31,33.2],PWP_vol_percent=[11.6,13,13.5]),
         'Surface60cm only, methods and soil hierarchy not qualified'),
        ('full_soil_profile','unresolved',None,'Bulk density,texture,SAT,Ksat,OC and deeper layers unavailable'),
        ('initial_water','unresolved',None,'First soil-water DAP is not sowing initialization'),
        ('initial_mineral_N','unresolved',None,'No per-layer initial mineral N'),
        ('daily_weather','unresolved',None,'No TMAX/TMIN/SRAD/precipitation file in checked package'),
        ('planting_geometry','unresolved',None,'Density/depth/row spacing not supplied'),
        ('grain_dry_endpoint','partial','GY dry weight kg/ha','Detailed drying/sampling protocol unavailable'),
        ('uncertainty','partial','12year-treatment groups x3 source records','Descriptive SD available; measurement error and contrast covariance not qualified'),
        ('experimental_units','partial','RCBD3 in metadata; R1/2/3 in harvest','Block hierarchy and fixed physical units across years unresolved'),
        ('live_damage_recovery','unsupported',None,'No assigned live-leaf injury/recovery treatment in supplied package')]
    dossier=[dict(id=i,status=s,reported_value=v,limitation=l,native_assignment_allowed=False) for i,s,v,l in fields]
    run=new_run(ROOT,'iran_protocol_dossier');print(run,flush=True)
    write_json(run/'workbook_package_inventory.json',package)
    write_json(run/'source_comments.json',comments)
    write_json(run/'reported_management_events.json',events)
    write_json(run/'harvest_calendar_checks.json',harvest_checks)
    write_json(run/'numeric_irrigation_calendar_coverage.json',coverage)
    write_json(run/'input_dossier.json',dossier)
    write_json(run/'paper_linkage_scope.json',dict(datacite_related_identifiers=relations,datacite_related_items=dc.get('relatedItems'),
        exact_primary_paper_verified=False,public_search_languages=['English','Persian'],
        secondary_index_lead=dict(url='https://www.magiran.com/volume/253364',
            title='اثر شرایط محیطی و تاریخ کاشت بر عملکرد و بهره وری آب ذرت علوفه ای در برخی مناطق استان اصفهان (با رویکرد مدل سازی)',
            role='unconfirmed discovery lead only; author overlap not proof of dataset identity',fetch_status=403,
            no_genotype_or_location_values_transferred=True),
        absence_claim_scope='checked DOI metadata and workbook package only; no claim that a paper or protocol does not exist'))
    report=dict(passed=True,scope='source comment recovery and input-gap dossier, not complete input qualification',
        source_sha256=sha256(path),datacite_sha256=sha256(linked/'datacite.json'),input_fields=len(dossier),
        status_counts=dict(Counter(f['status'] for f in dossier)),comments=len(comments),
        unique_management_events=len(events),fertigation_dates=sum(e['kind']=='fertigation' for e in events),
        newly_source_reported_planting_dates=planting,harvest_calendar_checks=harvest_checks,
        irrigation_event_records_outside_detected_weekday_conflicts=sum(c['numeric_event_records']-c['calendar_weekday_conflicting_event_records'] for c in coverage),
        exact_primary_paper_verified=False,source_dates_corrected=False,original_workbook_modified=False,
        active_studies_added=0,new_native_input_assignments=0,new_native_simulations=0,new_training_runs=0,
        quantitative_fit_ready=False,research_ready=False,main_training_allowed=False,
        next_task='Kenya candidate public file inventory and input qualification; Iran protocol/dose/calendar gaps remain pending')
    write_json(run/'verification.json',report)
    write_json(run/'derived_files_sha256.json',{p.name:sha256(p) for p in run.iterdir() if p.is_file()})
    assert sha256(path)==report['source_sha256'];print(json.dumps(report,indent=2))

if __name__=='__main__':main()
