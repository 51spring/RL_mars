"""Fail-closed boundary for explicit package diagnostics, never field validation."""
from datetime import datetime,timedelta
import math
import re

UNITS={'pldp':'mm','texture':'percent','soil_depth':'cm','initial_n':'ppm_N_dry_soil','water':'cm3/cm3'}


def validate_export(exp,units,cultivar_text,*,purpose,writer_version):
    errors=[]
    if purpose!='package_diagnostic':errors.append('Only package_diagnostic purpose is supported')
    if writer_version not in ('1.2.18','1.2.21'):errors.append('Writer version not qualified')
    if units!=UNITS:errors.append('Missing or unknown unit declaration')
    def numeric(row,key,path,low=None,high=None):
        try:
            raw=row[key]
            if isinstance(raw,bool):raise ValueError()
            value=float(raw)
            if not math.isfinite(value) or value in (-99,-999):raise ValueError()
            if low is not None and value<low:raise ValueError()
            if high is not None and value>high:raise ValueError()
            return value
        except (KeyError,TypeError,ValueError):
            errors.append(path+'.'+key+': missing/sentinel/nonfinite/out-of-range');return None
    try:
        soil=exp['soil'];weather=exp['weather'];events=exp['management']['events']
        if exp.get('soil_id')!=soil.get('soil_id') or exp.get('sid')!=soil.get('sid'):
            errors.append('Soil reference mismatch')
        if exp.get('wst_id')!=weather.get('wst_id') or exp.get('wid')!=weather.get('wid'):
            errors.append('Weather reference mismatch')
        planting=[e for e in events if e.get('event')=='planting']
        if len(planting)!=1:errors.append('Require exactly one planting event');return errors
        planting=planting[0]
        depth=numeric(planting,'pldp','planting',0)
        if depth==0:errors.append('Zero planting depth')
        cultivar=planting.get('cul_id','')
        if not cultivar or not re.search(r'^'+re.escape(cultivar)+r'\s',cultivar_text,re.M):
            errors.append('Cultivar coefficient row missing')
        layers=soil['soilLayer'];top=0.
        for i,s in enumerate(layers):
            path=f'soil[{i}]';base=numeric(s,'sllb',path,0)
            if base is not None and base<=top:errors.append(path+': nonincreasing depth')
            top=base if base is not None else top
            ll=numeric(s,'slll',path,0,1);dul=numeric(s,'sldul',path,0,1);sat=numeric(s,'slsat',path,0,1)
            if None not in (ll,dul,sat) and not ll<=dul<=sat:errors.append(path+': LL/DUL/SAT order')
            bulk=numeric(s,'slbdm',path,0)
            if bulk==0:errors.append(path+': zero bulk density')
            fractions=[numeric(s,k,path,0,100) for k in ('slcly','slsnd','slsil')]
            if None not in fractions and abs(sum(fractions)-100)>1e-6:
                errors.append(path+': texture must sum to100 percent; no automatic rescaling')
        if not layers:errors.append('Empty soil profile')
        for k,maximum in (('sldr',1),('salb',1),('slpf',1),('slro',100)):
            numeric(soil,k,'soil.surface',0,maximum)
        initial=exp['initial_conditions'];previous=0.
        for i,layer in enumerate(initial['soilLayer']):
            initial_top=previous
            base=numeric(layer,'icbl',f'initial[{i}]',0)
            if base is not None and (base<=previous or base>top):errors.append('Initial layer coverage/order mismatch')
            previous=base if base is not None else previous
            theta=numeric(layer,'ich2o',f'initial[{i}]',0,1)
            if theta is not None and base is not None:
                soil_top=0.
                for soil_layer in layers:
                    soil_base=float(soil_layer['sllb'])
                    if min(base,soil_base)>max(initial_top,soil_top):
                        if theta>float(soil_layer['slsat']):errors.append(f'initial[{i}]: water exceeds overlapping soil saturation')
                    soil_top=soil_base
            for k in ('icno3','icnh4'):numeric(layer,k,f'initial[{i}]',0)
        if not initial['soilLayer']:errors.append('Empty initial profile')
        for i,event in enumerate(events):
            if event['event']=='fertilizer':
                numeric(event,'fedep',f'fertilizer[{i}]',0);numeric(event,'feamn',f'fertilizer[{i}]',0)
        dates={k:datetime.strptime(v,'%Y%m%d') for k,v in
            (('planting',planting['date']),('start',exp['sdat']),('end',exp['endat']),('initial',initial['icdat']))}
        if not dates['initial']<=dates['start']<=dates['planting']<dates['end']:
            errors.append('Initial/start/planting/end date order invalid')
        seen={}
        for row in weather['dailyWeather']:
            day=datetime.strptime(row['w_date'],'%Y%m%d')
            if day in seen:errors.append('Duplicate weather date')
            seen[day]=row
            values={key:numeric(row,key,'weather.'+row['w_date'],0 if key in ('srad','rain') else None)
                for key in ('tmin','tmax','srad','rain')}
            if values['tmin'] is not None and values['tmax'] is not None and values['tmin']>values['tmax']:
                errors.append('Weather minimum exceeds maximum')
        day=dates['start']
        while day<=dates['end']:
            if day not in seen:errors.append('Missing weather date '+day.strftime('%Y%m%d'))
            day+=timedelta(days=1)
    except (KeyError,TypeError,ValueError) as exc:
        errors.append('Incomplete diagnostic input: '+str(exc))
    return errors


def require_export(exp,units,cultivar_text,*,purpose,writer_version):
    """Executable gate for the writer caller, also active under python -O."""
    errors=validate_export(exp,units,cultivar_text,purpose=purpose,writer_version=writer_version)
    if errors:raise ValueError('Diagnostic export blocked: '+'; '.join(errors))
