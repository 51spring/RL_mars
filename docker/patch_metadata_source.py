"""Fix diagnostic metadata on a container copy, never vendor crop equations."""
from pathlib import Path
import sys


def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f'Unsupported source anchor ({text.count(old)}): {old[:65]!r}')
    return text.replace(old, new, 1)


def patch_ipfld(text):
    start = text.index('      SUBROUTINE IPFLD (')
    end = text.index('      END SUBROUTINE IPFLD', start)
    block = text[start:end]
    block = once(block, '      LINEXP = 0\n',
        "      CXCRD = '           -999'\n      CYCRD = '            -99'\n"
        "      CELEV = '      -99'\n      XCRD = -999.0\n"
        "      YCRD = -99.0\n      ELEV = -99.0\n      LINEXP = 0\n")
    for variable in ('XCRD', 'YCRD', 'ELEV'):
        label = {'XCRD': "      READ(CXCRD,'(F15.0)', IOSTAT=ERRNUM) XCRD",
                 'YCRD': "      READ(CYCRD,'(F15.0)', IOSTAT=ERRNUM) YCRD",
                 'ELEV': "      READ(CELEV,'(F9.0)', IOSTAT=ERRNUM)  ELEV"}[variable]
        block = once(block, label + '\n      IF(ERRNUM .EQ. 0) THEN', label + '\n      IF(ERRNUM .NE. 0) THEN')
    block = once(block, '         XCRD = -999.0\n         MSG(1) = \'Error reading latitude',
                        '         XCRD = -999.0\n         MSG(1) = \'Error reading longitude')
    block = once(block, '         YCRD = -99.0\n         MSG(1) = \'Error reading longitude',
                        '         YCRD = -99.0\n         MSG(1) = \'Error reading latitude')
    # Coordinate validity depends on their own parsed values, not the last ELEV IOSTAT.
    block = once(block, '     &   (ABS(YCRD) .GT. 1.E-15 .OR. ABS(XCRD) .GT. 1.E-15).AND.\n     &   ERRNUM .NE. 0)THEN',
                        '     &   (ABS(YCRD) .GT. 1.E-15 .OR.\n     &    ABS(XCRD) .GT. 1.E-15))THEN')
    return text[:start] + block + text[end:]


def patch_module(text):
    if 'Type FieldMetadataType' in text:
        raise ValueError('FIELD metadata patch is already present')
    text = once(text, '      TYPE PDLABETATYPE\n',
        "      Type FieldMetadataType\n"
        "        Character(LEN=15) :: CYCRD = '            -99'\n"
        "        Character(LEN=15) :: CXCRD = '           -999'\n"
        "        Character(LEN=9)  :: CELEV = '      -99'\n"
        "      End Type FieldMetadataType\n\n      TYPE PDLABETATYPE\n")
    text = once(text, '        Type (WeathType)   WEATHER\n',
                        '        Type (WeathType)   WEATHER\n        Type (FieldMetadataType) FIELD\n')
    for name, read in [('GET_Char', True), ('PUT_Char', False)]:
        begin = text.index(f'      {"Subroutine" if read else "SUBROUTINE"} {name}(')
        end = text.index(f'      END SUBROUTINE {name}', begin)
        block = text[begin:end]
        cases = "      Case ('FIELD')\n        SELECT CASE (VarName)\n"
        for key in ('CYCRD','CXCRD','CELEV'):
            left,right = ('Value', f'SAVE_data % FIELD % {key}') if read else (f'SAVE_data % FIELD % {key}', 'Value')
            cases += f"        Case ('{key}'); {left} = {right}\n"
        cases += '        Case DEFAULT; ERR = .TRUE.\n        END SELECT\n\n'
        block = once(block, '      SELECT CASE (ModuleName)\n', '      SELECT CASE (ModuleName)\n' + cases)
        text = text[:begin] + block + text[end:]
    return text


def patch_conductivity_warning(text):
    return once(text, '             IF (SWCN(J) < 1.E-4) THEN\n               SWCN(J) = -99.\n               ERR = ERR + 1\n             ENDIF',
        '             IF (SWCN(J) < 1.E-4) THEN\n'
        '!              Preserve the declared -99 missing sentinel; flag real bad data.\n'
        '               IF (ABS(SWCN(J)+99.0) > 1.E-4) ERR = ERR + 1\n'
        '               SWCN(J) = -99.\n             ENDIF')


def main(root):
    root = Path(root)
    for relative, function in [('InputModule/ipexp.for', patch_ipfld),
        ('Utilities/ModuleDefs.for', patch_module), ('InputModule/IPSOIL_Inp.for', patch_conductivity_warning)]:
        path=root/relative
        path.write_text(function(path.read_text()))


if __name__=='__main__':main(sys.argv[1])
