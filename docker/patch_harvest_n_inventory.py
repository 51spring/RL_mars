"""Experimental maize-only harvest consumer: avoid duplicate tracked leaf N."""
from pathlib import Path
import sys
from patch_metadata_source import once


def patch(text):
    if 'MARS_N_HARV_SEN' in text:
        raise ValueError('Harvest N candidate already installed')
    text=once(text,'      Type (ResidueType) SENESCE',
              '      Type (ResidueType) SENESCE\n      Type (ResidueType) MARS_N_HARV_SEN')
    anchor='        CALL HRes_Ceres(CONTROL,'
    block=('!       CumLfNSenes is tracked without removal from STOVN.\n'
           '!       Retained canopy N is already passed via STOVN.\n'
           '!       Preserve original SENESCE for all other consumers.\n'
           '        MARS_N_HARV_SEN = SENESCE\n'
           '        MARS_N_HARV_SEN % ResE(0,N) = 0.0\n')
    text=once(text,anchor,block+anchor)
    start=text.index(anchor);end=text.index('!Output',start)+len('!Output')
    call=text[start:end]
    call=once(call,'     &    RTWT, SENESCE, STOVN, STOVWT, WTNSD,            !Input',
              '     &    RTWT, MARS_N_HARV_SEN, STOVN,\n     &    STOVWT, WTNSD,                               !Input')
    if any(len(line)>72 for line in (block+call).splitlines()):
        raise ValueError('Candidate exceeds native fixed form width')
    return text[:start]+call+text[end:]


if __name__=='__main__':
    path=Path(sys.argv[1])/'Plant/CERES-Maize/MZ_CERES.for'
    path.write_text(patch(path.read_text()))
