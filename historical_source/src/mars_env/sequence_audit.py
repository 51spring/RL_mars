"""Diagnostic maize-to-fallow input and privileged sequence protocol."""
import re
from .harvest_diagnostics import HarvestProtocol

Q_FIELDS=('RUN','STOVER_DM','STOVER_N','POD_DM','ALL_GRAIN_DM','ROOT_SEN_DM','ROOT_SEN_N')
S_FIELDS=('PHASE','RUN','RNMODE','DATE','CROP1','CROP2','ROOT_DM','ROOT_N','SURFACE_DM','SURFACE_N',
          'SOIL_DM','SOIL_N','MULCH_DM','MULCH_N')


def rounded_balance(actual, expected, scale):
    """Conservative gamma_64 bound for <=20-layer binary32 native sums.

    Up to 20 layer additions plus two reductions and four scalar operations.
    Inputs are nonnegative stocks. This is arithmetic verification, not a
    fitted tolerance for missing physical fluxes.
    """
    import math
    if not all(math.isfinite(v) for v in (actual, expected, scale)) or scale < 0:
        raise ValueError('Invalid native balance values')
    u = 2. ** -24
    bound = (64 * u / (1 - 64 * u)) * max(scale, 1e-30)
    return {'actual':actual,'expected':expected,'residual':actual-expected,
            'binary32_roundoff_bound':bound,'passed':abs(actual-expected)<=bound}


def analyze_handoff(result):
    harvests = result['harvests']
    if len(harvests) != 1:
        raise ValueError('Expected one maize harvest before fallow')
    h = harvests[0]
    soils = result['soils']
    before = [s for s in soils if s['run']==2 and s['phase']==1]
    after = [s for s in soils if s['run']==2 and s['phase']==2]
    if len(before)!=1 or len(after)!=1:
        raise ValueError('Missing unique native next-season soil boundary')
    b, a = before[0], after[0]
    from .audits import shift_yrdoy
    if ((b['crop1'],b['crop2']) != (ord('F'),ord('A'))
            or (a['crop1'],a['crop2']) != (ord('F'),ord('A'))
            or b['date'] != shift_yrdoy(h['date'],1) or a['date']!=b['date']
            or a['rnmode']!=b['rnmode'] or b['rnmode']!=h['rnmode']):
        raise ValueError('Unexpected fallow/date boundary')
    checks = {}
    for target, incoming in [('soil_dm','root_dm'),('soil_n','root_n'),
                             ('mulch_dm','surface_dm'),('mulch_n','surface_n')]:
        checks[target] = rounded_balance(a[target]-b[target], b[incoming],
                                        abs(a[target])+abs(b[target])+abs(b[incoming]))
    for field, surface, root in [('residue_dm','surface_dm','root_dm'),
                                 ('residue_n','surface_n','root_n')]:
        checks[field] = rounded_balance(b[surface]+b[root], h[field],
                                        abs(b[surface])+abs(b[root])+abs(h[field]))
    gf, sf = h['grain_fraction'], h['stover_fraction']
    # Producer already converts CumLeafSenes to kg/ha using PLTPOP * 10.
    # CumLfNSenes is not subtracted from STOVN and is included in canopy N.
    expected_dm = ((h['canopy_dm']-h['all_grain_dm']+h['dead_leaf_dm_raw'])*(1-sf)
                   +h['all_grain_dm']*(1-gf)+h['root_dm']+h['root_sen_dm'])
    expected_n = ((h['canopy_n']-h['grain_n'])*(1-sf)
                  +h['grain_n']*(1-gf)+h['root_n']+h['root_sen_n'])
    partition = {key:rounded_balance(h[key], expected, abs(h[key])+abs(expected))
                 for key,expected in [('residue_dm',expected_dm),('residue_n',expected_n)]}
    return {'handoff_passed':all(c['passed'] for c in checks.values()),'handoff':checks,
            'partition_passed':all(c['passed'] for c in partition.values()),'partition':partition,
            'predicted_native_duplicate_n':h['dead_leaf_n_raw']*(1-sf),
            'dead_leaf_dm_unit':'kg dry matter/ha','dead_leaf_n_unit':'kg N/ha; included in canopy N',
            'native_partition_conservation_verified':all(c['passed'] for c in partition.values()),
            'scope':'maize harvest partition and immediate fallow soil initialization',
            'whole_elemental_carbon_balance_verified':False,
            'whole_postharvest_system_balance_verified':False,'research_ready':False}


def replace_controls(lines,header_marker,changes):
    for i,line in enumerate(lines):
        if line.startswith(header_marker):
            headers=list(re.finditer(r'\S+',line));keys=[m.group() for m in headers]
            row=lines[i+1]
            if '{{' in row: raise ValueError('Render FileX controls before editing fixed-width fields')
            replacements={keys.index(key):str(value) for key,value in changes.items()}
            for index in sorted(replacements,reverse=True):
                left,right=headers[index-1].end(),headers[index].end()
                value=replacements[index]
                if len(value)>right-left:raise ValueError('Control exceeds fixed field width')
                row=row[:left]+value.rjust(right-left)+row[right:]
            lines[i+1]=row;return
    raise ValueError(f'Missing control header {header_marker}')


def sequence_filex(template,grain_percent=100,stover_percent=0,mode='Q',fallow_start=None):
    from .audits import enable_audit_outputs
    from .input_metadata import canonical_ufga_metadata
    if not 0<=grain_percent<=100 or not 0<=stover_percent<=100:raise ValueError('Invalid harvest fractions')
    if mode not in ('Q','F'): raise ValueError('Invalid sequence mode')
    lines=canonical_ufga_metadata(enable_audit_outputs(template)).splitlines()
    begin=next(i for i,l in enumerate(lines) if l.startswith('@N R O C '))
    end=begin+1
    while end<len(lines) and lines[end].strip():end+=1
    original=lines[begin+1]
    def treatment(rotation,cultivar,controls,fallow):
        row=original
        spans=list(re.finditer(r'\S+',row))[-13:]
        values=[cultivar,1,0,0 if fallow else 1,0 if fallow else 1,0 if fallow else 1,
                0 if fallow else 1,0,0,0,0,1 if fallow else 0,controls]
        for m,v in reversed(list(zip(spans,values))):row=row[:m.start()]+str(v).rjust(m.end()-m.start())+row[m.end():]
        row=row[:3]+str(rotation)+row[4:5]+'1'+row[6:]
        return row
    lines[begin+1:end]=[treatment(1,1,1,False),treatment(2,2,2,True)]
    if mode=='F':
        row=lines[begin+2]
        lines[begin+2]=row[:1]+'2'+row[2:3]+'1'+row[4:]
    cultivar=next(i for i,l in enumerate(lines) if l.startswith('@C CR INGENO'))
    lines.insert(cultivar+2,' 2 FA IB0001 Fallow')
    planting=next(i for i,l in enumerate(lines) if l.startswith('*IRRIGATION'))
    # Explicit fallow harvest date closes the one-year diagnostic window.
    lines[planting:planting]=['*HARVEST DETAILS','@H HDATE  HSTG  HCOM HSIZE   HPC  HBPC HNAME',
                             ' 1 83029 GS000   -99   -99   100     0 Fallow end','']
    replace_controls(lines,'@N GENERAL',{'NYERS':1,'NREPS':1})
    replace_controls(lines,'@N HARVEST ',{'HPCNP':grain_percent,'HPCNR':stover_percent})
    start=next(i for i,l in enumerate(lines) if l.startswith('*SIMULATION CONTROLS'))
    second=lines[start+1:].copy()
    # F rereads the explicit start date, then adds one day. Use a measured
    # maize harvest date for expanded cases; legacy default remains 82192.
    if mode=='F':
        if fallow_start is None: last_crop_date=82192
        else:
            from .audits import shift_yrdoy
            shift_yrdoy(fallow_start,0)  # Reject malformed native dates.
            year,doy=divmod(int(fallow_start),1000)
            last_crop_date=(year%100)*1000+doy
        replace_controls(second,'@N GENERAL',{'SDATE':last_crop_date})
    replace_controls(second,'@N MANAGEMENT',{'PLANT':'R','IRRIG':'R','FERTI':'R','RESID':'N','HARVS':'R'})
    second=[re.sub(r'^(\s*)1(\s+\w{2}\s)',r'\g<1>2\2',line) for line in second]
    lines+=['']+second
    return '\n'.join(lines)+'\n'


class SequenceProtocol(HarvestProtocol):
    def patch_template(self,template):
        template=super().patch_template(template)
        template=template.replace('          done = False',
            '          mars_sequence_harvests = []\n          mars_sequence_soils = []\n          done = False',1)
        marker="          'totir': totir,"
        template=template.replace(marker,marker+"\n          'mars_sequence_harvests': mars_sequence_harvests,\n          'mars_sequence_soils': mars_sequence_soils,")
        for prefix,fields in [('Q',Q_FIELDS),('S',S_FIELDS)]:
            template=template.replace('\ndata:\n','\ndata:\n'+''.join(f'  MARS_{prefix}_{key}: float\n' for key in fields),1)
            template=template.replace('    on_data:\n','    on_data:\n'+''.join(
                f'      MARS_{prefix}_{key}: |\n        mars_{prefix.lower()}_{key.lower()} = MARS_{prefix}_{key}\n' for key in fields),1)
        # Append to the existing harvest event after its record assignment.
        lines=template.splitlines()
        for i,line in enumerate(lines):
            if line.startswith('          mars_harvest_record = {'):
                extra=', '.join(f"'{key.lower()}': float(mars_q_{key.lower()})" for key in Q_FIELDS)
                lines.insert(i+1,f'          mars_sequence_harvests.append(dict(mars_harvest_record, **{{{extra}}}))')
                break
        template='\n'.join(lines)+'\n'
        fields=', '.join(f"'{key.lower()}': float(mars_s_{key.lower()})" for key in S_FIELDS)
        event='      mars_soil_init:\n        exec: |\n'+f'          mars_sequence_soils.append({{{fields}}})\n'
        return template.replace('    on_event:\n','    on_event:\n'+event,1)


from .dssat_backend import DssatBackend, BackendContractError


class SequenceAuditBackend(DssatBackend):
    """Private Q/F diagnostic, with no single-crop terminal classification."""
    def __init__(self, *, grain_percent=100, stover_percent=0, fallow_start=None):
        import os
        mode=os.environ.get('MARS_SEQUENCE_MODE','Q')
        super().__init__(run_dssat_location='/opt/mars/run_sequence',
            filex_transform=lambda t: sequence_filex(t, grain_percent, stover_percent, mode, fallow_start))
        self._instrumentation = SequenceProtocol()

    def step_damage(self, water, nitrogen, fraction=0.):
        import math
        if self._env is None or self.finished or self.broken:
            raise BackendContractError('Reset a usable sequence backend before stepping')
        if any(not math.isfinite(v) or not 0 <= v <= limit
               for v, limit in ((water, 50), (nitrogen, 200), (fraction, 1))):
            raise ValueError('Invalid sequence diagnostic action')
        self._instrumentation.fraction = float(fraction)
        try:
            result = self._env.step({'amir': water, 'anfer': nitrogen})
            if result is None:
                raise BackendContractError('Sequence simulator returned no result')
            self.state = dict(self._env.received_state)
            self.finished = bool(result[2])
            return self.state, self.finished, None
        except Exception:
            self.broken = True
            raise

    def step(self, water, nitrogen):
        return self.step_damage(water, nitrogen)
