"""Preserve field marginal evidence without claiming factorial reconstruction."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.agronomic_marginals import build_marginal_targets


if __name__=='__main__':
    source=json.loads((ROOT/'configs/rahman2022_marginal_grain.json').read_text(encoding='utf-8'))
    folder=ROOT/source['source_run']
    assert sha256(folder/source['source_pdf'])==source['source_pdf_sha256']
    targets,contrasts=build_marginal_targets(ROOT)
    run=new_run(ROOT,'agronomic_marginals')
    write_json(run/'marginal_targets.json',targets)
    write_json(run/'descriptive_contrasts.json',contrasts)
    write_json(run/'verification.json',{'passed':True,
        'scope':'source transcription, moisture conversion and marginal/factorial separation only',
        'marginal_targets':len(targets),'descriptive_contrasts':len(contrasts),
        'new_factorial_scenarios':0,'quantitative_validation_ready':0,'calibration_allowed':0,
        'source_pdf_sha256':source['source_pdf_sha256'],
        'transcription_config_sha256':sha256(ROOT/'configs/rahman2022_marginal_grain.json'),
        'visually_checked_pages':{str(p):sha256(folder/f'checked-{p:02d}.png') for p in source['visually_checked_pages']},
        'new_native_runs':0,'parameters_fitted':False,'research_ready':False})
    print(run)
