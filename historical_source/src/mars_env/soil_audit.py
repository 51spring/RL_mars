"""Independent reconstruction of native soil budgets, with printed precision bounds.

Soil-only arithmetic checks do not certify crop elemental C or ecosystem closure.
"""
import math
import re
from pathlib import Path


def daily_table(text):
    header=None; rows=[]
    for line in text.splitlines():
        if line.startswith('@YEAR'):
            header=line[1:].split()
        elif header and re.match(r'^\s*\d{4}\s+\d{3}\s',line):
            values=line.split()
            if len(values)!=len(header):raise ValueError('Malformed native daily table')
            row=dict(zip(header,values))
            if not all(math.isfinite(float(x)) for x in values):raise ValueError('Nonfinite native table')
            date=int(row['YEAR'])*1000+int(row['DOY'])
            # Legacy close handshake starts another season and writes an initial row.
            if rows and date<=int(rows[-1]['YEAR'])*1000+int(rows[-1]['DOY']):break
            rows.append(row)
    if not rows:raise ValueError('Missing daily native table')
    return rows


def precision(token):
    return .5*10**(-len(token.partition('.')[2]))


def linear(terms):
    return sum(sign*float(token) for sign,token in terms),sum(precision(token) for _,token in terms)


def reconstruct_soil(folder):
    folder=Path(folder)
    carbon=daily_table((folder/'SoilCBal.OUT').read_text())
    organic=daily_table((folder/'SoilNoBal.OUT').read_text())
    inorganic=daily_table((folder/'SoilNiBal.OUT').read_text())
    reconstructions=[];maximum=0.;max_budget=0.
    # Native C incorporates yesterday's senescence, not today's printed amount.
    previous_senescence={'SNCLD':'0.00','SNCSD':'0.00'}
    for row in carbon:
        terms=[(1,row[k]) for k in ('SOMC0T','SOMCT','LC0D','LCTD','CH4STD','CO2ED','CH4ED','CH4LCD','CH4COD')]
        terms +=[(-1,row[k]) for k in ('SOMC0Ti','SOMCTi','LC0Di','LCTDi','CH4STDi','RESC0D','RESC1D','THRC0D','THRC1D')]
        terms +=[(-1,previous_senescence[k]) for k in ('SNCLD','SNCSD')]
        residual,bound=linear(terms);error=abs(residual-float(row['DAYBAL']))
        assert error<=bound+precision(row['DAYBAL'])+1e-8,(row,error,bound)
        maximum=max(maximum,error);max_budget=max(max_budget,bound)
        previous_senescence=row
    reconstructions.append({'compartment':'soil_carbon','days':len(carbon),'max_reconstruction_error':maximum,
        'max_print_rounding_bound':max_budget,'unit':'kg C/ha','native_final_cumulative_residual':float(carbon[-1]['CUMBAL']),
        'max_native_daily_residual':max(abs(float(r['DAYBAL'])) for r in carbon),
        'senescence_transfer':'native one-day lag preserved','arithmetic_passed':True})
    definitions=[('soil_organic_n',organic,('HUMN','FON','RESN'),('RMINERP',),('ARESN','ASENN','AIMMOBN')),
        ('soil_inorganic_n',inorganic,('NO3','NH4','TUREA','TNGAS','FLOODN','ALGFIX','UNFERT'),
         ('RIMMOB','RLCH','RLTD','RNUP','RNRO','RAML','N2OED','N2ED','NOED'),('AFERT','AMINER'))]
    for name,rows,stocks,losses,inputs in definitions:
        maximum=0.;max_budget=0.
        for previous,current in zip(rows,rows[1:]):
            terms=[(1,current[k]) for k in (*stocks,*losses)]+[(-1,previous[k]) for k in stocks]
            terms +=[(-1,previous[k] if name=='soil_organic_n' and k=='ASENN' else current[k]) for k in inputs]
            residual,bound=linear(terms);error=abs(residual-float(current['DBAL']))
            assert error<=bound+precision(current['DBAL'])+1e-8,(name,current,error,bound)
            maximum=max(maximum,error);max_budget=max(max_budget,bound)
        reconstructions.append({'compartment':name,'days':len(rows)-1,'max_reconstruction_error':maximum,
            'max_print_rounding_bound':max_budget,'unit':'kg N/ha','native_final_cumulative_residual':float(rows[-1]['CBAL']),
            'max_native_daily_residual':max(abs(float(r['DBAL'])) for r in rows),
            'arithmetic_passed':True})
    return {'soil_arithmetic_reconstruction_passed':True,'checks':reconstructions,
        'native_residual_is_not_independent_ecosystem_validation':True,
        'whole_crop_soil_n_balance_validated':False,'whole_elemental_carbon_balance_validated':False,
        'remaining':['plant C assimilation/respiration/tissue composition and seed C',
                     'cross-compartment daily plant/soil senescence timing',
                     'harvest exports and post-harvest residue transfer']}


def preharvest_n_inventory(folder, final_audit):
    """Combine soil compartments and native plant/export stocks at maturity.

    Harvest has not been removed from native plant stocks: do not add harvested
    grain N a second time, and do not claim post-harvest ecosystem closure.
    """
    text=(Path(folder)/'SoilNBalSum.OUT').read_text()
    header=next(line[1:].split() for line in text.splitlines() if line.startswith('@Run'))
    rows=[line.split() for line in text.splitlines() if re.match(r'^\s*\d+\s+\S+\s+\d+\s+[A-Z]{2}\s',line)]
    if len(rows)!=1 or len(rows[0])!=len(header):raise ValueError('Expected one seasonal N summary')
    row=dict(zip(header,rows[0]))
    initial=('SN0Di','S1NTDi','S2NTDi','S3NTDi','LNTDi','NIADi')
    final=('SN0D','S1NTD','S2NTD','S3NTD','LNTD','NIAD')
    additions=('HRNH','RESNC','NICM')
    losses=('NLCM','TDFC','NGasC','RNRO')
    terms=[(1,row[k]) for k in (*final,*losses)]+[(-1,row[k]) for k in (*initial,*additions)]
    residual,bound=linear(terms)
    standing=10*(final_audit['canopy_n']+final_audit['rootn']*final_audit['population'])
    exported=10*final_audit['cum_n'];seed=10*final_audit['seed_n']
    residual+=standing+exported-seed
    bound+=4*2**-23*(abs(standing)+abs(exported)+abs(seed))
    assert abs(residual)<=bound,(residual,bound)
    return {'maturity_before_physical_harvest_n_inventory_passed':True,
        'residual_kg_n_ha':residual,'print_and_native_roundoff_bound_kg_n_ha':bound,
        'standing_plant_including_grain_n_kg_ha':standing,'damage_export_n_kg_ha':exported,
        'seed_n_kg_ha':seed,'native_senescence_transfer_kg_n_ha':float(row['SNNTC']),
        'plant_uptake_and_senescence_are_internal_fluxes_not_external_inputs':True,
        'harvest_grain_n_added_again':False,'post_harvest_n_balance_validated':False,
        'whole_elemental_carbon_balance_validated':False}
