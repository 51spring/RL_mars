"""Source-located experiment/unit audit; evidence can only retain the gate."""
from html.parser import HTMLParser
import json
import logging
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256

class Text(HTMLParser):
    def __init__(self):super().__init__();self.parts=[]
    def handle_data(self,data):self.parts.append(data)

def html_text(path):
    parser=Text();parser.feed(path.read_text(encoding='utf-8'))
    return ' '.join(' '.join(parser.parts).split())

def main():
    a=ROOT/'outputs/runs/20261106T062043Z_grain_maize_public_api_a275f354'
    n=ROOT/'outputs/runs/20261106T042630Z_agronomic_source_refresh_14759c5a'
    d=ROOT/'outputs/runs/20261106T062010Z_grain_maize_source_fetch_eb958dfa'
    pdf=a/'oliveira_architecture2026.pdf';html=n/'oliveira2026.html';docx=n/'oliveira2026_supplement.docx'
    dryad=d/'dryad_page.html';metadata=a/'dryad_metadata.json'
    checked=json.loads((a/'sources.json').read_text(encoding='utf-8'))
    assert sha256(pdf)==checked[pdf.name]['sha256'] and sha256(metadata)==checked[metadata.name]['sha256']
    assert '401' in checked['dryad_data.zip']['error']
    logging.getLogger('pypdf').setLevel(logging.ERROR)
    pages=PdfReader(pdf).pages
    p3,p4=(' '.join(pages[i].extract_text().split()) for i in (2,3))
    nt=html_text(html);dt=html_text(dryad)
    assert 'KWS9606' in p3 and 'five replicates per factor combination' in p3
    assert 'total weight per pot divided' in p4 and '13% moisture' in p4
    assert 'single plant' in dt and 'total aboveground biomass' in dt
    assert 'September 2024 to January 2025' in nt and '48 experimental units (pots)' in nt
    assert 'KWS 9668 VIP 3' in nt and '10.1002/agg2.70295' in nt
    assert 'total grain mass' in nt and 'standard error (SE) of 8 replications' in nt
    # This ANOVA row verifies a reported interaction, but is not a mean/SE table.
    with zipfile.ZipFile(docx) as z:tree=ET.fromstring(z.read('word/document.xml'))
    w={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    rows=[[''.join(x.text or '' for x in c.findall('.//w:t',w)).strip() for c in r.findall('w:tc',w)]
          for r in tree.findall('.//w:tr',w)]
    grain=next(r for r in rows if r and r[0]=='Grain weight')
    assert grain==['Grain weight','11.74','0.003','6.63','0.004','3.88','0.029']
    crosswalk=[
        ('identity','Danielle de Oliveira; 10.1002/agg2.70295','Antonio Carlos de Oliveira Jr.; 10.1007/s11738-026-03963-0','different first authors and DOIs; N paper cites architecture paper; citation is not a pot-ID link'),
        ('time','not stated in checked Methods p3 / Dryad design description','September2024–January2025','publication, receipt and funding dates do not establish experiment dates'),
        ('location','Santa Clara UNIFAL-MG, 818m, 21°25′20″S 45°59′00″W','same reported greenhouse coordinates and elevation','shared research setting, not proof of same material'),
        ('design','RCBD 4hybrids x2 cuts x5pots =40 nominal pots','RCBD 2cuts x3 topdress schedules x8pots =48 nominal pots','different reported factorial designs; do not pool or certify disjoint pot IDs'),
        ('cultivar','BRS1010, BRS1055, KWS9606 VIP3, NS90 PRO2','KWS 9668 VIP 3','9606 and 9668 retained literally; no alias or seed-lot proof'),
        ('plants_per_pot','paper 2; Dryad README 1','2 after thinning','architecture internal source conflict; raw row basis unresolved'),
        ('reported_environment','mean max35C/min18C, mean humidity79%','mean temperature23C, mean humidity55%','mean extrema and mean temperature not directly comparable; no daily weather'),
        ('damage','V4 approximately5cm shoot cut','V4 5cm shoot cut in journal; related embargoed dissertation metadata describes V5','different-source stage lead; experiment identity unresolved, preserve journal protocol, no uniform leaf mass mapping'),
        ('nitrogen','MAP at planting; urea three0.88g applications, 10days apart after emergence','N40 basal, N80 topdress at V4 or V6 or no N topdress','different reported schedules; no transfer of elemental N dose, pot conversion or assumed event dates'),
        ('grain_unit','paper grain yield = pot total /2 (per-plant average); README Grain_weight and Grain_yield both labelled g/plant','Fig2C total grain weight; no verified pot-total vs per-plant allocation','measurement label is not independent biological replicate; no division or multiplication applied to raw data'),
        ('moisture','13% explicit for 100-grain weight and HI numerator; separate grain-yield field basis unqualified','grain moisture correction not identified for Fig2C; grain dry matter mentioned for chemical assay','no across-field 0.87 or 65C dry protocol transfer'),
        ('harvest_index','paper denominator whole plant dry mass = shoot+root; README aboveground biomass','no common HI outcome qualified','denominator conflict; do not combine or calculate without matched component records'),
        ('uncertainty','five pots per combination; raw spreadsheet not acquired','Fig2 mean ±SE n8; S2 F/p, no numeric six-cell mean/SE from it','no n10/n16, no numeric fit threshold inferred'),
        ('lineage','raw pot identifiers and exact calibration exposure unavailable','data availability statement not applicable; exact package/cultivar calibration lineage unavailable','different reported setups, no proof of shared pots or verified independence')]
    fields=[dict(field=f,architecture=x,nitrogen=y,boundary=b,native_assignment_allowed=False) for f,x,y,b in crosswalk]
    leads=[
        dict(source='https://repositorio.unifal-mg.edu.br/browse/title?scope=2b8a00e9-d832-4f6b-b479-b08757daac12',
            title='Avaliação das respostas morfofisiológicas e transcriptômicas do milho sob desfolha precoce',
            indexed_date='2026-05-04',access='official indexed public abstract; item embargo',lead='Danielle, four genotypes, V4 and transcriptomics; exact experiment dates not established',body_acquired=False),
        dict(source='https://repositorio.unifal-mg.edu.br/browse/course?scope=ad6c043f-8d82-4ff5-9e5c-69e7b62ea96a&value=Mestrado+em+Ci%C3%AAncias+Ambientais',
            title='Desfolha precoce e adubação nitrogenada: efeitos nos aspectos morfofisiologicos e de produção de plantas de milho',
            indexed_date='2026-04-13',access='official indexed public abstract; item embargo',lead='Antonio Carlos, V5 cut and V4/V6 N in abstract vs journal V4; identical experiment not verified',body_acquired=False),
        dict(source='https://www.unifal-mg.edu.br/portal/2024/05/23/pesquisa-da-unifal-mg-revela-inovacoes-no-cultivo-e-na-resiliencia-do-milho-a-partir-da-desfolha-precoce/',
            access='official project news',lead='both first authors listed on shared broader project; not experimental-unit linkage')]
    run=new_run(ROOT,'oliveira_overlap_units');print(run,flush=True)
    write_json(run/'source_crosswalk.json',fields)
    write_json(run/'public_linkage_leads.json',leads)
    write_json(run/'grain_ANOVA_source_row.json',dict(table='S2',row=grain,columns=['response','F_defoliation','p_defoliation','F_N','p_N','F_interaction','p_interaction'],
        mean_or_SE_available_from_row=False,no_effect_of_defoliation_constraint_selected=False))
    write_json(run/'unit_contract.json',dict(architecture_paper_pot_replicates=5,architecture_paper_plants_per_pot=2,
        architecture_Dryad_plants_per_pot=1,nitrogen_pot_replicates=8,nitrogen_plants_per_pot=2,
        architecture_pot_population_conflict=True,architecture_HI_denominator_conflict=True,
        explicit_13_percent_targets=['architecture_100_grain_weight','architecture_HI_numerator'],
        automatic_grain_moisture_conversions=0,raw_pot_to_field_conversions=0,replicate_count_inflations=0,
        numeric_grain_mean_or_SE_digitized=0,raw_pot_ids_acquired=False))
    source_paths=[pdf,html,docx,dryad,metadata,a/'method-03.png',a/'method-04.png',a/'sources.json']
    write_json(run/'verification.json',dict(passed=True,study_id='oliveira2026',paired_study_id='oliveira_architecture2026',
        scope='reported experiment distinctions and unresolved overlap/unit/moisture; no cross-study independence qualification',
        fields_compared=len(fields),reported_designs_distinguishable=True,same_physical_pots_verified=False,
        exact_experiment_overlap_resolved=False,whole_study_independence_verified=False,package_calibration_lineage_verified=False,
        architecture_raw_XLSX_acquired=False,dryad_retried=False,embargo_bypass_attempted=False,
        numeric_grain_target_assignments=0,new_native_simulations=0,new_training_runs=0,
        quantitative_fit_ready=False,research_ready=False,main_training_allowed=False,
        next_task='Extract Du Plessis temperature-development/survival biological constraints, without assigning population growth/survey noise',
        source_sha256={p.relative_to(ROOT).as_posix():sha256(p) for p in source_paths}))
    write_json(run/'derived_files_sha256.json',{p.name:sha256(p) for p in run.iterdir() if p.is_file()})

if __name__=='__main__':main()
