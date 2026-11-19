"""Explicit, narrow compatibility adapter; never changes weather observations."""
import re
from datetime import datetime


def require_supported_native_dates(initial_date,start_date):
    """This diagnostic supports a date-matched initial/start state only."""
    initial=datetime.strptime(initial_date,'%Y%m%d')
    start=datetime.strptime(start_date,'%Y%m%d')
    if initial!=start:raise ValueError('Native diagnostic requires matching initial/start dates')


def align_y4k_weather_header(text):
    lines=text.splitlines(keepends=True)
    headers=[i for i,line in enumerate(lines) if line.startswith('@DATE')]
    if len(headers)!=1:raise ValueError('Expected one unadapted writer @DATE header')
    i=headers[0]
    if not lines[i].startswith('@DATE    SRAD'):raise ValueError('Unknown weather header layout')
    count=0
    for line in lines[i+1:]:
        if not line.strip():continue
        if not re.match(r'^\d{7}\s',line):raise ValueError('Expected seven-digit weather dates')
        count+=1
    if count==0:raise ValueError('No weather records')
    # Keep SRAD and every later header at the same end column, but extend
    # the first field from5 to7 columns, matching the seven-digit data dates.
    lines[i]='@  DATE'+lines[i][7:]
    return ''.join(lines)
