"""Source marginal targets, kept separate from executable factorial scenarios."""
import json
import math
from pathlib import Path


def dry_grain_mass(value, *, unit, moisture_fraction, basis_verified):
    """Wet-basis moisture conversion; does not change biological/area units."""
    if basis_verified is not True:
        raise ValueError('Grain moisture basis is not verified')
    if unit not in ('kg/ha', 't/ha'):
        raise ValueError('Pot mass cannot be converted to field yield')
    for x in (value, moisture_fraction):
        if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x):
            raise ValueError('Finite numeric mass and moisture required')
    if value < 0 or not 0 <= moisture_fraction < 1:
        raise ValueError('Invalid mass or wet-basis moisture')
    return value * (1000 if unit == 't/ha' else 1) * (1-moisture_fraction)


def require_factorial_observation(target):
    if target.get('aggregation') != 'factorial_cell':
        raise ValueError('Marginal means cannot be reused as cultivar/year factorial observations')


def build_marginal_targets(root):
    root=Path(root)
    source=json.loads((root/'configs/rahman2022_marginal_grain.json').read_text(encoding='utf-8'))
    catalog=json.loads((root/'configs/agronomic_sources.json').read_text(encoding='utf-8'))
    role=next(s['planned_role'] for s in catalog['studies'] if s['id']==source['study_id'])
    targets=[]; contrasts=[]
    convert=lambda v:dry_grain_mass(v, unit=source['unit'],
        moisture_fraction=source['moisture_fraction_wet_basis'],
        basis_verified=source['moisture_basis_verified'])
    for region in source['regions']:
        for treatment, mean in region['means'].items():
            targets.append({'target_id':source['study_id']+'_'+region['region'].replace(' ','_')+'_'+treatment,
                'study_id':source['study_id'],'study_role':role,'region':region['region'],
                'treatment':treatment,'aggregation':source['aggregation'],
                'cultivars_averaged':source['cultivars'],'years_averaged':source['years'],
                'reported_mean_kg_ha':mean,'reported_marginal_sem_kg_ha':region['reported_marginal_sem'],
                'derived_dry_grain_kg_ha':convert(mean),
                'derived_dry_marginal_sem_kg_ha':convert(region['reported_marginal_sem']),
                'sem_scope':'reported shared marginal SEM; not factorial cell or contrast SE',
                'damage_definition':source['damage_definitions'][treatment],
                'blockers':source['pending_inputs'], 'ready_for_quantitative_validation':False,
                'calibration_allowed':False,'research_ready':False})
            if treatment!='control':
                contrasts.append({'study_id':source['study_id'],'region':region['region'],'treatment':treatment,
                    'aggregation':source['aggregation'],'ratio':mean/region['means']['control'],
                    'contrast_standard_error':None,'confidence_interval':None,
                    'covariance_assumed_zero':False,'model_validation_passed':None})
    return targets,contrasts
