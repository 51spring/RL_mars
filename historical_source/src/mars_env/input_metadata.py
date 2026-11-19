"""Explicit FileX metadata edits; never infer coordinates or soil properties."""
import re
import math


def field_metadata(template, *, longitude=None, latitude=None, elevation=None):
    lines=template.splitlines()
    for i,line in enumerate(lines):
        if line.startswith('@L ') and 'XCRD' in line and 'YCRD' in line and 'ELEV' in line:
            row=lines[i+1]
            if not row.startswith(' 1 '):raise ValueError('Expected UFGA field factor 1')
            for start,end,value,width in reversed([(3,18,longitude,15),(19,34,latitude,15),(35,44,elevation,9)]):
                if value is not None:
                    if isinstance(value,(int,float)) and not math.isfinite(value):raise ValueError('Metadata must be finite')
                    token=f'{value:.4f}' if isinstance(value,(int,float)) else str(value)
                    if len(token)>width:raise ValueError('Metadata exceeds fixed-width field')
                    row=row[:start]+token.rjust(width)+row[end:]
            lines[i+1]=row
            return '\n'.join(lines)+'\n'
    raise ValueError('Missing FileX field coordinates header')


def canonical_ufga_metadata(template):
    # Specific source-template correction, not a general automatic X/Y swap.
    if 'UFGA8201' not in template or 'UFGA0002' not in template:
        raise ValueError('Canonical metadata transform only supports UFGA8201/UFGA0002')
    return field_metadata(template,longitude=-82.3689,latitude=29.6380,elevation=40)


def summary_metadata(text):
    """Summary.OUT metadata has mixed character and numeric columns."""
    header=None
    for line in text.splitlines():
        if line.startswith('@') and 'HWAH' in line:
            header=list(re.finditer(r'\S+',line))
        elif header and re.match(r'^\s*\d+\s',line):
            row={}
            for i,field in enumerate(header):
                if field.group() in ('XLAT','LONG','ELEV'):
                    token=line[header[i-1].end():field.end()].strip()
                    row[field.group()]=float(token) if token else None
            if set(row)!= {'XLAT','LONG','ELEV'}:raise ValueError('Unsupported seasonal summary layout')
            return row
    raise ValueError('Missing seasonal summary metadata')
