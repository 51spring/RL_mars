"""Experimental standing-stock/actual-yield harvest accounting contract."""
import math
from .sequence_audit import rounded_balance
from .ear_diagnostics import verify_organ_record


def check_actual_contract(h,ear):
    if ear['dynamic']!=6 or ear['date']!=h['date']:
        raise ValueError('Expected same-day native season-end organ measurement')
    if not all(math.isfinite(float(v)) for v in (*h.values(),*ear.values())):
        raise ValueError('Nonfinite harvest measurements')
    if ear['population']<=0 or ear['stovwt']<=1e-5:
        raise ValueError('Zero population/stover remains outside candidate domain')
    gf,sf=h['grain_fraction'],h['stover_fraction']
    if not 0<gf<=1 or not 0<=sf<=1:raise ValueError('Unsupported harvest fraction')
    organs=verify_organ_record(ear)
    expected={
        'dm':(h['canopy_dm']+h['dead_leaf_dm_raw']-ear['yield'])*(1-sf)
              +ear['yield']*(1-gf)+h['root_dm']+h['root_sen_dm'],
        'n':(h['canopy_n']-ear['gnup'])*(1-sf)+ear['gnup']*(1-gf)+h['root_n']+h['root_sen_n']}
    checks={key:rounded_balance(h['residue_'+key],value,abs(h['residue_'+key])+abs(value))
            for key,value in expected.items()}
    checks['reported_grain_dm']=rounded_balance(h['grain_dm'],ear['yield']*gf,2*h['canopy_dm'])
    checks['reported_grain_n']=rounded_balance(h['harvest_grain_n'],ear['gnup']*gf,2*h['canopy_n'])
    by_dm=(h['canopy_dm']+h['dead_leaf_dm_raw']-ear['yield'])*sf
    by_n=(h['canopy_n']-ear['gnup'])*sf
    before_dm=h['canopy_dm']+h['dead_leaf_dm_raw']+h['root_dm']+h['root_sen_dm']
    before_n=h['canopy_n']+h['root_n']+h['root_sen_n']
    checks['export_boundary_dm']=rounded_balance(h['residue_dm']+h['grain_dm']+by_dm,before_dm,2*before_dm)
    checks['export_boundary_n']=rounded_balance(h['residue_n']+h['harvest_grain_n']+by_n,before_n,2*before_n)
    return {'contract_version':'standing_stock_actual_yield_v2','checks':checks,
        'passed':organs['passed'] and all(c['passed'] for c in checks.values()),
        'byproduct_dm_kg_ha':by_dm,'byproduct_n_kg_ha':by_n,
        'byproduct_n_is_defined_allocation_not_native_measurement':True,
        'direct_ears_to_population':ear['ears']/ear['population'],
        'research_ready':False,'whole_ecosystem_balance_verified':False}
