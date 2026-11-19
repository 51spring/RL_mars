"""Explicit two-year Q-mode inputs and native residue boundaries."""
import re
from .sequence_audit import sequence_filex,replace_controls,rounded_balance
from .audits import shift_yrdoy


def two_year_filex(template,grain_percent=100,stover_percent=0):
    lines=sequence_filex(template,grain_percent,stover_percent,'Q').splitlines()
    treatment=next(i for i,l in enumerate(lines) if l.startswith('@N R O C '))
    first,second=lines[treatment+1:treatment+3]
    def clone(row,rotation,control):
        spans=list(re.finditer(r'\S+',row))[-13:]
        for index,value in sorted({3:0,12:control}.items(),reverse=True):
            m=spans[index];row=row[:m.start()]+str(value).rjust(m.end()-m.start())+row[m.end():]
        return row[:3]+str(rotation)+row[4:]
    lines[treatment+3:treatment+3]=[clone(first,3,3),clone(second,4,4)]
    starts=[i for i,l in enumerate(lines) if l.startswith('@N GENERAL')]
    if len(starts)!=2:raise ValueError('Expected original two control blocks')
    crop=lines[starts[0]:starts[1]];fallow=lines[starts[1]:]
    def control_copy(block,old,new):
        return [re.sub(r'^(\s*)'+str(old)+r'(\s+\w{2}\s)',
                       lambda m:m[1]+str(new)+m[2],line) for line in block]
    # Keep only the first overall horizon at two years; later controls must
    # not reset CSM's saved sequence start year.
    replace_controls(lines,'@N GENERAL',{'NYERS':2})
    lines+=['']+control_copy(crop,1,3)+['']+control_copy(fallow,2,4)
    return '\n'.join(lines)+'\n'


def audit_boundaries(diagnostics,*,expected_mode='Q'):
    if expected_mode not in ('Q','F'):raise ValueError('Unsupported sequence mode')
    harvests={int(h['run']):h for h in diagnostics['harvests']}
    if set(harvests)!={1,3}:raise ValueError('Expected maize harvests in runs1/3')
    if [int(harvests[r]['date'])//1000 for r in (1,3)]!=[1982,1983]:
        raise ValueError('Expected different native crop years')
    soils=diagnostics['soils'];results=[]
    if {int(s['run']) for s in soils}!={1,2,3,4}:raise ValueError('Expected four soil initializations')
    for run in (2,3,4):
        before=[s for s in soils if s['run']==run and s['phase']==1]
        after=[s for s in soils if s['run']==run and s['phase']==2]
        if len(before)!=1 or len(after)!=1:raise ValueError('Missing/duplicate soil boundary event')
        b,a=before[0],after[0]
        crop=(ord('M'),ord('Z')) if run==3 else (ord('F'),ord('A'))
        expected_date=1983030 if run==3 else shift_yrdoy(harvests[run-1]['date'],1)
        if any((s['crop1'],s['crop2'])!=crop or s['date']!=expected_date or s['rnmode']!=ord(expected_mode) for s in (b,a)):
            raise ValueError('Native crop/calendar/mode boundary differs')
        checks={}
        for stock,incoming in (('soil_dm','root_dm'),('soil_n','root_n'),('mulch_dm','surface_dm'),('mulch_n','surface_n')):
            checks[stock]=rounded_balance(a[stock]-b[stock],b[incoming],abs(a[stock])+abs(b[stock])+abs(b[incoming]))
        if run==3:
            if any(b[k]!=0 for k in ('root_dm','root_n','surface_dm','surface_n')):
                raise ValueError('Old harvest residue repeated after fallow')
        else:
            h=harvests[run-1]
            for key,fields in (('residue_dm',('surface_dm','root_dm')),('residue_n',('surface_n','root_n'))):
                incoming=sum(b[f] for f in fields)
                checks[key]=rounded_balance(incoming,h[key],abs(incoming)+abs(h[key]))
        results.append({'incoming_run':run,'date':int(b['date']),'checks':checks,
            'passed':all(c['passed'] for c in checks.values()),'old_residue_repeated':False})
    return {'passed':all(r['passed'] for r in results),'boundaries':results,
        'multiyear_full_n_balance_verified':False,'whole_elemental_carbon_verified':False,'research_ready':False}
