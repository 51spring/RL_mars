"""Reconstruct the exact changed source files from preserved vendor inputs."""
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'docker'))
from mars_env.artifacts import new_run,write_json,sha256
import patch_ear_audit,patch_harvest_boundary,patch_sequence_audit,patch_harvest_n_inventory,patch_harvest_actual_exports


if __name__=='__main__':
    vendor=ROOT/'vendor/dssat-pdi-source';results={}
    with tempfile.TemporaryDirectory(dir=ROOT/'tmp',prefix='source_rebuild_') as temp:
        temp=Path(temp);assert temp.resolve().is_relative_to((ROOT/'tmp').resolve())
        for relative in ('Plant/CERES-Maize/MZ_GROSUB.for','CSM_Main/CSM.for'):
            target=temp/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(vendor/relative,target)
        subprocess.run([sys.executable,str(ROOT/'docker/patch_leaf_source.py'),str(temp)],check=True)
        growth=patch_ear_audit.patch_growth((temp/'Plant/CERES-Maize/MZ_GROSUB.for').read_text())
        phenology=patch_ear_audit.patch_phenology((vendor/'Plant/CERES-Maize/MZ_PHENOL.for').read_text())
        maize=patch_harvest_actual_exports.patch(patch_harvest_n_inventory.patch(patch_sequence_audit.patch_crop(
            patch_harvest_boundary.patch((vendor/'Plant/CERES-Maize/MZ_CERES.for').read_text()))))
        for relative,expected in [('Plant/CERES-Maize/MZ_GROSUB.for',growth),
            ('Plant/CERES-Maize/MZ_PHENOL.for',phenology),('Plant/CERES-Maize/MZ_CERES.for',maize)]:
            digest=hashlib.sha256(expected.encode()).hexdigest();actual=sha256(Path('/build/source')/relative)
            assert digest==actual,relative
            results[relative]={'vendor_sha256':sha256(vendor/relative),'expected_sha256':digest,'built_sha256':actual}
    run=new_run(ROOT,'actual_harvest_source')
    write_json(run/'verification.json',{'passed':True,'source_files':results,
        'scope':'exact source reconstruction only','research_ready':False})
    print(run)
