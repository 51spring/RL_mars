"""Pin source/diagnostic outputs and no-promotion release scope."""
import csv
from fractions import Fraction
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256

def main():
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    source=ROOT/'outputs/runs/20261107T011325Z_kenya_public_dataset_f18ec4ef'
    folder=ROOT/'outputs/runs/20261107T011553Z_kenya_input_audit_4f7c8ce1'
    acquisition=read(source/'verification.json')
    assert acquisition['listed_files']==acquisition['acquired_files']==20
    for f in acquisition['files']:
        assert sha256(source/f['local_file'])==f['sha256']
        assert (source/f['local_file']).stat().st_size==f['declared_size']
    for name,digest in read(folder/'derived_files_sha256.json').items():assert sha256(folder/name)==digest
    table=next(f for f in acquisition['files'] if f['filename'].startswith('18_'))
    with (source/table['local_file']).open(encoding='utf-8-sig',newline='') as f:failure=list(csv.DictReader(f))
    assert len(failure)==75
    assert sum(int(r['Plots']) for r in failure)==225
    assert sum(int(r['Grain-failure plots']) for r in failure)==53
    for r in failure:
        exact=Fraction(int(r['Grain-failure plots']),int(r['Plots']))
        assert abs(exact-Fraction(r['Grain-failure proportion']))<=Fraction(1,10**9)
        assert int(r['Plots with grain'])+int(r['Grain-failure plots'])==int(r['Plots'])
    inventory=read(folder/'csv_inventory.json')
    assert len(inventory)==20 and sum(r['rows'] for r in inventory)==2538
    assert not any(r['raw_plot_grain_yield'] or r['daily_weather'] for r in inventory)
    report=read(folder/'verification.json')
    for key in ('rainfall_difference_flags','rainfall_date_range_flags','source_date_order_flags',
                'failure_identity_flags','failure_fraction_flags','contrast_t_review_flags','contrast_t_uncomputable','covariance_argmin_flags'):
        assert report[key]==0
    assert report['contrast_t_checks']==602 and report['AIC_BIC_disagreements']==6
    assert report['raw_plot_grain_yield_acquired'] is False and report['daily_weather_acquired'] is False
    prior=ROOT/'outputs/runs/20261107T005758Z_iran_protocol_dossier_release_dc82b118/source_snapshot'
    production=list((ROOT/'src').rglob('*.py'))
    assert all(sha256(p)==sha256(prior/p.relative_to(ROOT)) for p in production)
    assert sha256(ROOT/'configs/agronomic_sources.json')==sha256(prior/'configs/agronomic_sources.json')
    ready=ROOT/'outputs/runs/20261107T011714Z_readiness_5e054a38/readiness.json'
    priority=ROOT/'outputs/runs/20261107T011714Z_agronomic_input_priorities_bf911dc1/verification.json'
    r=read(ready)
    assert r['public_studies']==10 and not r['research_ready'] and not r['main_training_allowed'] and not r['quantitative_fit_ready_studies']
    assert r['agronomic_input_priority_sha256']==sha256(ROOT/'configs/agronomic_input_priorities.json')
    files=[source/'verification.json',folder/'verification.json',folder/'derived_files_sha256.json',ready,priority,
        ROOT/'configs/agronomic_sources.json',ROOT/'configs/agronomic_input_priorities.json',ROOT/'configs/field_calibration_candidate_screen.json',
        ROOT/'docs/KENYA_INPUT_AUDIT.md',ROOT/'docs/NEXT_STEPS.md',ROOT/'docs/AGRONOMIC_INPUT_PRIORITIES.md',
        ROOT/'docs/FIELD_CALIBRATION_CANDIDATE_SCREEN.md',ROOT/'scripts/fetch_kenya_public_dataset.py',
        ROOT/'scripts/audit_kenya_public_dataset.py',Path(__file__),ROOT/'PROGRESS.md']
    run=new_run(ROOT,'kenya_input_audit_release')
    write_json(run/'verification.json',dict(passed=True,scope='source file identity and arithmetic audit; no raw-grain/model qualification',
        source_file_hashes_verified=20,rational_failure_fraction_checks=75,
        raw_plot_grain_yield_acquired=False,daily_weather_acquired=False,
        production_python_files_unchanged=len(production),active_registry_unchanged=True,old_workspace_empty=True,
        new_tests_run=0,previous_tests_passed=204,new_native_simulations=0,new_training_runs=0,
        quantitative_fit_ready_studies=0,research_ready=False,main_training_allowed=False,
        evidence_sha256={p.relative_to(ROOT).as_posix():sha256(p) for p in files}))
    print(run)

if __name__=='__main__':main()
