"""Explicit diagnostic soil substitution; never inferred field observations."""
import math
import re
from .sequence_audit import replace_controls


def soil_profile(text,identifier):
    matches=list(re.finditer(r'^\*'+re.escape(identifier)+r'\s.*$',text,re.M))
    if len(matches)!=1:raise ValueError('Expected one exact soil profile')
    start=matches[0].start();end=text.find('\n*',matches[0].end())
    block=text[start:end if end>=0 else len(text)]
    lines=block.splitlines();header=None;layers=[]
    for line in lines[1:]:
        if line.startswith('@'):
            keys=line[1:].split()
            header=keys if all(k in keys for k in ('SLB','SLLL','SDUL','SSAT')) else None
        elif header and line.strip() and not line.startswith('!'):
            values=line.split()
            if len(values)!=len(header):raise ValueError('Malformed soil layer')
            row={k:float(v) for k,v in zip(header,values) if k in ('SLB','SLLL','SDUL','SSAT')}
            if not all(math.isfinite(v) for v in row.values()):raise ValueError('Nonfinite soil layer')
            if not 0<=row['SLLL']<row['SDUL']<row['SSAT']<=1:raise ValueError('Invalid soil water bounds')
            if row['SLB']<= (layers[-1]['SLB'] if layers else 0):raise ValueError('Soil depths must increase')
            layers.append(row)
    if not layers:raise ValueError('No soil layers')
    return {'identifier':identifier,'description':lines[0],'layers':layers,'source_block':block}


def diagnostic_soil_input(template,profile,*,water_fraction=.5):
    if isinstance(water_fraction,bool) or not math.isfinite(water_fraction) or not 0<=water_fraction<=1:
        raise ValueError('Diagnostic initial water fraction outside LL..DUL')
    lines=template.splitlines();layers=profile['layers']
    replace_controls(lines,'@L ID_FIELD',{'SLDP':int(layers[-1]['SLB'])})
    field_header=next(i for i,l in enumerate(lines) if l.startswith('@L ID_FIELD'))
    soil_index=lines[field_header].split().index('ID_SOIL')
    spans=list(re.finditer(r'\S+',lines[field_header+1]));old=spans[soil_index]
    # The native 10-character soil ID is wider than the ID_SOIL header label.
    if old.group()!='IBMZ910014' or len(profile['identifier'])!=len(old.group()):
        raise ValueError('Expected original UFGA soil ID and equal-width replacement')
    row=lines[field_header+1]
    lines[field_header+1]=row[:old.start()]+profile['identifier']+row[old.end():]
    header=next((i for i,l in enumerate(lines) if l.startswith('@C  ICBL')),None)
    if header is None:raise ValueError('Missing initial layer water/N header')
    end=header+1
    while end<len(lines) and lines[end].strip() and not lines[end].startswith(('*','@','!')):end+=1
    # New layer-specific diagnostic inputs: N concentrations fixed at .5/.1 ppm.
    rows=[]
    for layer in layers:
        water=layer['SLLL']+water_fraction*(layer['SDUL']-layer['SLLL'])
        rows.append(f" 1 {int(layer['SLB']):5d} {water:5.3f} {0.5:5.1f} {0.1:5.1f}")
    lines[header+1:end]=rows
    return '\n'.join(lines)+'\n'


def verify_effective_layers(profile,rows):
    """Permit native subdivision, but no crossing or missing source boundary."""
    top=0
    for row in rows:
        if row['top']!=top or row['bottom']<=top:raise ValueError('Native layer gap or overlap')
        candidates=[(0 if i==0 else profile['layers'][i-1]['SLB'],p)
                    for i,p in enumerate(profile['layers']) if p['SLB']>=row['bottom']]
        if not candidates:raise ValueError('Native layer exceeds soil depth')
        source_top,expected=candidates[0]
        if top<source_top:raise ValueError('Native layer crosses a source boundary')
        for key in ('SLLL','SDUL','SSAT'):
            if not math.isfinite(row[key]) or abs(row[key]-expected[key])>.00051:
                raise ValueError('Native water limit differs from selected soil')
        # Compare to the mathematical midpoint before decimal rounding. A tie
        # can round in either direction after binary representation.
        entered=(expected['SLLL']+expected['SDUL'])/2
        if not math.isfinite(row['SH2O']) or abs(row['SH2O']-entered)>.00051:
            raise ValueError('Native initial water differs from diagnostic input')
        top=row['bottom']
    if top!=profile['layers'][-1]['SLB']:raise ValueError('Native soil depth incomplete')
    return True
