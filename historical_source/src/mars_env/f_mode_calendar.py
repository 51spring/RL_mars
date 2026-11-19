"""Explicit F-mode treatment and date inputs; Q scheduling is not reused."""
import re
from .multiyear_audit import two_year_filex
from .sequence_audit import sequence_filex,replace_controls
from .audits import shift_yrdoy


def year_code(date):
    shift_yrdoy(date,0)
    year,doy=divmod(int(date),1000)
    return (year%100)*1000+doy


def f_filex(template,grain,stover,harvest_dates,*,two_years=True):
    needed=(1,3) if two_years else (1,)
    for run in needed:
        if run not in harvest_dates or int(harvest_dates[run])//1000!=(1982 if run==1 else 1983):
            raise ValueError('Measured harvest date for each crop year is required')
        shift_yrdoy(harvest_dates[run],0)
    if not two_years:return sequence_filex(template,grain,stover,'F',harvest_dates[1])
    lines=two_year_filex(template,grain,stover).splitlines()
    start=next(i for i,l in enumerate(lines) if l.startswith('@N R O C '))
    for index in range(4):
        i=start+1+index;row=lines[i]
        row=row[:1]+str(index+1)+row[2:3]+'1'+row[4:]
        changes={4:2} if index==2 else ({11:2} if index==3 else {})
        spans=list(re.finditer(r'\S+',row))[-13:]
        for field,value in sorted(changes.items(),reverse=True):
            m=spans[field];row=row[:m.start()]+str(value).rjust(m.end()-m.start())+row[m.end():]
        lines[i]=row
    p=next(i for i,l in enumerate(lines) if l.startswith('@P PDATE'))
    second=[lines[p],lines[p+1]]
    replace_controls(second,'@P PDATE',{'PDATE':83057})
    second[1]=second[1][:1]+'2'+second[1][2:]
    lines.insert(p+2,second[1])
    h=next(i for i,l in enumerate(lines) if l.startswith('@H HDATE'))
    second=[lines[h],lines[h+1]]
    replace_controls(second,'@H HDATE',{'HDATE':84029})
    second[1]=second[1][:1]+'2'+second[1][2:]
    lines.insert(h+2,second[1])
    starts=[i for i,l in enumerate(lines) if l.startswith('@N GENERAL')]
    # F's CSM reads the explicit close date, then starts on the next day.
    for block,date in ((1,harvest_dates[1]),(2,1983029),(3,harvest_dates[3])):
        index=starts[block];pair=lines[index:index+2]
        replace_controls(pair,'@N GENERAL',{'SDATE':year_code(date)})
        lines[index+1]=pair[1]
    return '\n'.join(lines)+'\n'


def launcher_text(treatments):
    if treatments not in (2,4):raise ValueError('F diagnostic supports2 or4 treatments')
    rows='\n'.join(f"printf '%-92s %6d %6d %6d\\n' 'MARS8201.SQX' {i} 1 1" for i in range(1,treatments+1))
    return ('#!/bin/sh\nset -eu\ncp fileX.MZX MARS8201.SQX\n{\n'
        "printf '%s\\n' '$BATCH(MARS MULTIYEAR F)' '@FILEX                                                                                         TRTNO RP SQ'\n"
        +rows+'\n} > MARS_SEQ.BAT\n'
        'exec "${MARS_SEQUENCE_BINARY}" F MARS_SEQ.BAT\n')
