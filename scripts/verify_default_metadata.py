"""Corrected image defaults must actually reach Summary.OUT in both backends."""
import json
from pathlib import Path
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.dssat_backend import DssatBackend
from mars_env.leaf_diagnostics import LeafDiagnosticBackend
from mars_env.input_metadata import summary_metadata


def main():
    run=new_run(ROOT,'default_metadata_profile');results={};trajectories=[]
    for cls in (DssatBackend,LeafDiagnosticBackend):
        folder=run/cls.__name__;folder.mkdir();backend=cls()
        backend._runtime_log_path=str(folder/'runtime.log');trace=[]
        try:
            assert backend.canonical_metadata and backend.run_dssat_location=='/opt/mars/run_metadata'
            state=backend.reset(123456)
            for _ in range(400):
                trace.append([float(state[k]) for k in ('yrdoy','dap','vstage','xlai','topwt','grnwt','rain','tmax','srad')])
                date,dap=int(state['yrdoy']),int(state['dap'])
                water=10 if date>=backend.planting_yrdoy and dap in (10,20,30,40,50,60,70,80) else 0
                nitrogen={40:27,45:35,80:54}.get(dap,0) if date>=backend.planting_yrdoy else 0
                state,done,outcome=backend.step(water,nitrogen)
                if done:break
            assert done and outcome.reason=='harvest'
            native=backend._env;tmp=Path(native._tmp_folder);native.close(_close_tmp=False)
            for name in ('Summary.OUT','WARNING.OUT','fileX.MZX'):
                shutil.copy2(tmp/name,folder/name)
            native._close_tmp_folder()
            metadata=summary_metadata((folder/'Summary.OUT').read_text())
            assert metadata=={'XLAT':29.638,'LONG':-82.3689,'ELEV':40.}
            warnings=(folder/'WARNING.OUT').read_text().lower()
            assert 'error transferring variable' not in warnings and 'error reading latitude' not in warnings
            assert 'saturated hydraulic conductivity equal to zero' not in warnings
            results[cls.__name__]={'metadata':metadata,'yield_kg_ha':outcome.harvested_grain_kg_ha,
                'native_executable':backend.run_dssat_location,'summary_sha256':sha256(folder/'Summary.OUT')}
            trajectories.append(trace)
        finally:backend.close()
    assert trajectories[0]==trajectories[1]
    write_json(run/'verification.json',{'passed':True,'corrected_image_defaults_verified':True,'cases':results,
        'control_and_zero_damage_crop_trajectory_exact':True,'research_ready':False})
    print(run);print(json.dumps(results))


if __name__=='__main__':main()
