"""Cumulative four-run modeled N, without resetting external ledgers by year."""
from pathlib import Path
from .integrated_n import run_tables,stock,LOSSES
from .soil_audit import precision
from .audits import shift_yrdoy,management_events
from .actual_harvest_contract import check_actual_contract
from .multiyear_audit import audit_boundaries


def cumulative_terms(run,date,states,finals,exports):
    prior=[r for r in finals if r<run]
    seed=10*sum(finals[r]['seed_n'] for r in prior)
    damage=10*sum(finals[r]['cum_n'] for r in prior)
    exported=sum(exports[r] for r in prior)
    plant=root_pending=uptake_pending=0.
    if (run,date) in states:
        a,uptake=states[(run,date)]
        plant=10*(a['canopy_n']+a['rootn']*a['population'])
        seed+=10*a['seed_n'];damage+=10*a['cum_n']
        root_pending=a['root_sen_n'];uptake_pending=uptake
    return dict(plant=plant,seed=seed,damage=damage,harvest=exported,
                root_pending=root_pending,uptake_pending=uptake_pending)


def analyze_multiyear_n(folder,diagnostics,trace,actions,*,mode='Q',expected_annual_fertilizer=116,
                        failed_before_emergence=()):
    if mode not in ('Q','F'):raise ValueError('Unsupported multiyear mode')
    failed_before_emergence = frozenset(failed_before_emergence)
    if not failed_before_emergence <= {1,3}:
        raise ValueError('Failure exception requires a crop run')
    folder=Path(folder);expected=(1,2,3,4)
    organic=run_tables((folder/'SoilNoBal.OUT').read_text(),expected_runs=expected)
    inorganic=run_tables((folder/'SoilNiBal.OUT').read_text(),expected_runs=expected)
    if len(trace)!=len(actions)+1:raise ValueError('Actions and native states differ in length')
    states={};uptake_bounds={};fertilizer={};contracts={};finals={};exports={}
    for before,after,action in zip(trace,trace[1:],actions):
        run=int(action['run']);date=int(action['date'])
        if run!=int(before['mars_sequence_soils'][-1]['run']) or date!=int(before['yrdoy']):
            raise ValueError('Action address and native state differ')
        if run not in (1,3):
            if any(action[k]!=0 for k in ('water_mm','nitrogen_kg_ha','damage')):
                raise ValueError('Unexpected fallow management')
            continue
        a,b=before['mars_plant_audit'],after['mars_plant_audit']
        key=(run,date)
        if key in states:raise ValueError('Duplicate crop/run/day')
        states[key]=(b,10*(b['wtnup']-a['wtnup']))
        uptake_bounds[key]=8*2**-24*10*(abs(a['wtnup'])+abs(b['wtnup']))
        if action['nitrogen_kg_ha']:fertilizer[key]=action['nitrogen_kg_ha']
    for run in (1,3):
        h=next(h for h in diagnostics['harvests'] if h['run']==run)
        date=int(h['date']);ear=next(e for e in diagnostics['ear_records'] if e['dynamic']==6 and e['date']==date)
        if run in failed_before_emergence:
            metadata={'run','date','rnmode','grain_fraction','stover_fraction'}
            zero_stocks=('canopy_n','rootn','root_sen_n','wtnup','seed_n','cum_n')
            if (any(value != 0 for key,value in h.items() if key not in metadata)
                or any(ear[key] != 0 for key in ('population','ears','yield','gnup','stovwt'))
                or any(state[key] != 0 for (crop,_),(state,_) in states.items()
                       if crop == run for key in zero_stocks)):
                raise ValueError('Expected failed crop with no established plant N or harvest residue')
            contract={'passed':True,'failed_before_emergence':True,'byproduct_n_kg_ha':0.}
        else:
            contract=check_actual_contract(h,ear)
        contracts[run]=contract
        if not contract['passed']:raise ValueError('Native v2 harvest boundary failed')
        expected_dates={int(r['YEAR'])*1000+int(r['DOY']) for r in organic[run] if int(r['DAS'])>0}
        if {d for r,d in states if r==run}!=expected_dates:raise ValueError('Crop soil/trace date coverage differs')
        finals[run],pending=states[(run,date)]
        if abs(finals[run]['root_sen_n'])>1e-10 or abs(pending)>1e-10:
            raise ValueError('Nonzero terminal pending transfer outside scope')
        exports[run]=h['harvest_grain_n']+contract['byproduct_n_kg_ha']
    events=[(d,amount) for d,kind,amount in management_events((folder/'MgmtEvent.OUT').read_text()) if kind=='Fertilizer']
    if sorted(events)!=sorted((date,amount) for (_,date),amount in fertilizer.items()):
        raise ValueError('Action/native fertilizer event mismatch')
    expected_fertilizer = (expected_annual_fertilizer if isinstance(expected_annual_fertilizer,tuple)
                           else (expected_annual_fertilizer,)*2)
    annual_fertilizer = tuple(sum(v for (r,_),v in fertilizer.items() if r==run) for run in (1,3))
    if annual_fertilizer != expected_fertilizer:
        raise ValueError(f'Expected {expected_annual_fertilizer} kg N for each diagnostic crop')
    initial,initial_bound=stock(organic[1][0],inorganic[1][0])
    loss=loss_bound=fert=0.;rows=[];max_uptake=max_root=0.;boundaries=[]
    for run in expected:
        if len(organic[run])!=len(inorganic[run]):raise ValueError('N table lengths differ')
        if run>1:
            previous_o,previous_n=organic[run-1][-1],inorganic[run-1][-1]
            o,n=organic[run][0],inorganic[run][0]
            if (o['YEAR'],o['DOY'])!=(previous_o['YEAR'],previous_o['DOY']):
                raise ValueError('Initialization date is not previous run close')
            before,bb=stock(previous_o,previous_n);after,ab=stock(o,n)
            incoming=next(h['residue_n'] for h in diagnostics['harvests'] if h['run']==run-1) if run in (2,4) else 0.
            residual=after-before-incoming;bound=bb+ab+64*2**-24*abs(incoming)
            if abs(residual)>bound:raise ValueError('Cross-run soil N inventory jump differs')
            boundaries.append(dict(run=run,residual_kg_ha=residual,bound_kg_ha=bound,passed=True))
        for o,n in zip(organic[run],inorganic[run]):
            if (o['YEAR'],o['DOY'],o['DAS'])!=(n['YEAR'],n['DOY'],n['DAS']):raise ValueError('N dates differ')
            date=int(o['YEAR'])*1000+int(o['DOY']);das=int(o['DAS'])
            if any(float(n[k])!=0 for k in ('FLOODN','ALGFIX')) or float(o['ARESN'])!=0:
                raise ValueError('Flood/fixation/external residue outside scope')
            expected_fert=fertilizer.get((run,date),0.) if das>0 else 0.
            if abs(float(n['AFERT'])-expected_fert)>precision(n['AFERT']):raise ValueError('Native daily fertilizer differs')
            if das>0:
                if any(float(n[k])<0 for k in LOSSES):raise ValueError('Negative external N loss unsupported')
                loss+=sum(float(n[k]) for k in LOSSES);loss_bound+=sum(precision(n[k]) for k in LOSSES)
                fert+=expected_fert
                previous=(run,shift_yrdoy(date,-1));previous_state,previous_uptake=states.get(previous,({},0.))
                u_error=abs(float(n['RNUP'])-previous_uptake)
                if u_error>precision(n['RNUP'])+uptake_bounds.get(previous,0.):raise ValueError('Soil uptake lag differs')
                root=previous_state.get('root_sen_n',0.);r_error=abs(float(o['ASENN'])-root)
                if r_error>precision(o['ASENN'])+8*2**-24*abs(root):raise ValueError('Root delivery lag differs')
                max_uptake=max(max_uptake,u_error);max_root=max(max_root,r_error)
            terms=cumulative_terms(run,date,states,finals,exports)
            soil,sb=stock(o,n)
            residual=(soil+terms['plant']+terms['root_pending']-terms['uptake_pending']
                +terms['damage']+terms['harvest']+loss-initial-fert-terms['seed'])
            bound=initial_bound+sb+loss_bound+32*2**-24*sum(abs(v) for v in terms.values())
            rows.append({'run':run,'date':date,'das':das,'soil_n_kg_ha':soil,**terms,
                'fertilizer_kg_ha':fert,'external_loss_kg_ha':loss,'residual_kg_ha':residual,
                'print_and_binary32_bound_kg_ha':bound,'passed':abs(residual)<=bound})
    if rows[-1]['date']!=1984029 or sum(r['das']>0 for r in rows)!=730:
        raise ValueError('Full two-year N output coverage required')
    handoff=audit_boundaries(diagnostics,expected_mode=mode)
    passed=all(r['passed'] for r in rows) and handoff['passed']
    return {'passed':passed,'rows':rows,'observations':len(rows),'daily_observations':730,
        'cross_run_boundaries':boundaries,'native_handoff':handoff,'crop_harvest_contracts':contracts,
        'final_residual_kg_ha':rows[-1]['residual_kg_ha'],'final_bound_kg_ha':rows[-1]['print_and_binary32_bound_kg_ha'],
        'max_abs_residual_kg_ha':max(abs(r['residual_kg_ha']) for r in rows),
        'max_uptake_lag_error_kg_ha':max_uptake,'max_root_delivery_error_kg_ha':max_root,
        'cumulative_seed_n_kg_ha':rows[-1]['seed'],'cumulative_damage_n_kg_ha':rows[-1]['damage'],
        'cumulative_harvest_n_kg_ha':rows[-1]['harvest'],'fertilizer_total_kg_ha':fert,
        'initial_offset_inferred':False,'residual_offsets_fitted':False,
        'scope':f'two-year four-run modeled N for specified {mode}-mode candidate allocation',
        'whole_elemental_carbon_verified':False,'independent_agronomic_validation':False,'research_ready':False}
