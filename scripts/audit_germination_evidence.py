"""Qualify saved native failure outputs and distinguish warning prose from timing."""
import argparse
import json
from pathlib import Path
import re
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.dssat_backend import read_summary


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--native-run',type=Path,default=ROOT/'outputs/runs/20261106T082253Z_germination_failure_035e575a')
    parser.add_argument('--capture-dir',type=Path)
    args=parser.parse_args()
    source=args.native_run.resolve()
    run=new_run(ROOT,'germination_evidence')
    report=json.loads((source/'verification.json').read_text())
    assert report['passed'] and report['native_runs']==4
    index=json.loads((source/'source_files.json').read_text())
    assert all(sha256(source/p)==h for p,h in index.items())
    captures={}
    capture_root=args.capture_dir or source
    for name in ('species_capture.SPE','phenol_capture.for'):
        p=capture_root/name
        target=run/name
        shutil.copy2(p,target)
        captures[name]=sha256(target)
    species=(run/'species_capture.SPE').read_text(encoding='latin-1')
    phenol=(run/'phenol_capture.for').read_text(encoding='latin-1')
    assert float(re.search(r'^\s*DSGT\s+([\d.]+)',species,re.M)[1])==21
    assert 'IF (NDAS .GE. DSGT)' in phenol and 'within 15 days of sowing' in phenol
    original=(source/'original_UFGA8201.WTH').read_text().splitlines()
    dry=(source/'dry_UFGA8201.WTH').read_text().splitlines()
    assert len(original)==len(dry)
    for a,b in zip(original,dry):
        if re.match(r'^\d{5}\s',a):
            a,b=a.split(),b.split()
            assert a[:4]==b[:4] and a[5:]==b[5:] and float(b[4])==0
        else: assert a==b
    for c in report['cases']:
        folder=source/c['name']
        trace=json.loads((folder/'trace.json').read_text())
        actions=json.loads((folder/'actions.json').read_text())
        summary=read_summary((folder/'Summary.OUT').read_text())
        assert summary['HWAH']==c['episode_result']['harvested_grain_kg_ha']==0
        assert not json.loads((folder/'cleanup.json').read_text())['alive_after_close']
        assert sum(a['reward'] for a in actions)==c['sum_raw_rewards']
        assert all(float(s['rain'])==0 for s in trace)
        lines=(folder/'fileX.MZX').read_text().splitlines()
        header=next(i for i,s in enumerate(lines) if s.startswith('@P PDATE'))
        assert lines[header+1].split()[lines[header].split().index('PLDP')]=='7'
        if not c['rescue']:
            assert c['terminal_date']==1982078 and c['steps']==22
            assert len([s for s in trace if s['istage']==8])==21
            assert trace[-1]['istage']==6 and trace[-1]['yrdoy']==trace[-2]['yrdoy']
            assert c['sum_raw_rewards']==-12.9
        else:
            assert c['first_emerged_date']==1982069
            # Slowed grain filling warning is dated150; final MDAT/HDAT are152.
            assert summary['MDAT']==1982152 and summary['HDAT']==1982152
    for rescue in (False,True):
        a,b=[source/c['name'] for c in report['cases'] if c['rescue']==rescue]
        assert json.loads((a/'trace.json').read_text())==json.loads((b/'trace.json').read_text())
    write_json(run/'verification.json',dict(passed=True,native_evidence=source.relative_to(ROOT).as_posix(),
        native_report_sha256=sha256(source/'verification.json'),raw_source_index_sha256=sha256(source/'source_files.json'),
        raw_files_verified=len(index),captured_image_sources=captures,native_runs=4,
        recorded_control_candidate_states_equal=True,dsGT_days=21,
        warning_literal_days=15,warning_literal_is_timing_evidence=False,
        terminal_callback_same_date_as_last_daily_state=True,software_changes_to_classifier=False,
        irrigation_control='emergence only, zero-grain maturity/harvest; not validated yield recovery',
        initial_water='native warning clamps sub-LL input to LL in most layers; effective states retained',
        independent_agronomic_validation=False,research_ready=False,main_training_allowed=False))
    print(run)


if __name__=='__main__':main()
