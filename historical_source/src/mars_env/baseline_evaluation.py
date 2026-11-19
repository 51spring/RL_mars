"""Diagnostic paired evaluation with independent raw-return/action accounting."""
import math
import numpy as np

from .policies import public_values


def evaluate_episode(env,policy,season,rules,grain_price,*,max_steps=240,
                     reset_options=None, record_decision_context=False, expected_split='validation'):
    if expected_split not in ('train', 'validation') or season.split != expected_split:
        raise ValueError('Expected the configured train or validation split; final test is reserved')
    options = {'season': season} if reset_options is None else reset_options
    obs, _ = env.reset(options=options)
    if record_decision_context and env.exogenous is not season:
        raise ValueError('Environment did not bind the expected season')
    tape=[]; total=water=nitrogen=sprays=cost_sum=0.
    for day in range(max_steps):
        state=env.state
        weather={k:float(state[k]) for k in ('rain','tmax','srad')}
        date=int(state['yrdoy'])
        mask=env.action_masks()
        indices=policy.action(obs,mask.copy(),rules)
        action=rules.decode(indices)
        if not all(mask[offset+int(i)] for offset,i in zip((0,6,15),indices)):
            raise ValueError('Policy selected a masked action')
        independent_cost=(action.water_mm*rules.water_price+action.nitrogen_kg_ha*rules.nitrogen_price
            +action.spray*rules.spray_price+(rules.irrigation_labor if action.water_mm else 0)
            +(rules.nitrogen_labor if action.nitrogen_kg_ha else 0))
        context = {}
        if record_decision_context:
            values = public_values(obs)
            context = {
                'istage': int(state['istage']), 'vstage': float(state['vstage']), 'ep': float(state['ep']),
                'mask': mask.tolist(),
                'public_survey': {name: values[name] for name in ('survey_value', 'survey_age')},
                'public_bulletin': {name: values[name] for name in
                                    ('announced', 'reduction_fraction', 'days_since_announcement')},
            }
        obs,reward,terminated,truncated,info=env.step(indices)
        if not math.isclose(info['cost'],independent_cost,abs_tol=1e-7):
            raise ValueError('Daily action-cost mismatch')
        total+=float(reward);cost_sum+=independent_cost
        water+=action.water_mm;nitrogen+=action.nitrogen_kg_ha;sprays+=action.spray
        tape.append({'decision_day':day,'yrdoy':date,'weather':weather,
            'action_indices':np.asarray(indices,dtype=int).tolist(),'raw_reward':float(reward),
            'cost':independent_cost,'terminated':terminated,'truncated':truncated,**context})
        if truncated:
            raise ValueError('Administrative truncation is not a completed baseline season')
        if terminated:
            result=info['episode_result']
            expected={'water_mm':water,'nitrogen_kg_ha':nitrogen,'sprays':sprays,'total_cost':cost_sum,
                'net_return':result['harvested_grain_kg_ha']*grain_price-cost_sum}
            for key,value in expected.items():
                if not math.isclose(result[key],value,abs_tol=1e-6):
                    raise ValueError('Independent episode accounting mismatch: '+key)
            if not math.isclose(total,result['net_return'],abs_tol=1e-6):
                raise ValueError('Raw reward does not sum to net return')
            if result['reason'] not in ('harvest','crop_failure'):
                raise ValueError('Unknown terminal reason')
            return {'season':season.manifest(),'episode_result':result,'raw_return':total,
                'steps':len(tape),'constraint_violations':0,'daily_tape':tape}
    raise ValueError('Baseline season did not terminate within diagnostic horizon')


def verify_pairs(records):
    groups={}
    for record in records:
        season=record['season']
        key=(season['split'],season['season_id'])
        group=groups.setdefault(key,{})
        if record['policy'] in group:raise ValueError('Duplicate policy/season result')
        group[record['policy']]=record
    checks=[]
    if not groups:raise ValueError('No paired seasons')
    for key,group in groups.items():
        if set(group)!= {'no_input','rule'}:raise ValueError('Missing policy in paired season')
        a,b=group.values()
        if a['season']!=b['season']:raise ValueError('Exogenous address or resource condition differs')
        def weather(record):
            days={r['yrdoy']:r['weather'] for r in record['daily_tape']}
            if len(days)!=len(record['daily_tape']):raise ValueError('Duplicate weather date')
            return days
        x,y=weather(a),weather(b);common=sorted(x.keys()&y.keys())
        if not common or any(x[d]!=y[d] for d in common):raise ValueError('Common-date weather mismatch')
        checks.append({'split':key[0],'season_id':key[1],'common_weather_dates':len(common),
            'manifest_equal':True,'weather_equal':True})
    return checks


def summarize(records):
    result={}
    for name in sorted({r['policy'] for r in records}):
        rows=[r['episode_result'] for r in records if r['policy']==name]
        result[name]={'seasons':len(rows),**{key:float(np.mean([r[key] for r in rows])) for key in
            ('net_return','harvested_grain_kg_ha','water_mm','nitrogen_kg_ha','sprays')},
            'failure_rate':sum(r['reason']=='crop_failure' for r in rows)/len(rows)}
    return result
