"""Read-only maize output and barrenness transition measurements."""
from pathlib import Path
import sys
from patch_metadata_source import once

EAR_FIELDS={'DATE':'REAL(YRDOY)','DYNAMIC':'REAL(DYNAMIC)','STAGE':'REAL(ISTAGE)',
 'EARS':'EARS','POPULATION':'PLTPOP','EARWT':'EARWT','LFWT':'LFWT','STMWT':'STMWT',
 'GRNWT':'GRNWT','GRAINN':'GRAINN','STOVN':'STOVN','STOVWT':'STOVWT',
 'TOPWT':'TOPWT','PODWT':'PODWT','CANOPY_N':'WTNCAN','SEED_N':'WTNSD',
 'YIELD':'YIELD','GNUP':'GNUP'}
BAR_FIELDS={'DATE':'REAL(YRDOY)','DYNAMIC':'REAL(DYNAMIC)','EARS':'EARS',
 'POPULATION':'PLTPOP','GPP':'GPP','G2':'G2','SUMP':'SUMP','IDURP':'REAL(IDURP)','PSKER':'PSKER'}


def event(prefix,fields,name,indent):
    block=''
    for key,value in fields.items():block+=f'{indent}MARS_{prefix}_{key} = {value}\n'
    block+=f'{indent}CALL pdi_transaction_begin("{name}")\n'
    for key in fields:block+=f'{indent}CALL pdi_expose("MARS_{prefix}_{key}",\n     &    MARS_{prefix}_{key}, pdi_out)\n'
    return block+f'{indent}CALL pdi_transaction_end()\n'


def patch_growth(text):
    if 'MARS_E_EARS' in text:raise ValueError('Ear audit already present')
    text=once(text,'      IMPLICIT  NONE','      IMPLICIT  NONE\n'+
              '\n'.join(f'      REAL MARS_E_{k}' for k in EAR_FIELDS))
    block=('      IF (DYNAMIC.EQ.OUTPUT .OR. DYNAMIC.EQ.SEASEND) THEN\n'+
           event('E',EAR_FIELDS,'mars_ear_output','        ')+'      ENDIF\n')
    return once(text,'      CALL pdi_transaction_begin("send_state_mz_grosub")',
                block+'      CALL pdi_transaction_begin("send_state_mz_grosub")')


def patch_phenology(text):
    if 'MARS_B_EARS' in text:raise ValueError('Barrenness audit already present')
    text=once(text,'      USE ModuleDefs','      USE pdi\n      USE ModuleDefs')
    text=once(text,'      IMPLICIT  NONE','      IMPLICIT  NONE\n'+
              '\n'.join(f'      REAL MARS_B_{k}' for k in BAR_FIELDS))
    anchor='              EARS           = AMAX1 (EARS,0.0)'
    return once(text,anchor,anchor+'\n'+event('B',BAR_FIELDS,'mars_barrenness','              '))


if __name__=='__main__':
    root=Path(sys.argv[1])/'Plant/CERES-Maize'
    for name,fn in [('MZ_GROSUB.for',patch_growth),('MZ_PHENOL.for',patch_phenology)]:
        p=root/name;p.write_text(fn(p.read_text()))
