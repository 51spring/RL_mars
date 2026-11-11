"""Independently verify original water/FC cells and preserve unresolved differences."""
from collections import Counter
from datetime import date,timedelta
from decimal import Decimal
import json
from pathlib import Path
import sys
import openpyxl
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256


def main():
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    folder=ROOT/'outputs/runs/20261106T142102Z_lirf_water_depths_5a3fa17b'
    source=ROOT/'outputs/runs/20261106T083612Z_lirf_public_sources_d90f9eab'
    tests=ROOT/'outputs/runs/20261106T142159Z_unit_regressions_b66a7d50/verification.json'
    ready=ROOT/'outputs/runs/20261106T142224Z_readiness_b3e1358b/readiness.json'
    for name,digest in read(folder/'derived_files_sha256.json').items():assert sha256(folder/name)==digest
    for name,digest in read(folder/'verification.json')['source_sha256'].items():assert sha256(source/name)==digest
    books={};cells={}
    for year in range(2008,2012):
        w=openpyxl.load_workbook(source/f'LIRF_Maize_{year}.xlsx',read_only=True,data_only=True);books[year]=w
        for sheet in [*(f'Tmnt{i}' for i in range(1,7)),'Seasonal']:
            cells[(year,sheet)]={c.coordinate:c.value for row in w[sheet] for c in row if c.value is not None}
        assert '175 - 225' in w['Data Descriptions']['C11'].value
    candidates=read(folder/'common_upper_water_candidates.json');keys=set();source_values=0
    for candidate in candidates:
        y,t= candidate['year'],candidate['treatment'];values=cells[(y,f'Tmnt{t}')]
        key=(y,t,candidate['date'],candidate['depth_cm']);assert key not in keys;keys.add(key)
        assert date(y,1,1)+timedelta(days=int(values[f"A{candidate['source_row']}"])-1)==date.fromisoformat(candidate['date'])
        contributions=[]
        for i,observation in enumerate(candidate['cells']):
            value=values[observation['cell']];assert value==observation['percent'];source_values+=1
            contributions.append(Decimal(str(value))*Decimal('0.1')*(15 if i==0 else 30))
            assert observation['formula'] is None
        assert abs(float(sum(contributions))-candidate['water_storage_mm'])<1e-10
        assert len(candidate['cells'])==({105:4,135:5}[candidate['depth_cm']])
        assert candidate['native_validation_ready'] is False and candidate['independent_plot_observation'] is False
    assert Counter(c['depth_cm'] for c in candidates)=={105:633,135:633}
    inventory=read(folder/'worksheet_depth_inventory.json');assert len(inventory)==24
    for entry in inventory:
        source_cells=cells[(entry['year'],entry['sheet'])]
        assert source_cells['J3']=='135 - 165' and source_cells['K3']=='165 - 200'
        fc_cells=cells[(entry['year'],'Seasonal')]
        assert [fc_cells[c] for c in entry['seasonal_fc_cells']]==entry['seasonal_fc_percent']
        assert all(f=='0.0' for f in entry['seasonal_fc_number_formats'])
        assert not entry['measured_water_and_deficit_cell_kinds'].get('formula',0)
    audit=read(folder/'deficit_reconstruction.json');outliers=[];comparisons=0
    for entry in audit:
        for row in entry['rows']:
            comparisons+=1
            assert cells[(entry['year'],f"Tmnt{entry['treatment']}")][row['source_cell']]==row['reported_swd_mm']
            assert abs(row['reconstructed_swd_mm']-row['reported_swd_mm']-row['residual_mm'])<1e-12
            if not row['within_visible_precision_bound']:outliers.append((entry['year'],entry['treatment'],row['date'],row['source_cell']))
    assert comparisons==599 and outliers==[(2010,2,'2010-07-01','AD57'),(2010,3,'2010-07-01','AD57')]
    t=read(tests);r=read(ready)
    assert t['passed'] and t['tests_run']==196 and not(t['failures'] or t['errors'] or t['skipped'])
    assert r['research_ready'] is False and r['main_training_allowed'] is False and not r['quantitative_fit_ready_studies']
    files=[folder/'verification.json',folder/'derived_files_sha256.json',tests,ready,
        ROOT/'src/mars_env/water_storage.py',ROOT/'tests/test_water_storage.py',
        ROOT/'scripts/audit_lirf_water_depths.py',Path(__file__),ROOT/'configs/lirf_translation_contract.json',
        ROOT/'configs/agronomic_sources.json',ROOT/'docs/LIRF_WATER_DEPTH_AUDIT.md',ROOT/'docs/NEXT_STEPS.md',ROOT/'PROGRESS.md']
    run=new_run(ROOT,'lirf_water_depths_release')
    write_json(run/'verification.json',dict(passed=True,source_water_value_references_verified=source_values,
        treatment_date_depth_candidates=1266,unique_treatment_dates=633,tests_run=196,
        source_sha256_unchanged=True,depth_conflicts_preserved=24,unresolved_deficit_differences=2,
        old_workspace_empty=True,new_native_simulations=0,new_training_runs=0,
        research_ready=False,main_training_allowed=False,quantitative_fit_ready_studies=0,
        evidence_sha256={str(p.relative_to(ROOT)):sha256(p) for p in files},
        scope='source inventory and common-upper storage arithmetic; no field-model validation'))
    print(run)


if __name__=='__main__':main()
