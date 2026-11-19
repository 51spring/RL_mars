"""Soil carbon output arithmetic, explicitly separate from crop elemental C."""
import math
import re
from .audits import shift_yrdoy
from .soil_audit import precision

INITIAL=('SOMC0Ti','SOMCTi','LC0Di','LCTDi','CH4STDi')
FINAL=('SOMC0T','SOMCT','LC0D','LCTD','CH4STD')
LOSSES=('CO2ED','CH4ED','CH4LCD','CH4COD')
ADDITIONS=('RESC0D','RESC1D','THRC0D','THRC1D')
SENESCENCE=('SNCLD','SNCSD')


def carbon_runs(text):
    runs={};run=None;header=None
    for line in text.splitlines():
        match=re.match(r'^\*RUN\s+(\d+)',line)
        if match:
            run=int(match[1]);header=None
            if run in runs:raise ValueError('Repeated carbon run identity')
            runs[run]=[]
        elif line.startswith('@YEAR'):
            header=line[1:].split()
            if run is None or not set((*INITIAL,*FINAL,*LOSSES,*ADDITIONS,*SENESCENCE,'DAYBAL','CUMBAL','YEAR','DOY','DAS'))<=set(header):
                raise ValueError('Missing carbon columns/run identity')
        elif header and re.match(r'^\s*\d{4}\s+\d{3}\s',line):
            values=line.split()
            if len(values)!=len(header):raise ValueError('Malformed carbon table')
            row=dict(zip(header,values))
            if not all(math.isfinite(float(v)) for v in values):raise ValueError('Nonfinite carbon output')
            if runs[run]:
                prev=runs[run][-1]
                date=lambda r:int(r['YEAR'])*1000+int(r['DOY'])
                if date(row)!=shift_yrdoy(date(prev),1) or int(row['DAS'])!=int(prev['DAS'])+1:
                    raise ValueError('Carbon dates/DAS are not consecutive within run')
            runs[run].append(row)
    if not runs or not all(runs.values()):raise ValueError('Empty carbon run')
    return runs


def audit_soil_carbon(runs):
    summaries=[]
    for run,rows in runs.items():
        previous_sen={k:'0.00' for k in SENESCENCE};previous_cum='0.0000'
        maximum=0.;max_bound=0.;max_cum_error=0.
        for row in rows:
            terms=[(1,row[k]) for k in (*FINAL,*LOSSES)]
            terms.extend((-1,row[k]) for k in (*INITIAL,*ADDITIONS))
            terms.extend((-1,previous_sen[k]) for k in SENESCENCE)
            residual=math.fsum(sign*float(token) for sign,token in terms)
            bound=sum(precision(token) for _,token in terms)+precision(row['DAYBAL'])
            error=abs(residual-float(row['DAYBAL']))
            if error>bound+1e-8:raise ValueError('Soil carbon formula differs from printed DAYBAL')
            cum_error=abs(float(row['CUMBAL'])-float(previous_cum)-float(row['DAYBAL']))
            cum_bound=sum(precision(t) for t in (row['CUMBAL'],previous_cum,row['DAYBAL']))
            if cum_error>cum_bound+1e-8:raise ValueError('Carbon cumulative balance does not reset/accumulate correctly')
            maximum=max(maximum,error);max_bound=max(max_bound,bound);max_cum_error=max(max_cum_error,cum_error)
            previous_sen=row;previous_cum=row['CUMBAL']
        summaries.append({'run':run,'days':len(rows),'max_daybal_reconstruction_error_kg_c_ha':maximum,
            'max_print_reconstruction_bound_kg_c_ha':max_bound,'max_cumulative_reconstruction_error_kg_c_ha':max_cum_error,
            'last_printed_cumulative_residual_kg_c_ha':float(rows[-1]['CUMBAL']),
            'arithmetic_reconstruction_passed':True})
    return {'runs':summaries,'days':sum(len(v) for v in runs.values()),'soil_output_arithmetic_passed':True,
        'unit':'kg C/ha','whole_elemental_carbon_verified':False,'research_ready':False}


def carbon_coverage(runs,expected_final_date):
    shift_yrdoy(expected_final_date,0)
    date=lambda r:int(r['YEAR'])*1000+int(r['DOY'])
    last=None
    for _,rows in sorted(runs.items()):
        if last is not None and date(rows[0])!=shift_yrdoy(last,1):
            raise ValueError('Soil carbon output gap between native runs')
        last=date(rows[-1])
    if last is None or last>expected_final_date:raise ValueError('Invalid terminal carbon date')
    current=last;missing=0
    while current<expected_final_date:
        current=shift_yrdoy(current,1);missing+=1
    return {'complete':missing==0,'last_printed_date':last,'native_terminal_date':int(expected_final_date),
        'missing_terminal_days':missing,'arithmetic_pass_is_not_coverage_pass':True}


def verify_soil_residue_carbon(runs,diagnostics):
    if set(runs)!={1,2}:raise ValueError('Expected maize/fallow soil carbon outputs')
    incoming=[s for s in diagnostics['soils'] if s['run']==2 and s['phase']==1]
    if len(incoming)!=1:raise ValueError('Missing unique high-precision incoming residue')
    row=runs[2][0];checks={}
    for key,stock in (('THRC0D','surface_dm'),('THRC1D','root_dm')):
        expected=.4*incoming[0][stock]
        bound=precision(row[key])+64*2**-24/(1-64*2**-24)*max(2*abs(expected),1e-30)
        residual=float(row[key])-expected
        if abs(residual)>bound:raise ValueError('Soil harvest residue C/DM interface differs')
        checks[key]={'expected_kg_c_ha':expected,'residual_kg_c_ha':residual,'print_and_binary32_bound':bound}
    if any(float(r[k])!=0 for r in runs[2][1:] for k in ('THRC0D','THRC1D')):
        raise ValueError('Harvest residue C repeated after first fallow output')
    return {'passed':True,'checks':checks,'native_assumed_carbon_fraction':.4,
        'scope':'soil incoming residue bookkeeping only; not measured crop/export C'}
