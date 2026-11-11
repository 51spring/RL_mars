"""Qualify partial university PDFs and historical model exposure, without filling inputs."""
import hashlib
import json
from pathlib import Path
import sys
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256

def main():
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    thesis=ROOT/'outputs/runs/20261107T014953Z_kenya_thesis_pdf_5b37285e'
    early=ROOT/'outputs/runs/20261107T015203Z_kenya_early_protocol_source_eb106ea9'
    bundles=ROOT/'outputs/runs/20261107T015050Z_kenya_thesis_bundle_inventory_cdebf755'
    previous_failure=ROOT/'outputs/runs/20261107T015136Z_kenya_early_protocol_source_2945371c/verification.json'
    t=thesis/'Ngetich_thesis.pdf';e=early/'Ngetich2011_planting.pdf'
    assert sha256(t)==read(thesis/'verification.json')['sha256']
    entry=next(f for f in read(early/'verification.json')['files'] if f.get('file')==e.name)
    assert sha256(e)==entry['sha256']
    tp=PdfReader(t).pages;ep=PdfReader(e).pages
    assert len(tp)==3 and len(ep)==1
    texts=[p.extract_text() for p in tp];et=ep[0].extract_text()
    assert 'November, 2012' in texts[0] and 'DECLARATION' in texts[1] and 'ABSTRACT' in texts[2]
    assert 'AquaCrop' in texts[2] and 'AquaCrop' in et
    assert 'no grain yields were realized' in ' '.join(et.split())
    inventory=read(bundles/'inventory.json');original=next(b for b in inventory if b['bundle']=='ORIGINAL')
    assert len(original['files'])==1 and original['page_info']['totalElements']==1
    file=original['files'][0]
    assert file['sizeBytes']==t.stat().st_size==1800513
    checksum=file['checkSum']
    if checksum['checkSumAlgorithm'].upper()=='MD5':assert hashlib.md5(t.read_bytes()).hexdigest()==checksum['value']
    assert read(previous_failure)['pdf_acquired'] is False
    assert 'CERTIFICATE_VERIFY_FAILED' in str(read(previous_failure))
    findings=[
        dict(id='thesis_identity_and_scope',source=t.relative_to(ROOT).as_posix(),pdf_pages=[1,2,3],
            reported='November2012 thesis title/declaration/abstract only; repository record dated2013-03-21',
            limitation='3page public bitstream is not the full methods chapter; no moisture-correction, exact cultivar/management or model parameter tables'),
        dict(id='historical_model_exposure',source=t.relative_to(ROOT).as_posix(),pdf_pages=[3],
            reported='AquaCrop parameterization, calibration and validation mentioned for studies including staggered planting',
            limitation='possible shared data; exact seasons/plots/coefficients/splits not identified; not proof of DSSAT exposure or independence',
            exact_model_package_lineage_verified=False),
        dict(id='trial_separation',source=t.relative_to(ROOT).as_posix(),pdf_pages=[3],
            reported='abstract covers staggered planting, tillage/surface management, split N timing and runoff trials',
            limitation='70N statement belongs to split-N result; do not assign it or unstated kg/ha units to staggered-sowing treatment'),
        dict(id='early_paper_scope',source=e.relative_to(ROOT).as_posix(),pdf_pages=[1],
            reported='Mbeere3sowing x2varieties x3replicates, LR09/SR09/LR10 and trial-site AquaCrop calibration described',
            limitation='one-page abstract only; two varieties unnamed and full5season/site match unverified'),
        dict(id='LR09_non_equivalence',source=e.relative_to(ROOT).as_posix(),pdf_pages=[1],
            reported='early abstract reports no grain in LR09; current CSV18 MachangaLR09 totals17failures/18, with1grain-producing plot',
            limitation='same trial/aggregation/curation definitions unverified; do not erase one positive source plot or create an independent replicate'),
        dict(id='availability_scope',source=bundles.relative_to(ROOT).as_posix(),pdf_pages=[],
            reported='ORIGINAL1PDF; LICENSE/TEXT/THUMBNAIL one file each',
            limitation='checked public item contains no extra ORIGINAL methods file; does not prove full thesis unavailable elsewhere'),
        dict(id='TLS_and_localhost',source=previous_failure.relative_to(ROOT).as_posix(),pdf_pages=[],
            reported='search-indexed repository host failed hostname verification; separate valid ir-library item was explicitly linked by official ARM browse page',
            limitation='certificate checks never disabled; localhost citation_pdf_url ignored in favor of official HTTPS rel=item link')]
    run=new_run(ROOT,'kenya_legacy_protocol_audit');print(run,flush=True)
    write_json(run/'source_scope_and_lineage.json',findings)
    needed=['full grain correction/drying protocol','exact5season/site/plot overlap','cultivar identities and parameters',
        'full soil/initial water/mineral N','daily weather','sowing/fertilizer/pesticide schedules and plant geometry',
        'AquaCrop calibration splits and coefficients','DSSAT coefficient/package exposure']
    write_json(run/'unresolved_input_contract.json',dict(fields=[dict(name=n,status='unresolved',native_assignment_allowed=False) for n in needed],
        no_dose_or_weather_imputation=True,quantitative_execution_allowed=False))
    renders=[thesis/f'page-{n}.png' for n in (1,2,3)]+[early/'page-1.png']
    assert all(p.exists() for p in renders)
    write_json(run/'verification.json',dict(passed=True,scope='public partial-PDF and historical lineage scope audit, not full protocol acquisition',
        official_PDFs_acquired=2,thesis_public_pages=3,early_paper_public_pages=1,rendered_pages_visually_reviewed=4,
        original_bundle_PDFs=1,full_thesis_acquired=False,full_early_protocol_acquired=False,grain_correction_basis_verified=False,
        current_dataset_exact_overlap_verified=False,exact_model_package_lineage_verified=False,
        LR09_definition_conflict_unresolved=True,source_grain_failure_values_changed=False,
        new_native_input_assignments=0,active_studies_added=0,new_native_simulations=0,new_training_runs=0,
        quantitative_fit_ready=False,research_ready=False,main_training_allowed=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha256(p) for p in [t,e,thesis/'verification.json',early/'verification.json',bundles/'verification.json',bundles/'inventory.json',previous_failure,*renders]},
        next_task='Independent work item3: Oliveira architecture/N-study overlap, experimental units and moisture basis; field calibration candidates stay pending full inputs'))
    write_json(run/'derived_files_sha256.json',{p.name:sha256(p) for p in run.iterdir() if p.is_file()})

if __name__=='__main__':main()
