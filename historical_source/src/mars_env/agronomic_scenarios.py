"""Explicit public-study scenarios and refusal of unsupported comparisons."""
import json
import math
from pathlib import Path


def build_registry(root):
    root=Path(root)
    protocols=json.loads((root/'configs/agronomic_protocols.json').read_text(encoding='utf-8'))['studies']
    roles={s['id']:s['planned_role'] for s in json.loads((root/'configs/agronomic_sources.json').read_text(encoding='utf-8'))['studies']}
    if any(p['role']!=roles[k] for k,p in protocols.items()):raise ValueError('Study split role drift')
    rows=[]
    def add(study,name,factors,group,control,damage_kind,mean):
        protocol=protocols[study]
        readiness=dict(protocol['readiness'],numeric_cell_mean=mean is not None,damage_mapping=damage_kind=='none')
        rows.append({'scenario_id':study+'_'+name,'study_id':study,'study_role':protocol['role'],
            'factors':factors,'comparison_group':study+'_'+group,'is_control':control,'damage_kind':damage_kind,
            'endpoint':protocol['endpoint'],'unit':protocol['unit'],'observed_mean':mean,
            'observed_standard_error':None,'replicates':protocol['replicates'],'readiness':readiness,
            'registered_acceptance_rule':None,
            'source':protocol['source'],'execution_scope':'simulator_validation_not_policy_training'})
    s=json.loads((root/'configs/santos2018_table1_productivity.json').read_text(encoding='utf-8'))
    for row in s['rows']:
        for water,mean in zip(s['irrigation_percent_etc'],row['means']):
            damage=row['defoliation_percent']
            add('santos2018',f'etc{water}_d{damage}',{'irrigation_percent_etc':water,'defoliation_percent':damage,'stage':'V4'},
                f'etc{water}',damage==0,protocols['santos2018']['damage_kinds'][str(damage)],mean)
    o=json.loads((root/'configs/oveysi2010_table4_grain.json').read_text(encoding='utf-8'))
    for row in o['rows']:
        damage=o['defoliation'][row['defoliation']]
        add('oveysi2010',row['water']+'_'+row['defoliation'],dict(row,stage=damage['stage'],blade_fraction=damage['fraction']),
            row['water'],row['defoliation']=='D1','none' if row['defoliation']=='D1' else 'blade_clipping',row['grain_t_ha'])
    for stage in protocols['oliveira2026']['nitrogen']['topdress_options']:
        for damaged in (False,True):
            topdress=80 if stage else 0
            add('oliveira2026',f'n{stage or "none"}_d{int(damaged)}',
                {'basal_n_kg_ha_equivalent':40,'topdress_n_kg_ha_equivalent':topdress,
                 'total_n_kg_ha_equivalent':40+topdress,'nitrogen_stage':stage,'damage_stage':'V4' if damaged else None},
                f'n{stage or "none"}',not damaged,'shoot_cut_5cm' if damaged else 'none',None)
    if len({r['scenario_id'] for r in rows})!=len(rows):raise ValueError('Duplicate public scenario')
    return rows


def readiness(scenario):
    blockers=[k for k,v in scenario['readiness'].items() if v is not True]
    se=scenario['observed_standard_error'];rule=scenario.get('registered_acceptance_rule')
    numeric_se=isinstance(se,(int,float)) and not isinstance(se,bool) and math.isfinite(se) and se>=0
    registered_bounds=(isinstance(rule,dict) and rule.get('registered_before_comparison') is True
        and rule.get('endpoint')==scenario['endpoint'] and rule.get('unit')==scenario['unit']
        and isinstance(rule.get('reference'),str) and bool(rule['reference'].strip())
        and isinstance(rule.get('absolute_tolerance'),(int,float)) and not isinstance(rule.get('absolute_tolerance'),bool)
        and math.isfinite(rule['absolute_tolerance']) and rule['absolute_tolerance']>0)
    if not numeric_se and not registered_bounds:
        blockers.append('numeric_uncertainty_or_registered_bounds')
    return {'ready_for_quantitative_validation':not blockers,'blockers':blockers,
        'calibration_allowed':not blockers and scenario['study_role'].startswith('calibration'),
        'study_role':scenario['study_role'],'research_ready':False}


def require_calibration_role(scenario):
    if not scenario['study_role'].startswith('calibration'):
        raise ValueError('Independent study cannot be used for calibration or threshold selection')
    if not readiness(scenario)['calibration_allowed']:
        raise ValueError('Calibration study inputs/endpoint/uncertainty are not ready')


def source_contrasts(scenarios):
    groups={}
    for s in scenarios:groups.setdefault(s['comparison_group'],[]).append(s)
    result=[]
    for group,rows in groups.items():
        controls=[r for r in rows if r['is_control']]
        if len(controls)!=1:raise ValueError('Expected one matched control per study condition')
        control=controls[0]
        for row in rows:
            if row['is_control'] or row['observed_mean'] is None:continue
            if not control['observed_mean'] or control['observed_mean']<0:raise ValueError('Undefined control response ratio')
            result.append({'scenario_id':row['scenario_id'],'control_scenario_id':control['scenario_id'],
                'study_id':row['study_id'],'endpoint':row['endpoint'],
                'ratio':row['observed_mean']/control['observed_mean'],
                'confidence_interval':None,'standard_error_inferred':False,
                'use':'descriptive source contrast only','model_validation_passed':None})
    return result


def descriptive_prediction_comparison(scenario,prediction):
    if prediction['endpoint']!=scenario['endpoint']:raise ValueError('Biological harvest endpoints differ')
    scales={'t/ha':1000.,'kg/ha':1.}
    if prediction['unit'] not in scales or scenario['unit'] not in scales:
        raise ValueError('Pot or unspecified experimental units cannot be converted to field mass/area')
    if scenario['observed_mean'] is None:raise ValueError('No numeric observation')
    value=float(prediction['value'])*scales[prediction['unit']]
    observed=float(scenario['observed_mean'])*scales[scenario['unit']]
    if not math.isfinite(value) or value<0:raise ValueError('Invalid predicted yield')
    return {'prediction_kg_ha':value,'observed_kg_ha':observed,'difference_kg_ha':value-observed,
        'comparison_mode':'descriptive_only','statistical_validation_passed':None,
        'scenario_readiness':readiness(scenario),'research_ready':False}
