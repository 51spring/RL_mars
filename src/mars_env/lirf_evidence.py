"""Source summaries, without selecting or filling native model parameters."""
import calendar
from collections import defaultdict
from datetime import date
import math


def temperature_descriptions(records):
    """Describe complete calendar years using recorded daily mean air temperature.

    Full and half monthly ranges are both descriptive outputs, not a TAMP fit.
    """
    years=defaultdict(dict);monthly=defaultdict(list)
    for row in records:
        day=date.fromisoformat(row['date']);value=row['tmean_c']
        if isinstance(value,bool) or not isinstance(value,(float,int)) or not math.isfinite(value) or value in (-99,-999):
            raise ValueError('Missing/nonfinite daily mean air temperature')
        if day in years[day.year]:raise ValueError('Duplicate daily temperature date')
        years[day.year][day]=float(value);monthly[day.month].append(float(value))
    if not years:raise ValueError('No temperature observations')
    annual=[]
    for year,values in sorted(years.items()):
        if len(values)!=365+calendar.isleap(year):raise ValueError('Incomplete calendar year')
        means={m:math.fsum(v for d,v in values.items() if d.month==m)/calendar.monthrange(year,m)[1] for m in range(1,13)}
        span=max(means.values())-min(means.values())
        annual.append(dict(year=year,days=len(values),daily_weighted_mean_air_c=math.fsum(values.values())/len(values),
            monthly_mean_air_c=means,full_monthly_range_c=span,half_monthly_range_c=span/2))
    means={m:math.fsum(v)/len(v) for m,v in sorted(monthly.items())}
    span=max(means.values())-min(means.values())
    return dict(annual=annual,days=sum(len(y) for y in years.values()),
        pooled_daily_mean_air_c=math.fsum(v for y in years.values() for v in y.values())/sum(len(y) for y in years.values()),
        pooled_monthly_mean_air_c=means,pooled_full_monthly_range_c=span,pooled_half_monthly_range_c=span/2,
        temperature_input='recorded daily mean air, not mean of extrema or soil temperature',
        native_tav_tamp_selected=False,long_term_climate_normals=False)
