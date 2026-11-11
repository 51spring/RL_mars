"""Native Q/F handoff plus independent inventory; never apply withdrawn adapter."""
import argparse
import hashlib
import itertools
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run, write_json, sha256
from mars_env.sequence_audit import analyze_handoff
from verify_sequence_handoff import run_case


def validate_result(result):
    h=result['harvests'][0]
    for key,target in [('grain_fraction',result['grain_percent']/100),('stover_fraction',result['stover_percent']/100)]:
        assert abs(h[key]-target)<=2**-24,(key,'input not honored')
    analysis=analyze_handoff(result)
    assert analysis['handoff_passed']
    assert analysis['partition']['residue_dm']['passed']
    n=analysis['partition']['residue_n']
    assert abs(n['residual']-analysis['predicted_native_duplicate_n'])<=n['binary32_roundoff_bound']
    return analysis


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--matrix',action='store_true')
    args=parser.parse_args()
    os.environ['MARS_SEQUENCE_BINARY']='/opt/dssat_pdi/mars_sequence_audit_dscsm048'
    run=new_run(ROOT,'sequence_inventory_reaudit');print(run,flush=True)
    sys.path.insert(0,str(ROOT/'docker'))
    import patch_harvest_boundary,patch_sequence_audit
    fingerprints={}
    for relative in ['Plant/CERES-Maize/MZ_CERES.for','Soil/CERES_OrganicMatter/SoilOrg_init.for']:
        p=ROOT/'vendor/dssat-pdi-source'/relative;original=p.read_text(encoding='latin-1')
        expected=(patch_sequence_audit.patch_crop(patch_harvest_boundary.patch(original))
                  if 'MZ_CERES' in relative else patch_sequence_audit.patch_soil(original))
        expected_hash=hashlib.sha256(expected.encode('latin-1')).hexdigest()
        assert expected_hash==sha256(Path('/build/source')/relative)
        fingerprints[relative]={'vendor_sha256':sha256(p),'built_sha256':expected_hash}
    specs=itertools.product(['Q','F'],[100,50],[0,50,100],[0.,.03]) if args.matrix else [('Q',100,0,0.)]
    cases=[]
    for mode,grain,stover,damage in specs:
        name=f'{mode}_g{grain}_s{stover}_d{damage}'
        result=run_case(run/name,mode,grain,stover,damage)
        result['analysis']=validate_result(result)
        write_json(run/name/'diagnostics.json',result)
        for filename,digest in result['files'].items():assert sha256(run/name/filename)==digest
        cases.append({'name':name,'analysis':result['analysis']})
        print(name+' transfer audited; conservation separately reported',flush=True)
    write_json(run/'verification.json',{'passed':True,
        'scope':'native transfer and identification of N duplication, not physical N closure',
        'native_runs':len(cases),'cases':cases,'source_fingerprints':fingerprints,
        'binary_sha256':sha256('/opt/dssat_pdi/mars_sequence_audit_dscsm048'),
        'native_n_partition_conservation_verified':False,'unit_adapter_withdrawn':True,
        'supersedes':'20261106T020048Z_sequence_handoff_7b592b1e','research_ready':False})
