"""Experimental maize harvest interface using standing stocks + actual exports.

No growth, phenology, original state, or report equations are changed. P and
zero-population/zero-stover cases require separate validation.
"""
from pathlib import Path
import sys
from patch_metadata_source import once


def patch(text):
    if 'MARS_A_GRAIN' in text:raise ValueError('Actual-export adapter already present')
    if 'MARS_N_HARV_SEN' not in text:raise ValueError('Expected N inventory candidate as base')
    text=once(text,'      IMPLICIT NONE','      IMPLICIT NONE\n'
        '      REAL MARS_A_GRAIN, MARS_A_POD, MARS_A_STOVN\n'
        '      REAL MARS_A_SEEDN')
    anchor='        CALL HRes_Ceres(CONTROL,'
    block=('!       Interface translation only: preserve standing stocks and\n'
           '!       actual YIELD/GNUP/BWAH reports, including barren ears.\n'
           '        MARS_A_GRAIN = GRNWT\n'
           '        MARS_A_POD = PODWT\n'
           '        MARS_A_STOVN = STOVN\n'
           '        MARS_A_SEEDN = WTNSD\n'
           '        IF (PLTPOP.GT.0.0 .AND. STOVWT.GT.1.E-5) THEN\n'
           '          MARS_A_GRAIN = YIELD / (10.0 * PLTPOP)\n'
           '          MARS_A_POD = TOPWT - STOVWT * PLTPOP\n'
           '          MARS_A_SEEDN = GNUP / 10.0\n'
           '          MARS_A_STOVN = (WTNCAN - MARS_A_SEEDN) / PLTPOP\n'
           '        ENDIF\n')
    text=once(text,anchor,block+anchor)
    start=text.index(anchor);end=text.index('!Output',start)+len('!Output')
    call=text[start:end]
    call=once(call,'CROP, DLAYR, GRNWT, HARVFRAC, NLAYR,',
                   'CROP, DLAYR, MARS_A_GRAIN, HARVFRAC, NLAYR,')
    call=once(call,'PConc_Seed, PLTPOP, PODWT, RLV, ROOTN,',
                   'PConc_Seed, PLTPOP, MARS_A_POD, RLV, ROOTN,')
    call=once(call,'RTWT, MARS_N_HARV_SEN, STOVN,','RTWT, MARS_N_HARV_SEN, MARS_A_STOVN,')
    call=once(call,'STOVWT, WTNSD,','STOVWT, MARS_A_SEEDN,')
    # Existing inline input comments may exceed column 72 after substitution.
    call='\n'.join(line.split('!Input')[0].rstrip() for line in call.splitlines())
    if any(len(line)>72 for line in (block+call).splitlines()):raise ValueError('Fixed-form width exceeded')
    return text[:start]+call+text[end:]


if __name__=='__main__':
    p=Path(sys.argv[1])/'Plant/CERES-Maize/MZ_CERES.for'
    p.write_text(patch(p.read_text()))
