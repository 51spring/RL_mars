"""Privileged diagnostics; none of these fields enter policy observations."""
from datetime import date, timedelta
import math
import re


def shift_yrdoy(value, days):
    year, doy = divmod(int(value), 1000)
    actual = date(year, 1, 1) + timedelta(days=doy - 1)
    if doy < 1 or actual.year != year:
        raise ValueError('Invalid YYYYDDD date')
    actual += timedelta(days=days)
    return actual.year * 1000 + actual.timetuple().tm_yday


def enable_audit_outputs(template):
    lines = template.splitlines()
    for i, line in enumerate(lines):
        if line.startswith('@N OUTPUTS'):
            keys = line.split()[2:]
            row = lines[i + 1]
            spans = list(re.finditer(r'\S+', row))
            values = [m.group() for m in spans]
            for key in ('GROUT', 'CAOUT', 'WAOUT', 'NIOUT', 'MIOUT', 'CHOUT', 'OPOUT'):
                if key not in keys:
                    raise ValueError(f'Missing output control {key}')
                values[2 + keys.index(key)] = 'Y'
            values[2 + keys.index('VBOSE')] = 'D'
            for match, value in reversed(list(zip(spans, values))):
                row = row[:match.start()] + value.rjust(match.end()-match.start()) + row[match.end():]
            lines[i+1] = row
            return '\n'.join(lines) + '\n'
    raise ValueError('Missing output controls')


def weather_rows(text):
    rows, header = {}, None
    for line in text.splitlines():
        if line.startswith('@YEAR'):
            header = line[1:].split()
        elif header and re.match(r'^\s*\d{4}\s+\d{3}\s', line):
            values = line.split()
            if len(values) != len(header):
                raise ValueError('Unexpected weather column count')
            row = dict(zip(header, map(float, values)))
            yrdoy = int(row['YEAR']) * 1000 + int(row['DOY'])
            if yrdoy in rows:
                raise ValueError('Duplicate weather date')
            rows[yrdoy] = row
    if not rows:
        raise ValueError('No Weather.OUT rows')
    return rows


def verify_completed_weather(state, completed_date, rows):
    """Weather.OUT F6.1 fields imply ±0.05 plus native float32 rounding."""
    output = rows[int(completed_date)]
    residuals = {}
    for state_key, output_key in [('rain','PRED'),('srad','SRAD'),('tmax','TMXD'),('tmin','TMND')]:
        value = float(state[state_key])
        difference = value - output[output_key]
        if not math.isfinite(value) or abs(difference) > 0.05001:
            raise AssertionError(f'{state_key} does not match completed date {completed_date}: {difference}')
        residuals[state_key] = difference
    return residuals


def management_events(text):
    months = {name:i+1 for i,name in enumerate(('JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'))}
    events = []
    for line in text.splitlines():
        match = re.match(r'^\s*\d+\s+([A-Z]{3})\s+(\d+),\s+(\d{4}).*?\b(Irrigation|Fertilizer)\s+([\d.]+)',line)
        if match:
            month,day,year,operation,amount=match.groups()
            stamp=date(int(year),months[month],int(day))
            events.append((stamp.year*1000+stamp.timetuple().tm_yday,operation,float(amount)))
    return events
