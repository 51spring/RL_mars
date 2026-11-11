"""Read-only Q/F crop-to-soil handoff diagnostics on a container source copy."""
from pathlib import Path
import sys
from patch_metadata_source import once

CROP_FIELDS={'RUN':'REAL(CONTROL % RUN)','STOVER_DM':'STOVWT * PLTPOP * 10.0',
 'STOVER_N':'STOVN * PLTPOP * 10.0','POD_DM':'PODWT * 10.0',
 'ALL_GRAIN_DM':'GRNWT * PLTPOP * 10.0',
 'ROOT_SEN_DM':'SUM(SENESCE % ResWt(1:NLAYR))',
 'ROOT_SEN_N':'SUM(SENESCE % ResE(1:NLAYR,1))'}
SOIL_FIELDS={'RUN':'REAL(RUN)','RNMODE':'REAL(IACHAR(RNMODE))','DATE':'REAL(CONTROL % YRDOY)',
 'CROP1':'REAL(IACHAR(CROP(1:1)))','CROP2':'REAL(IACHAR(CROP(2:2)))',
 'ROOT_DM':'SUM(HARVRES % ResWt(1:NLAYR))','ROOT_N':'SUM(HARVRES % ResE(1:NLAYR,1))',
 'SURFACE_DM':'HARVRES % ResWt(0)','SURFACE_N':'HARVRES % ResE(0,1)',
 'SOIL_DM':'SUM(FOM(1:NLAYR))','SOIL_N':'SUM(FON(1:NLAYR))',
 'MULCH_DM':'MULCH % MULCHMASS','MULCH_N':'MULCH % MULCHN'}


def patch_crop(text):
    if 'MARS_Q_RUN' in text:raise ValueError('Sequence crop audit already present')
    text=once(text,'      IMPLICIT NONE','      IMPLICIT NONE\n'+ '\n'.join(f'      REAL MARS_Q_{x}' for x in CROP_FIELDS))
    block=''
    for name,value in CROP_FIELDS.items():block+=f'        MARS_Q_{name} = {value}\n'
    # Data is available to the already-existing harvest-boundary event.
    block+='        CALL pdi_transaction_begin("mars_sequence_crop")\n'
    for name in CROP_FIELDS:block+=f'        CALL pdi_expose("MARS_Q_{name}",\n     &      MARS_Q_{name}, pdi_out)\n'
    block+='        CALL pdi_transaction_end()\n'
    return once(text,'        CALL pdi_transaction_begin("mars_harvest_boundary")',
        block+'        CALL pdi_transaction_begin("mars_harvest_boundary")')


def soil_event(phase):
    block=f'      MARS_S_PHASE = {float(phase)}\n'
    for name,value in SOIL_FIELDS.items():
        if phase==1 and name in ('ROOT_DM','ROOT_N','SURFACE_DM','SURFACE_N','SOIL_DM','SOIL_N','MULCH_DM','MULCH_N'):
            block+=f'      MARS_S_{name} = 0.0\n      IF (RUN > 1) MARS_S_{name} = {value}\n'
        else:block+=f'      MARS_S_{name} = {value}\n'
    block+='      CALL pdi_transaction_begin("mars_soil_init")\n'
    for name in ('PHASE',*SOIL_FIELDS):block+=f'      CALL pdi_expose("MARS_S_{name}",\n     &    MARS_S_{name}, pdi_out)\n'
    block+='      CALL pdi_transaction_end()\n'
    return block


def patch_soil(text):
    if 'MARS_S_PHASE' in text:raise ValueError('Sequence soil audit already present')
    text=once(text,'      USE ModuleDefs','      USE pdi\n      USE ModuleDefs')
    declaration='\n'.join(f'      REAL MARS_S_{x}' for x in ('PHASE',*SOIL_FIELDS))+'\n'
    text=once(text,'      INTEGER RUN\n','      INTEGER RUN\n'+declaration)
    anchor='      IF (RUN .EQ. 1 .OR. INDEX(\'QF\',RNMODE) .LE. 0) THEN'
    text=once(text,anchor,soil_event(1)+anchor)
    text=once(text,'      RETURN\n      END SUBROUTINE SoilOrg_init',soil_event(2)+'      RETURN\n      END SUBROUTINE SoilOrg_init')
    return text


if __name__=='__main__':
    root=Path(sys.argv[1])
    for relative,fn in [('Plant/CERES-Maize/MZ_CERES.for',patch_crop),('Soil/CERES_OrganicMatter/SoilOrg_init.for',patch_soil)]:
        p=root/relative;result=fn(p.read_text(encoding='latin-1'))
        # Native fixed-form build uses extended lines, but keep all inserted executable lines <= 100.
        p.write_text(result,encoding='latin-1')
