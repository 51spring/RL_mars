"""Compile the native conductivity branch with missing, zero and invalid inputs."""
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'docker'))
from mars_env.artifacts import new_run,write_json
from patch_metadata_source import patch_conductivity_warning


def branch(text):
    begin=text.index('             IF (SWCN(J) < 1.E-4) THEN')
    end=text.index('             ENDIF',begin)+len('             ENDIF')
    return text[begin:end]


def main():
    run=new_run(ROOT,'conductivity_native_branch')
    original=(ROOT/'vendor/dssat-pdi-source/InputModule/IPSOIL_Inp.for').read_text()
    results={}
    for name,source in [('original',original),('fixed',patch_conductivity_warning(original))]:
        program=run/f'{name}.for'
        program.write_text('      PROGRAM CHECK_SWCN\n      REAL SWCN(5)\n      INTEGER J, ERR\n'
            '      SWCN = (/-99.0, 0.0, 1.E-6, 0.5, -1.0/)\n      ERR=0\n      DO J=1,5\n'+branch(source)+
            '\n      ENDDO\n      WRITE(*,*) ERR,SWCN\n      END PROGRAM\n')
        binary=run/name
        subprocess.run(['gfortran','-ffixed-form','-o',str(binary),str(program)],check=True,capture_output=True,text=True)
        output=subprocess.check_output([str(binary)],text=True);values=output.split()
        results[name]={'warning_count':int(values[0]),'normalized_values':list(map(float,values[1:])),'stdout':output}
    assert results['original']['normalized_values']==results['fixed']['normalized_values']==[-99.,-99.,-99.,.5,-99.]
    assert results['original']['warning_count']==4 and results['fixed']['warning_count']==3
    write_json(run/'verification.json',{'passed':True,'cases':results,'scope':'native input normalization branch only',
        'missing_sentinel_no_longer_misreported_as_zero':True,'zero_near_zero_negative_still_flagged':True,
        'soil_property_values_unchanged':True,'research_ready':False})
    print(run);print(results)


if __name__=='__main__':main()
