"""External C-mode boundary allocation; never mutates native crop/soil stocks."""
import math
import re
from .dssat_backend import BackendContractError
from .sequence_audit import rounded_balance


def c_harvest_allocation(h):
    required=('rnmode','canopy_dm','canopy_n','root_dm','root_n','all_grain_dm',
              'grain_n','grain_dm','harvest_grain_n','dead_leaf_dm_raw',
              'grain_fraction','stover_fraction','residue_dm','residue_n')
    if any(k not in h or not math.isfinite(float(h[k])) or h[k]<0 for k in required):
        raise BackendContractError('Missing or invalid harvest inventory')
    if int(h['rnmode'])!=ord('C') or h['residue_dm']!=0 or h['residue_n']!=0:
        raise BackendContractError('Expected unmodified C-mode zero native HARVRES')
    gf,sf=h['grain_fraction'],h['stover_fraction']
    if not 0<gf<=1 or sf>1 or h['all_grain_dm']>h['canopy_dm'] or h['grain_n']>h['canopy_n']:
        raise BackendContractError('Invalid harvest fraction or grain stock')
    # Actual yield uses EARS, whereas the stock diagnostic uses PLTPOP. They
    # can differ in stressed crops. Use actual reported exports, not a
    # silently substituted GRNWT*PLTPOP yield. This interface requires gf>0.
    non_grain_dm=h['canopy_dm']-h['grain_dm']/gf+h['dead_leaf_dm_raw']
    # Canopy N already contains the tracked senesced-leaf N.
    non_grain_n=h['canopy_n']-h['grain_n']
    before={'dry_matter_kg_ha':h['canopy_dm']+h['root_dm']+h['dead_leaf_dm_raw'],
            'nitrogen_kg_ha':h['canopy_n']+h['root_n']}
    grain={'dry_matter_kg_ha':h['grain_dm'],'nitrogen_kg_ha':h['harvest_grain_n']}
    byproduct={'dry_matter_kg_ha':non_grain_dm*sf,'nitrogen_kg_ha':non_grain_n*sf}
    retained={k:before[k]-grain[k]-byproduct[k] for k in before}
    if any(v<0 for v in retained.values()):raise BackendContractError('Exports exceed measured inventory')
    checks={k:rounded_balance(grain[k]+byproduct[k]+retained[k],v,2*v) for k,v in before.items()}
    if not all(c['passed'] for c in checks.values()):raise BackendContractError('Harvest allocation does not match native grain')
    stock_fraction_checks={
        'dm':rounded_balance(h['grain_dm'],h['all_grain_dm']*gf,2*h['canopy_dm']),
        'n':rounded_balance(h['harvest_grain_n'],h['grain_n']*gf,2*h['canopy_n'])}
    return {'before':before,'grain_export':grain,'byproduct_export':byproduct,'retained':retained,
            'checks':checks,'requested_fraction_of_population_grain_stock':stock_fraction_checks,
            'byproduct_n_is_external_allocation_not_native_export_measurement':True,
            'dead_leaf_dm_unit':'kg dry matter/ha',
            'dead_leaf_n_counted_twice':False,'native_state_transition_executed':False,
            'native_C_mode_residue_transfer':False,'scope':'external terminal allocation only; no soil restart',
            'whole_postharvest_system_balance_verified':False,'elemental_carbon_verified':False,
            'research_ready':False}


def harvest_summary(text):
    header=None;rows=[]
    for line in text.splitlines():
        if line.startswith('@') and 'HWAH' in line:header=list(re.finditer(r'\S+',line))
        elif header and re.match(r'^\s*\d+\s',line):rows.append(line)
    if not header or len(rows)!=1:raise BackendContractError('Expected one C-mode harvest summary')
    result={}
    for i,m in enumerate(header):
        if m.group() in ('HWAH','BWAH','CWAM','CNAM','GNAM'):
            result[m.group()]=float(rows[0][header[i-1].end():m.end()].strip())
    if set(result)!= {'HWAH','BWAH','CWAM','CNAM','GNAM'}:
        raise BackendContractError('Missing harvest output fields')
    return result
