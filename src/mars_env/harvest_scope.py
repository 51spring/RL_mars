"""Separate population-based residue arithmetic from actual harvest export."""
import math
from .sequence_audit import rounded_balance


def actual_export_boundary(h):
    fields=('grain_fraction','stover_fraction','canopy_dm','canopy_n','root_dm','root_n',
            'root_sen_dm','root_sen_n','all_grain_dm','grain_n','grain_dm','harvest_grain_n',
            'dead_leaf_dm_raw','residue_dm','residue_n')
    if any(k not in h or not math.isfinite(h[k]) or h[k]<0 for k in fields):
        raise ValueError('Missing or invalid native harvest stock')
    gf,sf=h['grain_fraction'],h['stover_fraction']
    if not 0<gf<=1 or not 0<=sf<=1:raise ValueError('Unsupported harvest fractions')
    before_dm=h['canopy_dm']+h['root_dm']+h['dead_leaf_dm_raw']+h['root_sen_dm']
    before_n=h['canopy_n']+h['root_n']+h['root_sen_n']
    # Mirrors the independently verified native BWAH formula. Byproduct N
    # has no native measurement and remains an explicitly declared allocation.
    byproduct_dm=(h['canopy_dm']-h['grain_dm']/gf+h['dead_leaf_dm_raw'])*sf
    byproduct_n=(h['canopy_n']-h['grain_n'])*sf
    after_dm=h['residue_dm']+h['grain_dm']+byproduct_dm
    after_n=h['residue_n']+h['harvest_grain_n']+byproduct_n
    checks={'dm':rounded_balance(after_dm,before_dm,abs(after_dm)+abs(before_dm)),
            'n':rounded_balance(after_n,before_n,abs(after_n)+abs(before_n))}
    expected_dm=h['all_grain_dm']*gf;expected_n=h['grain_n']*gf
    stock_checks={'dm':rounded_balance(h['grain_dm'],expected_dm,2*h['canopy_dm']),
                  'n':rounded_balance(h['harvest_grain_n'],expected_n,2*h['canopy_n'])}
    mismatch=not all(c['passed'] for c in stock_checks.values())
    boundary_passed=all(c['passed'] for c in checks.values())
    return {'actual_export_boundary':checks,'population_grain_export_checks':stock_checks,
            'population_export_mismatch':mismatch,'actual_export_boundary_passed':boundary_passed,
            'inferred_ears_to_population_dm_ratio':h['grain_dm']/expected_dm if expected_dm>0 else None,
            'inferred_ears_to_population_n_ratio':h['harvest_grain_n']/expected_n if expected_n>0 else None,
            'ratio_is_inferred_not_direct_ears_observation':True,
            'scope_qualified':boundary_passed and not mismatch and expected_dm>0,
            'byproduct_n_is_external_allocation':True,'byproduct_dm_kg_ha':byproduct_dm,
            'whole_ecosystem_balance_verified':False,'research_ready':False}
