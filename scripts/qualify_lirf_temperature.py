"""Qualify readback and paired sensitivity without agronomic scoring."""
import json
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.audits import weather_rows
from mars_env.dssat_backend import read_summary


def temperature_rows(text):
    headers=[line[1:].split() for line in text.splitlines() if line.startswith('@YEAR')]
    assert len(headers)==1
    rows=[dict(zip(headers[0],map(float,line.split()))) for line in text.splitlines() if re.match(r'^\s*\d{4}\s+\d{3}\s',line)]
    assert rows and all(len(line.split())==len(headers[0]) for line in text.splitlines() if re.match(r'^\s*\d{4}\s+\d{3}\s',line))
    assert [row['DAS'] for row in rows]==list(range(1,len(rows)+1))
    assert [row['DOY'] for row in rows]==list(range(1,len(rows)+1))
    return rows


def main():
    native=ROOT/'outputs/runs/20261106T140011Z_lirf_temperature_1d320bb0'
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    assert read(native/'verification.json')['passed']
    for p,h in read(native/'raw_files_sha256.json').items():assert sha256(native/p)==h
    original=ROOT/'outputs/runs/20261106T133233Z_lirf_native_inputs_574604f1'
    old_index=read(ROOT/'outputs/runs/20261106T133507Z_lirf_native_qualification_f44ee96f/raw_files_sha256.json')
    for p,h in old_index.items():assert sha256(original/p)==h
    plan=read(native/'predeclared_plan.json');assert len(plan['cases'])==5
    summaries={};temperatures={};reports=[];weather_count=0
    old_summary=read_summary((original/'aligned_weather_048/Summary.OUT').read_text())
    original_weather=(original/'aligned_weather_048/CO01.WTH').read_text().splitlines()
    for case in plan['cases']:
        name=case['name'];folder=native/name
        text=(folder/'SoilTemp.OUT').read_text()
        values={k:float(re.search(r'! '+k+r'\s*=\s*([-\d.]+)',text)[1]) for k in ('TAV','TAMP')}
        expected=(20.,5.) if case['tav'] is None else (case['tav'],case['amp'])
        assert all(abs(values[k]-v)<=.05001 for k,v in zip(('TAV','TAMP'),expected))
        temperatures[name]=temperature_rows(text)
        summaries[name]=read_summary((folder/'Summary.OUT').read_text())
        assert len(temperatures[name])==int(summaries[name]['HDAT'])%1000
        assert all(row['YEAR']==2008 for row in temperatures[name])
        weather_text=(folder/'CO01.WTH').read_text().splitlines()
        assert weather_text[:3]==original_weather[:3] and weather_text[4:]==original_weather[4:]
        assert (folder/'nu.SOL').read_bytes()==(original/'aligned_weather_048/nu.SOL').read_bytes()
        fx=(folder/'COGree01.MZX').read_text().splitlines()
        old_fx=(original/'aligned_weather_048/COGree01.MZX').read_text().splitlines()
        differences=[i for i,(a,b) in enumerate(zip(fx,old_fx)) if a!=b]
        allowed={i for i,l in enumerate(old_fx) if l.startswith('@N METHODS')}
        allowed|={i+1 for i,l in enumerate(old_fx) if l.startswith(('@N METHODS','@N OUTPUTS'))}
        assert len(fx)==len(old_fx) and set(differences)<=allowed
        assert all(len(fx[i+1])>=86 and fx[i+1][85]=='D' for i,l in enumerate(fx) if l.startswith('@N METHODS'))
        observed=weather_rows((folder/'Weather.OUT').read_text())
        daily={int(l.split()[0]):list(map(float,l.split()[1:5])) for l in weather_text if re.match(r'^\d{7}\s',l)}
        for day,row in observed.items():
            for key,value in zip(('SRAD','TMXD','TMND','PRED'),daily[day]):
                assert abs(row[key]-value)<=.05001;weather_count+=1
        assert len(observed)==len(temperatures[name])
        reports.append(dict(name=name,printed_temperature_parameters=values,days=len(observed),
            summary=summaries[name],field_performance_score_computed=False))
    assert summaries['missing_defaults']==summaries['explicit_defaults']==old_summary
    assert temperatures['missing_defaults']==temperatures['explicit_defaults']
    # Check daily numeric water/plant trajectories too, independently of timestamp headers.
    def numeric_rows(path):return [l.split() for l in path.read_text().splitlines() if re.match(r'^\s*\d{4}\s+\d{3}\s',l)]
    for filename in ('PlantGro.OUT','SoilWat.OUT','SoilNi.OUT'):
        assert numeric_rows(native/'missing_defaults'/filename)==numeric_rows(native/'explicit_defaults'/filename)==numeric_rows(original/'aligned_weather_048'/filename)
    contrasts=[]
    for a,b in [('explicit_defaults','period_mean_only'),('period_mean_only','period_full_range'),('period_mean_only','period_half_range'),('period_full_range','period_half_range')]:
        left={r['DOY']:r for r in temperatures[a]};right={r['DOY']:r for r in temperatures[b]};days=sorted(left.keys()&right.keys())
        by_layer={k:max(abs(left[d][k]-right[d][k]) for d in days) for k in left[days[0]] if k.startswith('TS')}
        assert max(by_layer.values())>0
        contrasts.append(dict(left=a,right=b,common_days=len(days),max_absolute_printed_delta_c=by_layer,
            tolerance_source='SoilTemp.OUT F8.1; descriptive differences, no fitted acceptance threshold'))
    anchors={
        'Weather/IPWTH_alt.for':["CASE('AMP')","READ(LINE(C1:C2),*,IOSTAT=ERR) TAMP","TAMP = 5.0"],
        'Weather/WGEN.for':["XLAT, XLONG, ELEV, TAV, TAMP"],
        'Weather/weathr.for':['WEATHER % TAMP   = TAMP','TA = TAV - SIGN(1.0,XLAT) * TAMP'],
        'SPAM/SPAM.for':["CASE ('E')",'CALL STEMP(CONTROL, ISWITCH,'],
        'InputModule/IPSIM.for':["METMP   = 'D'","IF (INDEX('ED',METMP) < 1) METMP = 'D'"],
        'SPAM/STEMP.for':['TA = TAV + TAMP * COS(ALX) / 2.0','ST(L) = TAV + (TAMP / 2.0 * COS(ALX + ZD) + DT) * EXP(ZD)'],
        'SPAM/OPSTEMP.for':["TAV,TAMP"],
        'Utilities/READS.for':['COL(COUNT,1) = I + 1'],
        'CMakeLists.txt':['Weather/IPWTH_alt.for']}
    source_audit=[]
    for path,needles in anchors.items():
        p=ROOT/'vendor/dssat-pdi-source'/path;lines=p.read_text(encoding='latin-1').splitlines()
        hits=[]
        for needle in needles:
            matches=[dict(line=i+1,text=l) for i,l in enumerate(lines) if needle in l]
            assert matches,(path,needle);hits+=matches
        source_audit.append(dict(path=str(p.relative_to(ROOT)),sha256=sha256(p),hits=hits))
    run=new_run(ROOT,'lirf_temperature_qualification')
    write_json(run/'source_path_audit.json',source_audit)
    write_json(run/'sensitivity_diagnostics.json',dict(cases=reports,contrasts=contrasts))
    write_json(run/'verification.json',dict(passed=True,source_run=str(native.relative_to(ROOT)),
        native_report_sha256=sha256(native/'verification.json'),raw_files_sha256=sha256(native/'raw_files_sha256.json'),
        plan_sha256=sha256(native/'predeclared_plan.json'),native_cases=5,
        wth_parameter_readbacks=10,weather_field_comparisons=weather_count,weather_mismatches=0,
        baseline_exact_numeric_regression=True,baseline_matches_previous_native=True,
        wth_to_tamp_scale_factor=1,default_stemp_seasonal_term_multiplier=.5,
        wgen_climate_parser_scale_factor=1,wgen_runtime_exercised=False,
        historical_manual_semantic_discrepancy_resolved=False,
        source_files=len(source_audit),native_field_parameters_selected=False,
        research_ready=False,main_training_allowed=False,
        scope='WTH to default STEMP readback and diagnostic sensitivity, not field temperature validation'))
    print(run);print(json.dumps(dict(weather_comparisons=weather_count,cases=reports,contrasts=contrasts),indent=2))


if __name__=='__main__':main()
