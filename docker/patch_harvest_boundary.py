"""Read-only SEASEND diagnostic after native residue calculation."""
from pathlib import Path
import sys
from patch_metadata_source import once

FIELDS={
    'RNMODE': 'REAL(IACHAR(CONTROL % RNMODE))',
    'GRAIN_FRACTION': 'HARVFRAC(1)', 'STOVER_FRACTION':'HARVFRAC(2)',
    'GRAIN_DM':'SDWTAH * 10.0', 'GRAIN_N':'WTNSD * 10.0',
    'HARVEST_GRAIN_N':'GNUP * HARVFRAC(1)',
    'CANOPY_DM':'TOPWT * 10.0','CANOPY_N':'WTNCAN * 10.0',
    'ROOT_N':'ROOTN * PLTPOP * 10.0','ROOT_DM':'RTWT * PLTPOP * 10.0',
    'DEAD_LEAF_DM_RAW':'SENESCE % ResWt(0)',
    'DEAD_LEAF_N_RAW':'SENESCE % ResE(0,1)',
    'RESIDUE_DM':'SUM(HARVRES % ResWt)',
    'RESIDUE_N':'SUM(HARVRES % ResE(:,1))',
}


def patch(text):
    if 'MARS_H_RNMODE' in text:raise ValueError('Harvest diagnostics are already present')
    begin=text.index('      SUBROUTINE MZ_CERES (')
    # Native file includes the subroutine followed by its variable definitions.
    decl='      IMPLICIT NONE'
    assert text[begin:].count(decl)==1
    declarations='\n'.join(f'      REAL MARS_H_{name}' for name in FIELDS)
    text=once(text,decl,decl+'\n'+declarations)
    anchor='        !Set senescence variable to zero for next season'
    audit=''
    for name,value in FIELDS.items():audit+=f'        MARS_H_{name} = {value}\n'
    audit+='        CALL pdi_transaction_begin("mars_harvest_boundary")\n'
    for name in FIELDS:
        audit+=f'        CALL pdi_expose("MARS_H_{name}",\n     &      MARS_H_{name}, pdi_out)\n'
    audit+='        CALL pdi_transaction_end()\n\n'
    for line in (declarations+'\n'+audit).splitlines():
        if len(line)>72:raise ValueError('Diagnostic exceeds fixed-form line width')
    return once(text,anchor,audit+anchor)


if __name__=='__main__':
    path=Path(sys.argv[1])/'Plant/CERES-Maize/MZ_CERES.for'
    path.write_text(patch(path.read_text()))
