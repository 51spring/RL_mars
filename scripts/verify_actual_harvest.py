"""Paired native execution of the v2 actual-yield harvest interface."""
import hashlib
import itertools
import json
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'docker'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.ear_diagnostics import EarProtocol
from mars_env.actual_harvest_contract import check_actual_contract
from mars_env.sequence_audit import analyze_handoff
from mars_env.harvest_accounting import harvest_summary
from verify_sequence_handoff import run_case
from verify_c_harvest_accounting import run_case as run_c
from verify_harvest_n_candidate import crop_trace,crop_output,independent_n
import patch_harvest_boundary,patch_sequence_audit,patch_harvest_n_inventory,patch_harvest_actual_exports


if __name__=='__main__':
    date_source=ROOT/'outputs/runs/20261106T032225Z_harvest_n_scope_90413cc2/verification.json'
    previous=json.loads(date_source.read_text());dates={(c['seed'],c['managed'],c['damage']):c['harvest_date'] for c in previous['c_date_sources']}
    run=new_run(ROOT,'actual_harvest_candidate');print(run,flush=True)
    source=ROOT/'vendor/dssat-pdi-source/Plant/CERES-Maize/MZ_CERES.for'
    expected=patch_harvest_actual_exports.patch(patch_harvest_n_inventory.patch(
        patch_sequence_audit.patch_crop(patch_harvest_boundary.patch(source.read_text()))))
    assert hashlib.sha256(expected.encode()).hexdigest()==sha256('/build/source/Plant/CERES-Maize/MZ_CERES.for')
    binaries={'control':'/opt/dssat_pdi/mars_ear_audit_dscsm048',
              'candidate':'/opt/dssat_pdi/mars_actual_harvest_dscsm048'}
    cases=[]
    for seed,managed,damage,mode,grain,stover in itertools.product([123456,456789],[False,True],
            [0.,.03],['Q','F'],[100,50],[0,100]):
        name=f'{mode}_{seed}_m{int(managed)}_d{damage}_g{grain}_s{stover}';pair={}
        for label,binary in binaries.items():
            os.environ['MARS_SEQUENCE_BINARY']=binary;folder=run/name/label
            d=run_case(folder,mode,grain,stover,damage,seed=seed,managed=managed,
                fallow_start=dates[(seed,managed,damage)],instrumentation=EarProtocol())
            h=d['harvests'][0];assert h['date']==dates[(seed,managed,damage)]
            assert abs(h['grain_fraction']-grain/100)<=2**-24 and abs(h['stover_fraction']-stover/100)<=2**-24
            ear=next(r for r in reversed(d['ear_records']) if r['dynamic']==6)
            d['v2_contract']=check_actual_contract(h,ear)
            d['handoff']=analyze_handoff(d)
            d['plant_n']=independent_n(folder,d)['plant_n']
            assert d['handoff']['handoff_passed']
            assert d['plant_n']['plant_n_inventory_balance_within_tolerance']
            if label=='candidate':assert d['v2_contract']['passed'],name
            header=next(l for l in (folder/'Summary.OUT').read_text().splitlines() if l.startswith('@') and 'HWAH' in l)
            summary=harvest_summary(header+'\n'+crop_output(folder,'Summary.OUT')[0])
            assert abs(summary['BWAH']-d['v2_contract']['byproduct_dm_kg_ha'])<=.5+2**-20*abs(summary['BWAH'])
            write_json(folder/'contract_diagnostics.json',d)
            for filename,digest in d['files'].items():assert sha256(folder/filename)==digest
            pair[label]=d
        # Direct observations also remain identical because only HRes inputs change.
        assert pair['control']['ear_records']==pair['candidate']['ear_records']
        assert pair['control']['barrenness_records']==pair['candidate']['barrenness_records']
        for filename in ('Summary.OUT','PlantGro.OUT','PlantN.OUT'):
            assert crop_output(run/name/'control',filename)==crop_output(run/name/'candidate',filename)
        assert crop_trace(run/name/'control')==crop_trace(run/name/'candidate')
        cases.append({'name':name,'seed':seed,'managed':managed,'damage':damage,'mode':mode,
            'grain_percent':grain,'stover_percent':stover,'control':pair['control']['v2_contract'],
            'candidate':pair['candidate']['v2_contract'],'first_crop_and_organ_records_exact':True})
        write_json(run/'partial_results.json',cases);print(name+' v2 paired checks passed',flush=True)
        import psutil
        # No simulator may survive the owned backend close between cases.
        assert not psutil.Process().children(recursive=True),'Simulator child leaked after paired close'
    c_cases=[]
    for seed,managed,damage in itertools.product([123456,456789],[False,True],[0.,.03]):
        results={}
        for label,binary in binaries.items():
            name=f'C_{seed}_m{int(managed)}_d{damage}_{label}'
            results[label]=run_c(run/name,seed,managed,damage,100,0,binary=binary)
        assert results['control']['harvest']==results['candidate']['harvest']
        for filename in ('Summary.OUT','PlantGro.OUT','PlantN.OUT'):
            assert crop_output(run/f'C_{seed}_m{int(managed)}_d{damage}_control',filename)==crop_output(run/f'C_{seed}_m{int(managed)}_d{damage}_candidate',filename)
        c_cases.append({'seed':seed,'managed':managed,'damage':damage,'C_harvest_reporting_exact':True})
        assert not psutil.Process().children(recursive=True),'Simulator child leaked after C close'
        print(f'C {seed} {managed} {damage} exact and cleaned',flush=True)
    write_json(run/'verification.json',{'passed':True,'qf_pairs':len(cases),'c_pairs':len(c_cases),
        'native_runs':2*(len(cases)+len(c_cases)),'cases':cases,'c_regressions':c_cases,
        'contract_version':'standing_stock_actual_yield_v2','date_source_sha256':sha256(date_source),
        'binary_sha256':{k:sha256(v) for k,v in binaries.items()},'vendor_sha256':sha256(source),
        'built_maize_source_sha256':sha256('/build/source/Plant/CERES-Maize/MZ_CERES.for'),
        'byproduct_n_is_defined_allocation':True,'default_crop_image_changed':False,
        'shared_backend_lifecycle_hardened':True,
        'no_simulator_children_after_every_pair':True,
        'whole_ecosystem_balance_verified':False,'independent_agronomic_validation':False,'research_ready':False})
