"""Paired real Q/F native runs against independent N input and export stocks."""
import hashlib
import itertools
import json
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'docker'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.sequence_audit import analyze_handoff,rounded_balance
from mars_env.balances import NitrogenInventoryDiagnostic,RemovalLedger
from verify_sequence_handoff import run_case
from verify_c_harvest_accounting import run_case as run_c
import patch_harvest_boundary,patch_sequence_audit,patch_harvest_n_inventory

BINARIES={'native':'/opt/dssat_pdi/mars_sequence_audit_dscsm048',
          'candidate':'/opt/dssat_pdi/mars_harvest_n_candidate_dscsm048'}


def independent_n(folder,result):
    trace=json.loads((folder/'trace.json').read_text())
    inventory=NitrogenInventoryDiagnostic();removal=RemovalLedger()
    for before,after in zip(trace,trace[1:]):
        date=int(before['yrdoy'])
        if len(before['mars_sequence_harvests']) or date<1982057:continue
        inventory.append(date,after['mars_plant_audit'])
        record=after.get('mars_leaf_diagnostic')
        if record and record['yrdoy']==date:removal.append(record)
    assert inventory.summary()['plant_n_inventory_balance_within_tolerance']
    h=result['harvests'][0]
    # This reference starts from measured plant stocks, actual reported grain
    # export, and a declared byproduct N allocation; not SENESCE + STOVN.
    before=h['canopy_n']+h['root_n']+h['root_sen_n']
    byproduct=(h['canopy_n']-h['grain_n'])*h['stover_fraction']
    after=h['residue_n']+h['harvest_grain_n']+byproduct
    boundary=rounded_balance(after,before,abs(after)+abs(before))
    return {'plant_n':inventory.summary(),'damage':removal.summary(),
            'actual_export_boundary_n':boundary,
            'byproduct_n_is_inventory_allocation':True,'pending_root_sen_n_counted_once':True}


def crop_trace(folder):
    trace=json.loads((folder/'trace.json').read_text())
    return [{k:v for k,v in s.items() if k not in ('mars_sequence_harvests','mars_sequence_soils','mars_harvest_boundary')}
            for s in trace if len(s['mars_sequence_harvests'])==0]


def crop_output(folder,filename):
    rows=[l for l in (folder/filename).read_text().splitlines() if l.strip() and l.lstrip()[0].isdigit()]
    return [l for l in rows if l.split()[5]=='MZ'] if filename=='Summary.OUT' else rows


if __name__=='__main__':
    run=new_run(ROOT,'harvest_n_candidate');print(run,flush=True)
    source=ROOT/'vendor/dssat-pdi-source/Plant/CERES-Maize/MZ_CERES.for'
    expected=patch_harvest_n_inventory.patch(patch_sequence_audit.patch_crop(patch_harvest_boundary.patch(source.read_text())))
    expected_hash=hashlib.sha256(expected.encode()).hexdigest()
    assert expected_hash==sha256('/build/source/Plant/CERES-Maize/MZ_CERES.for')
    cases=[]
    for mode,grain,stover,damage in itertools.product(['Q','F'],[100,50],[0,50,100],[0.,.03]):
        name=f'{mode}_g{grain}_s{stover}_d{damage}';pair={}
        for label,binary in BINARIES.items():
            os.environ['MARS_SEQUENCE_BINARY']=binary
            folder=run/name/label
            result=run_case(folder,mode,grain,stover,damage)
            h=result['harvests'][0]
            assert abs(h['grain_fraction']-grain/100)<=2**-24
            assert abs(h['stover_fraction']-stover/100)<=2**-24
            result['analysis']=analyze_handoff(result)
            result['independent_n']=independent_n(folder,result)
            assert result['analysis']['handoff_passed']
            assert result['analysis']['partition']['residue_dm']['passed']
            if label=='candidate':
                assert result['analysis']['partition_passed']
                assert result['independent_n']['actual_export_boundary_n']['passed']
            else:
                n=result['analysis']['partition']['residue_n']
                assert abs(n['residual']-result['analysis']['predicted_native_duplicate_n'])<=n['binary32_roundoff_bound']
            write_json(folder/'diagnostics.json',result)
            for filename,digest in result['files'].items():assert sha256(folder/filename)==digest
            pair[label]=result
        assert crop_trace(run/name/'native')==crop_trace(run/name/'candidate')
        for filename in ('Summary.OUT','PlantGro.OUT','PlantN.OUT'):
            assert crop_output(run/name/'native',filename)==crop_output(run/name/'candidate',filename)
        for field,value in pair['native']['harvests'][0].items():
            if field!='residue_n':assert value==pair['candidate']['harvests'][0][field],field
        cases.append({'name':name,'native':pair['native']['analysis'],'candidate':pair['candidate']['analysis'],
            'independent_n':pair['candidate']['independent_n'],'first_crop_exact':True})
        write_json(run/'partial_results.json',cases);print(name+' paired checks passed',flush=True)
    c_cases=[]
    for seed,damage in itertools.product([123456,456789],[0.,.03]):
        pair={}
        for label,binary in BINARIES.items():
            folder=run/f'C_{seed}_{damage}_{label}'
            result=run_c(folder,seed,seed==123456,damage,100,0,binary=binary)
            pair[label]=result
        assert pair['native']['harvest']==pair['candidate']['harvest']
        for filename in ('Summary.OUT','PlantGro.OUT','PlantN.OUT'):
            assert crop_output(run/f'C_{seed}_{damage}_native',filename)==crop_output(run/f'C_{seed}_{damage}_candidate',filename)
        c_cases.append({'seed':seed,'damage':damage,'native_harvest_and_numeric_outputs_exact':True})
        print(f'C {seed} {damage} exact',flush=True)
    write_json(run/'verification.json',{'passed':True,'qf_pairs':len(cases),'c_pairs':len(c_cases),
        'native_runs':len(cases)*2+len(c_cases)*2,'cases':cases,'c_regressions':c_cases,
        'vendor_sha256':sha256(source),'built_maize_source_sha256':expected_hash,
        'binary_sha256':{k:sha256(v) for k,v in BINARIES.items()},
        'scope':'UFGA managed maize harvest N partition and immediate fallow handoff; C regression',
        'candidate_only':True,'default_training_runtime_changed':False,
        'whole_postharvest_ecosystem_balance_verified':False,'whole_elemental_carbon_verified':False,
        'independent_agronomic_validation':False,'research_ready':False})
