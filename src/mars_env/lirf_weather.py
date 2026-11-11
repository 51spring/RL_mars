"""Unit/time guards for research-source audit; never substitutes policy weather."""
from datetime import datetime,timedelta
import math


def finite_observation(value):
    if isinstance(value,bool) or not isinstance(value,(int,float)):
        raise ValueError('Expected numeric observation')
    if not math.isfinite(value) or value == -999:
        raise ValueError('Missing/nonfinite observation')
    return float(value)


def aggregate_hourly_solar(day,records):
    """24 hour-end means in kJ/m2/min -> daily MJ/m2; no interpolation.

    Preserve signed sensor readings for the audit, never silently clip them.
    This arithmetic is not a physical-quality acceptance test.
    """
    start=datetime.combine(day,datetime.min.time())
    records=sorted(records,key=lambda row:row[0])
    expected=[start+timedelta(hours=i) for i in range(1,25)]
    if [row[0] for row in records] != expected:
        raise ValueError('Require exactly 24 unique consecutive hour-end records')
    values=[finite_observation(row[1]) for row in records]
    return math.fsum(values)*60/1000


def api_daily_value(payload,day,field,*,station):
    """Return QC field in Celsius or daily MJ/m2, keeping -999 as missing."""
    expected=dict(which='qc',frequency='daily',units='m',timezone='mst',station=station)
    if any(payload.get(k)!=v for k,v in expected.items()):
        raise ValueError('Wrong station, units, product or time convention')
    if field not in ('tMin','tMax','solarRad'):raise ValueError('Unsupported field')
    times=payload['time'];values=payload[field]
    if len(times)!=len(values) or len(set(times))!=len(times):
        raise ValueError('Unaligned or duplicate dates')
    value=values[times.index(day.isoformat())]
    if value == -999:return None
    value=finite_observation(value)
    return value*86400/1e6 if field=='solarRad' else value
