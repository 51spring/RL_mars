"""Independent daily crop/soil N inventory with explicit scheduler liabilities.

No fitted offsets, inferred missing fluxes, or whole-C validation are supplied.
"""
import math
import re
from pathlib import Path
from .audits import shift_yrdoy,management_events
from .soil_audit import precision

ORGANIC=('HUMN','FON','RESN')
INORGANIC=('NO3','NH4','TUREA','TNGAS','FLOODN','ALGFIX','UNFERT')
LOSSES=('RLCH','RLTD','RNRO','RAML','N2OED','N2ED','NOED')


def run_tables(text,*,expected_runs=(1,2)):
    result={};run=None;header=None
    for line in text.splitlines():
        m=re.match(r'^\*RUN\s+(\d+)',line)
        if m:
            run=int(m.group(1));header=None
            if run in result:raise ValueError('Repeated native run')
            result[run]=[]
        if line.startswith('@YEAR'):
            if run is None:raise ValueError('Native rows need run identity')
            header=line[1:].split()
        elif header and re.match(r'^\s*\d{4}\s+\d{3}\s',line):
            tokens=line.split()
            if len(tokens)!=len(header):raise ValueError('Malformed native N table')
            if not all(math.isfinite(float(t)) for t in tokens):raise ValueError('Nonfinite native N table')
            row=dict(zip(header,tokens));date=int(row['YEAR'])*1000+int(row['DOY'])
            if result[run]:
                old=result[run][-1];prev=int(old['YEAR'])*1000+int(old['DOY'])
                if date!=shift_yrdoy(prev,1):raise ValueError('Nonconsecutive soil dates')
            if int(row['DAS'])!=len(result[run]):raise ValueError('Nonconsecutive native DAS')
            result[run].append(row)
    if set(result)!=set(expected_runs) or not all(result.values()):raise ValueError('Unexpected/missing native N runs')
    return result


def stock(organic,inorganic):
    values=[organic[k] for k in ORGANIC]+[inorganic[k] for k in INORGANIC]
    if any(float(v)<0 for v in values):raise ValueError('Negative soil N stock')
    return sum(map(float,values)),sum(precision(v) for v in values)


def analyze_integrated_n(folder,diagnostics,trace):
    folder=Path(folder)
    organic=run_tables((folder/'SoilNoBal.OUT').read_text())
    inorganic=run_tables((folder/'SoilNiBal.OUT').read_text())
    h=diagnostics['harvests'][0];harvest_date=int(h['date']);states={};fertilizer={};uptake={};uptake_bounds={}
    for before,after in zip(trace,trace[1:]):
        if len(before['mars_sequence_harvests']):continue
        date=int(before['yrdoy'])
        if date in states:raise ValueError('Repeated maize state date')
        states[date]=after['mars_plant_audit']
        old_uptake=before['mars_plant_audit']['wtnup'];new_uptake=after['mars_plant_audit']['wtnup']
        uptake[date]=10*(new_uptake-old_uptake)
        uptake_bounds[date]=8*2**-24*10*(abs(new_uptake)+abs(old_uptake))
        dap=int(before['dap'])
        amount={40:27.,45:35.,80:54.}.get(dap,0.) if diagnostics['managed'] and date>=1982057 else 0.
        if amount:fertilizer[date]=amount
    expected_dates={int(r['YEAR'])*1000+int(r['DOY']) for r in organic[1] if int(r['DAS'])>0}
    if set(states)!=expected_dates:raise ValueError('Crop trace and maize soil calendar coverage differ')
    native_fert=[(date,amount) for date,kind,amount in management_events((folder/'MgmtEvent.OUT').read_text()) if kind=='Fertilizer']
    if sorted(native_fert)!=sorted(fertilizer.items()):raise ValueError('Actions and native fertilizer events differ')
    final=states[harvest_date]
    if abs(final['root_sen_n'])>1e-10 or abs(uptake[harvest_date])>1e-10:
        raise ValueError('Harvest pending transfers nonzero; this boundary requires separate coverage')
    allocation=diagnostics['v2_contract'];harvest_export=h['harvest_grain_n']+allocation['byproduct_n_kg_ha']
    initial,initial_bound=stock(organic[1][0],inorganic[1][0])
    loss=loss_bound=fert=0.;rows=[];max_timing=0.;max_root_timing=0.;timing_checks=0
    for run in (1,2):
        if len(organic[run])!=len(inorganic[run]):raise ValueError('Organic/inorganic day count differs')
        for o,n in zip(organic[run],inorganic[run]):
            date=int(o['YEAR'])*1000+int(o['DOY']);das=int(o['DAS'])
            if (o['YEAR'],o['DOY'],o['DAS'])!=(n['YEAR'],n['DOY'],n['DAS']):raise ValueError('N table dates differ')
            if any(float(n[k])!=0 for k in ('FLOODN','ALGFIX')) or float(o['ARESN'])!=0:
                raise ValueError('External fixation/flood/residue inputs are outside this audit domain')
            expected_fert=fertilizer.get(date,0.) if run==1 and das>0 else 0.
            if abs(float(n['AFERT'])-expected_fert)>precision(n['AFERT']):raise ValueError('Native fertilizer flux differs')
            if das>0:
                if any(float(n[k])<0 for k in LOSSES):raise ValueError('Unsupported negative external N loss')
                loss+=sum(float(n[k]) for k in LOSSES);loss_bound+=sum(precision(n[k]) for k in LOSSES)
                fert+=expected_fert
            if run==1 and date in states:
                a=states[date]
                plant=10*(a['canopy_n']+a['rootn']*a['population'])
                damage=10*a['cum_n'];seed=10*a['seed_n'];root_pending=a['root_sen_n']
                uptake_pending=uptake[date]
            elif run==1:
                plant=damage=seed=root_pending=uptake_pending=0.
            else:
                plant=root_pending=uptake_pending=0.;damage=10*final['cum_n'];seed=10*final['seed_n']
            if das>0:
                prior_date=shift_yrdoy(date,-1)
                prior_uptake=uptake.get(prior_date,0.) if run==1 else 0.
                timing_error=abs(float(n['RNUP'])-prior_uptake)
                timing_bound=precision(n['RNUP'])+uptake_bounds.get(prior_date,0.)
                if timing_error>timing_bound:raise ValueError(f'Soil uptake lag differs on {run}/{date}: {timing_error}')
                prior_root=states[prior_date]['root_sen_n'] if run==1 and prior_date in states else 0.
                root_error=abs(float(o['ASENN'])-prior_root)
                root_bound=precision(o['ASENN'])+8*2**-24*abs(prior_root)
                if root_error>root_bound:raise ValueError(f'Soil root delivery lag differs on {run}/{date}: {root_error}')
                max_root_timing=max(max_root_timing,root_error)
                max_timing=max(max_timing,timing_error);timing_checks+=1
            soil,soil_bound=stock(o,n)
            exported=harvest_export if run==2 else 0.
            raw=soil+plant+root_pending+damage+exported+loss-initial-fert-seed
            residual=raw-uptake_pending
            native_bound=32*2**-24*(abs(plant)+abs(root_pending)+abs(damage)+abs(seed)+abs(exported)+abs(uptake_pending))
            bound=initial_bound+soil_bound+loss_bound+native_bound
            rows.append({'run':run,'date':date,'das':das,'soil_n_kg_ha':soil,'standing_plant_n_kg_ha':plant,
                'pending_root_delivery_kg_ha':root_pending,'pending_soil_uptake_withdrawal_kg_ha':uptake_pending,
                'damage_export_n_kg_ha':damage,'harvest_export_n_kg_ha':exported,'seed_input_n_kg_ha':seed,
                'fertilizer_n_kg_ha':fert,'external_loss_n_kg_ha':loss,'unadjusted_scheduler_residual_kg_ha':raw,
                'residual_kg_ha':residual,'native_print_and_float_bound_kg_ha':bound,'passed':abs(residual)<=bound})
    start_fallow=rows[len(organic[1])]
    if start_fallow['date']!=harvest_date or start_fallow['das']!=0:
        raise ValueError('Unexpected printed harvest-to-fallow initial boundary')
    end_crop,end_bound=stock(organic[1][-1],inorganic[1][-1])
    init_fallow,init_bound=stock(organic[2][0],inorganic[2][0])
    boundary_residual=init_fallow-end_crop-h['residue_n']
    boundary_bound=end_bound+init_bound+64*2**-24*abs(h['residue_n'])
    if abs(boundary_residual)>boundary_bound:raise ValueError('Printed soil initial stock did not receive native HARVRES exactly once')
    return {'rows':rows,'observations':len(rows),'days_with_losses':timing_checks,
        'native_harvest_contract_passed':bool(diagnostics['v2_contract']['passed']),
        'combined_model_n_evidence_passed':all(r['passed'] for r in rows) and bool(diagnostics['v2_contract']['passed']),
        'daily_inventory_passed':all(r['passed'] for r in rows),'fallow_initial_inventory_passed':start_fallow['passed'],
        'final_inventory_passed':rows[-1]['passed'],'final_residual_kg_ha':rows[-1]['residual_kg_ha'],
        'final_roundoff_bound_kg_ha':rows[-1]['native_print_and_float_bound_kg_ha'],
        'max_abs_residual_kg_ha':max(abs(r['residual_kg_ha']) for r in rows),
        'max_soil_uptake_lag_match_error_kg_ha':max_timing,'source_flux_lag_checks':timing_checks,
        'max_root_delivery_lag_match_error_kg_ha':max_root_timing,
        'printed_harvest_soil_stock_jump_residual_kg_ha':boundary_residual,
        'printed_harvest_soil_stock_jump_bound_kg_ha':boundary_bound,
        'initial_offset_inferred':False,'residual_offsets_fitted':False,
        'byproduct_n_is_defined_allocation':True,'scope':'modeled daily N inventory with explicit scheduler transfers',
        'independent_agronomic_validation':False,'whole_elemental_carbon_verified':False,'research_ready':False}
