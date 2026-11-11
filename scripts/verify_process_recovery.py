"""Real worker death must invalidate an episode without committing its action."""
import json
import os
from pathlib import Path
import signal
import sys
import time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json
from mars_env.process_backend import LegacyProcessBackend
from mars_env.environment import CropManagementEnv
from benchmark_real_ppo import process_tree


def main():
    run=new_run(ROOT,'process_recovery');os.environ['MARS_RUN_DIR']=str(run)
    records=[]
    for forced in (False,True):
        backend=LegacyProcessBackend()
        env=CropManagementEnv(pest_enabled=False,backend_factory=lambda **kwargs:backend)
        baseline=process_tree()[0]
        try:
            env.reset(seed=123456)
            owned=process_tree()[0]-baseline
            assert owned
            ledger=env.ledger
            if forced:
                # This is the freshly started private DSSAT group owned by this test.
                group=os.getpgid(backend.process.pid)
                assert group==backend.process.pid and group!=os.getpgrp()
                os.killpg(group,signal.SIGKILL)
                try:env.step([2,0,0])
                except Exception:pass
                else:raise AssertionError('Dead backend accepted an action')
                assert env.broken and env.ledger is ledger and env.ledger.water_used==0
            else:env.step([0,0,0])
        finally:env.close()
        deadline=time.monotonic()+5
        def alive(pid):
            try:return Path(f'/proc/{pid}/stat').read_text().split(') ',1)[1].split()[0]!='Z'
            except FileNotFoundError:return False
        while any(alive(pid) for pid in owned) and time.monotonic()<deadline:time.sleep(.05)
        assert not any(alive(pid) for pid in owned)
        records.append({'forced_worker_death':forced,'owned_processes':len(owned),'live_processes_after_close':0,
                        'ledger_unchanged_on_failure':True if forced else None})
    write_json(run/'verification.json',{'passed':True,'cases':records,'research_ready':False})
    print(run);print(json.dumps(records))


if __name__=='__main__':main()
