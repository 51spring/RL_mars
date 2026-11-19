"""Diagnostic-only WTH station temperature edits; daily records stay byte-identical."""
import math
import re


def station_temperature_fixture(text,tav,amp):
    """Set positive diagnostic TAV/AMP in existing station-width fields.

    Native IPWTH treats nonpositive values as missing. This helper rejects them
    rather than pretending they reach the soil model as supplied.
    """
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<=0 for v in (tav,amp)):
        raise ValueError('Diagnostic TAV/AMP must be finite and positive')
    lines=text.splitlines(keepends=True)
    headers=[i for i,l in enumerate(lines) if l.startswith('@ INSI')]
    if len(headers)!=1:raise ValueError('Exactly one station header required')
    i=headers[0];header=lines[i]
    spans=list(re.finditer(r'\S+',header));names=[s.group() for s in spans]
    if 'TAV' not in names or 'AMP' not in names:raise ValueError('TAV/AMP station fields required')
    row=lines[i+1]
    for name,value in [('AMP',amp),('TAV',tav)]:
        # PARSE_HEADERS starts the next field two Fortran columns after the
        # previous end, reserving one separator column (READS.for).
        j=names.index(name);end=spans[j].end();start=spans[j-1].end()+1
        token=f'{value:.2f}'
        if len(token)>end-start:raise ValueError('Value exceeds existing station field width')
        if row[start-1:start] != ' ':raise ValueError('Station separator must be blank')
        row=row[:start]+token.rjust(end-start)+row[end:]
    lines[i+1]=row
    return ''.join(lines)
