"""Evidence index and fail-closed research status, without rewriting old reports."""
import json
from pathlib import Path
import sys
import yaml
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256

# Gates moved to documented limitations by the user on 2026-11-11 (decision_project.md section 20):
# each needs data or model output that is not available, so it cannot be passed by more work here.
# The result scope written next to each gate must be stated with any reported result.
RECLASSIFIED_LIMITATIONS={
    'whole_elemental_carbon_and_crop_soil_n_balance':{
        'why_unprovable':'CERES-Maize does not output crop carbon terms (stock, seed, gross assimilation, respiration, harvest, damage export); '
                         'closing the balance needs Fortran instrumentation plus a dry-matter-to-carbon assumption, and no public field carbon '
                         'series sets the tolerance',
        'result_scope':'profit and yield comparisons only; no crop or ecosystem carbon balance claim'},
    'native_qf_n_partition_conservation':{
        'why_unprovable':'native multi-year Q/F accounting double-counts senesced leaf N when byproduct remains; fixing it changes the vendor crop '
                         'model and voids earlier checks, and printed rounding hides the differences',
        'result_scope':'single-season runs only; the comparison does not use Q/F modes'},
    'harvest_n_candidate_domain_expansion':{
        'why_unprovable':'the separate actual-export harvest candidate fails closure in 32 no-input cases; widening it needs a redesigned harvest '
                         'export and field residue-N data that are not available',
        'result_scope':'grain yield from native HWAH; the candidate image is not used'},
    'independent_agronomic_recovery':{
        'why_unprovable':'frozen tier B failed at 99 % defoliation (V8, V13); improving DSSAT recovery needs crop-model changes and another '
                         'independent defoliation trial',
        'result_scope':'pest damage interpreted within 33-66 % defoliation; H3 stays exploratory'},
    'independent_parameter_lineage':{
        'why_unprovable':'calibration data, years and plots behind cultivar IB0035 coefficients are not published, so independence of evaluation '
                         'observations cannot be shown from fixed records',
        'result_scope':'results are conditional on the current cultivar coefficients; tier A (SIAZ 1995 independent-year water response) is partial support'},
}


def main():
    config=yaml.safe_load((ROOT/'configs/proposal_v2.yaml').read_text(encoding='utf-8'))
    sources=json.loads((ROOT/'configs/agronomic_sources.json').read_text(encoding='utf-8'))
    evidence=[]
    qualifications=json.loads((ROOT/'configs/evidence_qualifications.json').read_text(encoding='utf-8'))
    paths=list((ROOT/'outputs/runs').glob('*/verification.json'))+list((ROOT/'outputs/runs').glob('*/failure.json'))
    paths += [ROOT/'outputs'/name for name in ('core_test_results.json','native_leaf_verification.json',
             'season_balance_online_verification.json','real_reward_verification.json')]
    for path in sorted(paths):
        data=json.loads(path.read_text(encoding='utf-8-sig'))
        qualification=qualifications.get(path.parent.name,{})
        originally_passed=data.get('passed',data.get('diagnostic_pipeline_passed',False))
        evidence.append({'path':path.relative_to(ROOT).as_posix(),'sha256':sha256(path),
            'passed':originally_passed and qualification.get('status')!='withdrawn',
            'historically_reported_passed':originally_passed,'qualification':qualification,
            'scope':path.parent.name if path.parent.name!='outputs' else path.stem})
    from mars_env.validation_lineage import independent_lineage_status
    lineage=[independent_lineage_status(ROOT,s) for s in sources['studies']]
    # Field-validation gates follow configs/field_validation_tiers.json (adopted 2026-11-10).
    from mars_env.field_validation import tier_gate_status
    tiers=json.loads((ROOT/'configs/field_validation_tiers.json').read_text(encoding='utf-8'))
    primary=tiers['tiers']['A_undamaged_water_response']['primary']
    judgment=None
    if primary.get('judgment'):
        judgment_path=(ROOT/primary['judgment']).resolve()
        if judgment_path.is_relative_to(ROOT) and judgment_path.is_file() and sha256(judgment_path)==primary['judgment_sha256']:
            judgment=json.loads(judgment_path.read_text(encoding='utf-8'))
    field=tier_gate_status(tiers,judgment)
    pending=['whole_elemental_carbon_and_crop_soil_n_balance','native_qf_n_partition_conservation',
        'harvest_n_candidate_domain_expansion',*field['pending'],
        'validation_tuned_baselines','fixed_reduction_calendar_and_preregistered_contrasts',
        'independent_parameter_lineage']
    pending=[gate for gate in pending if gate not in RECLASSIFIED_LIMITATIONS]
    run=new_run(ROOT,'readiness')
    report={'research_ready':False,'main_training_allowed':False,'pending_gates':pending,
        'satisfied_field_validation_gates':field['satisfied'],
        'documented_limitations_not_gating':field['documented_limitations']+list(RECLASSIFIED_LIMITATIONS),
        'reclassified_limitations':RECLASSIFIED_LIMITATIONS,
        'field_validation_tier_config':'configs/field_validation_tiers.json',
        'field_validation_tier_sha256':sha256(ROOT/'configs/field_validation_tiers.json'),
        'field_validation_claim_scope':tiers['claim_scope'],
        'independent_parameter_lineage':lineage,
        'agronomic_input_priority_config':'configs/agronomic_input_priorities.json',
        'agronomic_input_priority_sha256':sha256(ROOT/'configs/agronomic_input_priorities.json'),
        'unset_parameters':[key for key in ('temperature_low_c','temperature_high_c','survey_noise_std') if config['pest'][key] is None],
        'evidence':evidence,'public_studies':len(sources['studies']),
        'quantitative_fit_ready_studies':[s['id'] for s in sources['studies'] if s['quantitative_fit_ready']],
        'note':'Evidence indexing is not agronomic validation; do not enable gates from software tests or metadata alone'}
    write_json(run/'readiness.json',report);print(run);print(json.dumps({k:v for k,v in report.items() if k!='evidence'},indent=2))


if __name__=='__main__':main()
