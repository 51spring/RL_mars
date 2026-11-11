"""Check immutable source, conditional units, retained observations and no promotion."""
import json
from pathlib import Path
import sys
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.validation_lineage import independent_lineage_status


def main():
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    folder=ROOT/'outputs/runs/20261106T231818Z_oveysi_input_dossier_2283981d'
    priority=ROOT/'outputs/runs/20261106T231934Z_agronomic_input_priorities_e045fb29/verification.json'
    tests=ROOT/'outputs/runs/20261106T231934Z_unit_regressions_ef11aa9d/verification.json'
    ready=ROOT/'outputs/runs/20261106T231955Z_readiness_fabe51a3/readiness.json'
    old=ROOT/'outputs/runs/20261106T152054Z_agronomic_input_priorities_release_a790f285/source_snapshot/configs'
    for name,digest in read(folder/'derived_files_sha256.json').items():assert sha256(folder/name)==digest
    d=read(ROOT/'configs/oveysi2010_input_dossier.json');report=read(folder/'verification.json')
    assert sha256(ROOT/d['source_pdf'])==d['source_pdf_sha256']==report['source_sha256']
    assert sha256(ROOT/'configs/oveysi2010_input_dossier.json')==report['config_sha256']
    fields={f['id']:f for f in d['fields']};assert len(fields)==17
    assert all(f['native_assignment_allowed'] is False for f in fields.values())
    pages=PdfReader(ROOT/d['source_pdf']).pages
    assert '1.63 g/cm' in pages[1].extract_text() and '38%' in pages[1].extract_text()
    assert fields['soil_bulk_density']['value']['reported_unit']=='g/cm2'
    assert fields['soil_bulk_density']['value']['corrected_unit_verified'] is False
    arithmetic=read(folder/'conditional_arithmetic.json')
    assert arithmetic['water_trigger_volumetric_percent']==dict(W1=33,W2=23)
    assert arithmetic['seasonal_water_mm']==dict(W1=750,W2=600)
    assert arithmetic['nitrogen_split_if_reported_maximum_applies_kg_ha']==[32,64,32]
    assert arithmetic['population_plants_ha']==70000 and arithmetic['subplot_area_m2']==26.25
    assert abs(arithmetic['Table1_May_Sep_precip_sum_mm']-24.8)<1e-10
    assert arithmetic['native_values_selected'] is False
    assert fields['nitrogen']['value']['dose_qualifier']=='maximum rate'
    assert fields['crop_period']['value']['harvest_year_explicit'] is False
    current=read(ROOT/'configs/oveysi2010_table4_grain.json')
    previous=read(old/'oveysi2010_table4_grain.json')
    assert current['rows']==previous['rows'] and current['reported_table3_grain_marginals']==previous['reported_table3_grain_marginals']
    sources=read(ROOT/'configs/agronomic_sources.json')['studies'];prior=read(old/'agronomic_sources.json')['studies']
    assert {s['id']:s['planned_role'] for s in sources}=={s['id']:s['planned_role'] for s in prior}
    study=next(s for s in sources if s['id']=='oveysi2010')
    assert independent_lineage_status(ROOT,study)['parameter_lineage_eligible'] is False
    plan=read(ROOT/'configs/agronomic_input_priorities.json')
    assert plan['work_queue'][0]['status']=='dossier_completed_quantitative_execution_blocked'
    assert plan['work_queue'][1]['status']=='next'
    assert read(priority)['registered_damage_scenarios']==28 and read(priority)['source_damage_contrasts']==16
    t=read(tests);r=read(ready)
    assert t['passed'] and t['tests_run']==204 and not(t['failures'] or t['errors'] or t['skipped'])
    assert r['research_ready'] is False and r['main_training_allowed'] is False and not r['quantitative_fit_ready_studies']
    assert r['agronomic_input_priority_sha256']==sha256(ROOT/'configs/agronomic_input_priorities.json')
    files=[folder/'verification.json',folder/'derived_files_sha256.json',priority,tests,ready,
        ROOT/'configs/oveysi2010_input_dossier.json',ROOT/'configs/oveysi2010_table4_grain.json',
        ROOT/'configs/agronomic_protocols.json',ROOT/'configs/agronomic_sources.json',ROOT/'configs/agronomic_input_priorities.json',
        ROOT/'scripts/build_oveysi_input_dossier.py',Path(__file__),ROOT/'docs/OVEYSI2010_INPUT_DOSSIER.md',
        ROOT/'docs/AGRONOMIC_INPUT_PRIORITIES.md',ROOT/'docs/NEXT_STEPS.md',ROOT/'PROGRESS.md']
    run=new_run(ROOT,'oveysi_input_dossier_release')
    write_json(run/'verification.json',dict(passed=True,source_located_fields=17,partial_or_unresolved_fields=14,
        observations_and_roles_unchanged=True,conditional_unit_arithmetic_checked=True,
        source_sha256_unchanged=True,old_workspace_empty=True,tests_run=204,
        new_native_simulations=0,new_training_runs=0,quantitative_fit_ready_studies=0,
        research_ready=False,main_training_allowed=False,
        evidence_sha256={str(p.relative_to(ROOT)):sha256(p) for p in files},
        scope='source-located dossier and explicit unresolved units/schedules; no field-model validation'))
    print(run)


if __name__=='__main__':main()
