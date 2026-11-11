"""Diagnostic integration of explicit ICASA soil/initial layers; no gap filling."""
import math


def number(value):
    if isinstance(value,bool):raise ValueError('Boolean is not a physical value')
    value=float(value)
    if not math.isfinite(value):raise ValueError('Nonfinite physical value')
    return value


def intervals(rows,key):
    result=[];top=0.
    for row in rows:
        bottom=number(row[key])
        if bottom<=top:raise ValueError('Layer bases must strictly increase from zero')
        result.append((top,bottom,row));top=bottom
    if not result:raise ValueError('Empty profile')
    return result


def initial_inventory(soil_layers,initial_layers):
    """Assumed dictionary units: cm, g/cm3, ppm N, volumetric water.

    Integrate intersections so nonmatching layer boundaries do not move N.
    Results describe the package initial date, not a later field observation.
    """
    soils=intervals(soil_layers,'sllb');initial=intervals(initial_layers,'icbl')
    if soils[-1][1]<initial[-1][1]:raise ValueError('Bulk density profile does not cover initial layers')
    no3=nh4=water=0.;parts=[]
    for top,bottom,ic in initial:
        theta=number(ic['ich2o']);nitrate=number(ic['icno3']);ammonium=number(ic['icnh4'])
        if not 0<=theta<=1 or min(nitrate,ammonium)<0:raise ValueError('Invalid initial concentration')
        water+=(bottom-top)*theta*10
        for st,sb,soil in soils:
            depth=max(0.,min(bottom,sb)-max(top,st))
            if not depth:continue
            bulk=number(soil['slbdm'])
            if bulk<=0:raise ValueError('Missing/nonpositive bulk density')
            factor=bulk*depth*.1
            no3+=nitrate*factor;nh4+=ammonium*factor
            parts.append(dict(top_cm=max(top,st),bottom_cm=min(bottom,sb),bulk_g_cm3=bulk,
                no3_kg_n_ha=nitrate*factor,nh4_kg_n_ha=ammonium*factor))
    return dict(depth_cm=initial[-1][1],water_mm=water,no3_kg_n_ha=no3,nh4_kg_n_ha=nh4,
                mineral_n_kg_ha=no3+nh4,intersections=parts)


def soil_schema_flags(layers):
    flags=[]
    for layer in layers:
        base=number(layer['sllb'])
        if 'slfc1' in layer and not 0<=number(layer['slfc1'])<=1:
            flags.append(dict(issue='volumetric_field_capacity_outside_0_1',base_cm=base,field='slfc1',value=layer['slfc1']))
        total=sum(number(layer[k]) for k in ('slcly','slsnd','slsil'))
        if abs(total-100)>1e-6:
            flags.append(dict(issue='texture_percent_sum_not_100',base_cm=base,total=total,
                fraction_like=abs(total-1)<1e-6,automatic_rescaling_allowed=False))
    return flags
