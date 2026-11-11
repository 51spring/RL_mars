"""Reproducible source-located Oveysi inputs, conditional arithmetic and blockers."""
import json
from pathlib import Path
import shutil
import sys
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.agronomic_scenarios import build_registry,source_contrasts
from mars_env.validation_lineage import independent_lineage_status


def main():
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    config=ROOT/'configs/oveysi2010_input_dossier.json';d=read(config)
    pdf=ROOT/d['source_pdf'];assert sha256(pdf)==d['source_pdf_sha256']
    source_info=read(pdf.parent/'source.json');assert source_info['sha256']==sha256(pdf)
    fields={f['id']:f for f in d['fields']};assert len(fields)==len(d['fields'])==17
    assert all(f['native_assignment_allowed'] is False for f in fields.values())
    assert d['native_execution_allowed'] is False and d['calibration_allowed'] is False
    pages=PdfReader(pdf).pages;assert len(pages)==6
    for f in fields.values():assert 1<=f['locator']['pdf_page']<=6 and f['locator']['printed_page']==475+f['locator']['pdf_page']
    # Anchors detect a different document, not a replacement for visual unit/number verification.
    assert 'SC704' in pages[1].extract_text() and '7500' in pages[2].extract_text()
    assert '2007' in pages[2].extract_text() and 'Duncan' in pages[2].extract_text()
    water=fields['soil_water_characteristics']['value'];protocol=fields['irrigation_protocol']['value']
    fc,wp=water['field_capacity_volumetric_percent'],water['wilting_point_volumetric_percent']
    w1=wp+protocol['W1_available_water_fraction_trigger']*(fc-wp)
    w2=wp+protocol['W2_available_water_fraction_trigger']*(fc-wp)
    assert w1==33 and w2==23
    nitrogen=fields['nitrogen']['value'];total=sum(nitrogen['reported_N_contributions_kg_ha'])
    assert total==128 and sum(nitrogen['fractions'])==1
    geometry=fields['planting_geometry']['value'];climate=fields['climate_basis_difference']['value']
    conditional=dict(latitude_decimal=35+19/60,longitude_decimal=51+39/60,
        water_trigger_volumetric_percent=dict(W1=w1,W2=w2),
        seasonal_water_mm={k:v*.1 for k,v in fields['seasonal_irrigation']['value']['reported_m3_ha'].items()},
        nitrogen_split_if_reported_maximum_applies_kg_ha=[total*f for f in nitrogen['fractions']],
        population_plants_ha=geometry['plants_m2']*10000,subplot_area_m2=geometry['subplot_width_m']*geometry['subplot_length_m'],
        Table1_May_Sep_precip_sum_mm=sum(climate['Table1_May_Sep_precip_mm']),
        arithmetic_only=True,source_basis_conflicts_resolved=False,native_values_selected=False)
    observation=read(ROOT/'configs/oveysi2010_table4_grain.json')
    assert len(observation['rows'])==10 and not observation['standard_errors_available']
    registry=read(ROOT/'configs/agronomic_sources.json')['studies']
    study=next(s for s in registry if s['id']=='oveysi2010')
    assert study['planned_role']==d['planned_role']
    scenarios=build_registry(ROOT);oveysi=[s for s in scenarios if s['study_id']=='oveysi2010']
    contrasts=[c for c in source_contrasts(scenarios) if c['study_id']=='oveysi2010']
    assert len(oveysi)==10 and len(contrasts)==8
    lineage=independent_lineage_status(ROOT,study);assert lineage['parameter_lineage_eligible'] is False
    run=new_run(ROOT,'oveysi_input_dossier');print(run,flush=True)
    write_json(run/'source_located_fields.json',d)
    write_json(run/'conditional_arithmetic.json',conditional)
    write_json(run/'blocked_inputs.json',dict(blockers=[dict(field=f['id'],status=f['status'],locator=f['locator']) for f in fields.values() if f['status'] not in ('reported','endpoint_basis_verified')],
        lineage=lineage,no_automatic_input_export=True,no_automatic_model_or_policy_validation=True,
        study_split_unit='wholeOveysi2010study; no calibration on outcomes',
        table4_year_basis='combined analysis context; no year-specific means/covariance acquired',
        numeric_model_acceptance_tolerance=None,source_mean_comparison_not_a_validation_score=True))
    write_json(run/'source_pages.json',[dict(pdf_page=i+1,printed_page=476+i,text=p.extract_text()) for i,p in enumerate(pages)])
    for n in ('oveysi-input-methods-2.png','oveysi-input-methods-3.png'):shutil.copy2(ROOT/'outputs'/n,run/n)
    report=dict(passed=True,study_id=d['study_id'],source_located_fields=17,
        partial_or_unresolved_fields=sum(f['status'] not in ('reported','endpoint_basis_verified') for f in fields.values()),
        source_joint_means=10,registered_scenarios=10,source_contrasts=8,
        water_triggers_verified_arithmetic_percent=[w1,w2],reported_seasonal_irrigation_mm=[750,600],
        dose_basis_preserved_as_maximum=True,bulk_density_unit_unresolved=True,
        daily_weather_missing=True,year_specific_joint_means_acquired=False,
        source_sha256=sha256(pdf),config_sha256=sha256(config),
        role_changed=False,quantitative_fit_ready=False,new_native_simulations=0,new_training_runs=0,
        research_ready=False,main_training_allowed=False,
        scope='source-located inputs and conditional arithmetic; no completed profile/schedule/uncertainty or field-model validation')
    write_json(run/'verification.json',report)
    write_json(run/'derived_files_sha256.json',{p.name:sha256(p) for p in run.iterdir() if p.is_file()})
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
