"""Check acquired official metadata without promoting abstracts to full inputs."""
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256

class Inventory(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.metadata=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='a' and a.get('href','').startswith(('https://','http://','/')):
            self.links.append(a['href'])
        if tag=='meta' and a.get('name') and a.get('content'):
            self.metadata.append(dict(name=a['name'],content=a['content']))

def main():
    source=ROOT/'outputs/runs/20261106T234559Z_nebraska_reference_sources_3fd38462'
    report=json.loads((source/'verification.json').read_text(encoding='utf-8'))
    inventory=[]
    for entry in report['files']:
        if not entry['response_saved']:continue
        p=source/entry['file'];assert sha256(p)==entry['sha256']
        parser=Inventory();parser.feed(p.read_text(encoding='utf-8'))
        inventory.append(dict(file=entry['file'],url=entry['url'],sha256=sha256(p),
            metadata=parser.metadata,
            public_resource_links=sorted(set(u for u in parser.links if any(k in u.lower() for k in ('viewcontent','supplement','arsuserfiles'))))))
    assert len(inventory)==5 and report['actual_reference_pdfs']==0
    missing=[f for f in report['files'] if f['file'].endswith('.pdf')]
    assert len(missing)==2 and all(not f['pdf_acquired'] and '403' in f['error'] for f in missing)
    lookup={f['file']:f for f in inventory}
    def description(name):
        return next(m['content'] for m in lookup[name]['metadata'] if m['name']=='description')
    assert '125 or 200' in description('schmer_landing.html')
    assert '2011–2018' in description('schmer_landing.html')
    assert '56%' in description('sindelar_landing.html')
    assert 'after 5 and 6 yr' in description('sindelar_landing.html')
    assert any('article=2414&context=agronomyfacpub' in u for u in lookup['schmer_landing.html']['public_resource_links'])
    assert any('article=2280&context=agronomyfacpub' in u for u in lookup['sindelar_landing.html']['public_resource_links'])
    # Anchor the current subset to the previously checked primary article dossier.
    prior=ROOT/'outputs/runs/20261106T233953Z_nebraska_input_audit_fd40b2ec'
    d=json.loads((prior/'source_input_dossier.json').read_text(encoding='utf-8'))
    assert next(f for f in d if f['id']=='fertilizer')['reported']['rate_kg_N_ha']==200
    findings=[dict(id='schmer_full_experiment_vs_current_subset',sources=['schmer_landing.html',str((prior/'source_input_dossier.json').relative_to(ROOT))],
        verified_metadata='full experiment includes 125 and 200 kg N/ha, manure/control/cover crop, 2011-2018',
        limitation='current Li2023 subset has 200 kg N/ha only; no N-rate response contrast qualified; 2010 inclusion requires separate linkage',
        full_annual_management_acquired=False),
        dict(id='sindelar_time_and_endpoint_scope',sources=['sindelar_landing.html'],
        verified_metadata='hydraulic study after 5 and 6 years; 56 percent residue removal in abstract',
        limitation='not 2010 initial soil; no numerical full-profile parameters acquired; 56 vs approx59 percent kept source-specific',
        full_soil_profile_acquired=False),
        dict(id='li_supplement',sources=['li_landing.html'],
        limitation='no explicit supplementary payload URL identified in acquired repository anchors; publisher DOI points to previously denied landing; not a claim supplement does not exist',
        supplemental_file_acquired=False),
        dict(id='original_link_inventory_qualification',sources=['linked_resources.json'],
        limitation='acquisition script originally matched meta-description text containing supplemental as if a URL; use this audit actual href-only inventory; no downloads were issued from that list',
        resolved_in_current_parser=True),
        dict(id='source_conflicts',sources=[str((prior/'verification.json').relative_to(ROOT))],
        sd_differences_resolved=False,irrigation_unit_mapping_resolved=False,
        limitation='abstracts and bibliographic metadata do not explain raw-summary SD or repeated irrigation rows')]
    run=new_run(ROOT,'nebraska_reference_access_audit');print(run,flush=True)
    write_json(run/'official_metadata_inventory.json',inventory)
    write_json(run/'source_scope_findings.json',findings)
    write_json(run/'verification.json',dict(passed=True,scope='official metadata/access and subset boundary audit, not full-text/input qualification',
        actual_reference_pdfs=0,official_html_sources=5,supplement_acquired=False,
        unresolved_reference_pdfs=2,access_bypass_attempted=False,source_conflicts_resolved=False,
        n_rate_response_calibration_qualified=False,new_native_input_assignments=0,
        active_studies_added=0,new_native_simulations=0,new_training_runs=0,
        quantitative_fit_ready=False,research_ready=False,main_training_allowed=False,
        source_report_sha256=sha256(source/'verification.json'),
        source_input_dossier_sha256=sha256(prior/'source_input_dossier.json'),
        next_task='Inspect public file inventory and raw inputs for Iran water x N candidate 10.17632/6zj7pzftwg.1; keep Nebraska full-text and unresolved summaries pending'))
    write_json(run/'derived_files_sha256.json',{p.name:sha256(p) for p in run.iterdir() if p.is_file()})

if __name__=='__main__':main()
