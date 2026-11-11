"""Four-year worksheet depth/formula inventory and common-upper stock candidates."""
from collections import Counter
from datetime import date,timedelta
import json
from pathlib import Path
import re
import shutil
import sys
import openpyxl
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,sha256,write_json
from mars_env.water_storage import water_storage_mm


def main():
    source=ROOT/'outputs/runs/20261106T083612Z_lirf_public_sources_d90f9eab'
    original=json.loads((source/'verification.json').read_text())
    for item in original['files']:assert sha256(source/item['file'])==item['sha256']
    run=new_run(ROOT,'lirf_water_depths');print(run,flush=True)
    write_json(run/'comparison_protocol.json',dict(depths_cm=[105,135],
        quantities='T1-T6 treatment mean volumetric storage; no plot or native fit',
        deficit_diagnostic='Seasonal treatment FC stock0-105 minus water stock vs stored AD',
        deficit_tolerance_mm=.57500001,
        tolerance_basis='visible FC and SWD0.1 resolution: 105cm*0.05percentagepoint*0.1 +0.05mm + float margin; not sampling error',
        outliers_preserved=True,source_formula_evaluation=False,source_workbook_recalculation=False,
        native_comparison_allowed=False,field_initialization_allowed=False))
    sheets=[];candidates=[];formula_inventory=[];definitions=[];diagnostics=[]
    def numeric(v):return isinstance(v,(int,float)) and not isinstance(v,bool)
    expected=[(0,15),(15,45),(45,75),(75,105),(105,135),(135,165),(165,200)]
    parse=lambda text:tuple(map(int,re.fullmatch(r'(\d+)\s*-\s*(\d+)(?:\s*cm)?',text).groups()))
    for year in range(2008,2012):
        filename=f'LIRF_Maize_{year}.xlsx';path=source/filename
        w=openpyxl.load_workbook(path,read_only=True,data_only=True)
        f=openpyxl.load_workbook(path,read_only=True,data_only=False)
        definition=w['Data Descriptions']['C11'].value
        assert '135 - 175' in definition and '175 - 225' in definition
        definitions.append(dict(file=filename,cell='Data Descriptions C11',text=definition))
        seasonal=list(w['Seasonal']);fc_headers=seasonal[4]
        fc_start=next(i for i,c in enumerate(fc_headers) if c.value=='0 - 15 cm')
        assert [parse(c.value) for c in fc_headers[fc_start:fc_start+7]]==expected
        for treatment in range(1,7):
            name=f'Tmnt{treatment}';rows=list(w[name]);forms=list(f[name])
            layers=[parse(c.value) for c in rows[2][4:11]]
            assert layers==expected and all(c.value=='%' for c in rows[3][4:11])
            fcrow=seasonal[treatment+5]
            assert fcrow[fc_start-1].value==treatment
            fc=[c.value for c in fcrow[fc_start:fc_start+7]]
            fc_stock=water_storage_mm(fc,layers,105)
            counts=Counter();residuals=[]
            for row_index,(row,formula_row) in enumerate(zip(rows,forms),1):
                doy=row[0].value
                if row_index<5 or not numeric(doy) or int(doy)!=doy or not 1<=doy<=(366 if year==2008 else 365):continue
                values=[c.value for c in row[4:11]]
                for ci in (*range(4,11),29,31):
                    c=formula_row[ci]
                    if c.value not in (None,''):
                        kind='formula' if c.data_type=='f' else 'stored_value'
                        counts[kind]+=1
                        if kind=='formula':formula_inventory.append(dict(file=filename,sheet=name,cell=c.coordinate,formula=c.value))
                for depth,columns in ((105,4),(135,5)):
                    if not all(numeric(v) for v in values[:columns]):continue
                    stock=water_storage_mm(values,layers,depth)
                    candidate=dict(year=year,treatment=treatment,date=(date(year,1,1)+timedelta(days=doy-1)).isoformat(),
                        depth_cm=depth,water_storage_mm=stock,source_file=filename,source_sheet=name,
                        source_row=row_index,cells=[dict(cell=c.coordinate,percent=c.value,formula=formula_row[c.column-1].value if formula_row[c.column-1].data_type=='f' else None) for c in row[4:4+columns]],
                        population='reported mean4field replicates',observation_sd_available=False,
                        independent_plot_observation=False,native_validation_ready=False)
                    candidates.append(candidate)
                    if depth==105 and numeric(row[29].value):
                        residual=fc_stock-stock-row[29].value
                        residuals.append(dict(date=candidate['date'],source_cell=row[29].coordinate,reported_swd_mm=row[29].value,
                            reported_swd_number_format=row[29].number_format,
                            reconstructed_swd_mm=fc_stock-stock,residual_mm=residual,
                            within_visible_precision_bound=abs(residual)<=.57500001))
            sheets.append(dict(year=year,treatment=treatment,source_file=filename,sheet=name,
                header_depths_cm=layers,description_depths_cm=layers[:5]+[(135,175),(175,225)],
                conflict_below_cm=135,matching_upper_depths_cm=[105,135],
                measured_water_and_deficit_cell_kinds=dict(counts),
                seasonal_fc_header_cell=fc_headers[fc_start].coordinate,
                seasonal_fc_cells=[c.coordinate for c in fcrow[fc_start:fc_start+4]],
                seasonal_fc_number_formats=[c.number_format for c in fcrow[fc_start:fc_start+4]],seasonal_fc_percent=fc[:4]))
            diagnostics.append(dict(year=year,treatment=treatment,comparisons=len(residuals),
                maximum_absolute_residual_mm=max((abs(r['residual_mm']) for r in residuals),default=None),
                outside_visible_precision_bound=sum(not r['within_visible_precision_bound'] for r in residuals),rows=residuals))
    assert len(sheets)==24
    pages=PdfReader(source/'LIRF_Methodology_r1.pdf').pages
    method=[]
    for number in (8,9,10):
        text=pages[number-1].extract_text()
        # Preserve whole local primary-source page text as provenance, not a web quote.
        method.append(dict(physical_page=number,text=text))
    for name,data in [('worksheet_depth_inventory',sheets),('common_upper_water_candidates',candidates),
        ('measured_cell_formulas',formula_inventory),('definitions',definitions),
        ('deficit_reconstruction',diagnostics),('methodology_pages',method)]:write_json(run/f'{name}.json',data)
    report=dict(passed=True,years=4,treatment_sheets=24,header_description_conflicts=24,
        conflict_below_cm=135,common_upper_depths_cm=[105,135],
        candidates_by_depth=dict(Counter(c['depth_cm'] for c in candidates)),
        measured_cell_formula_count=len(formula_inventory),
        deficit_comparisons=sum(d['comparisons'] for d in diagnostics),
        deficit_outside_visible_precision_bound=sum(d['outside_visible_precision_bound'] for d in diagnostics),
        deep_profile_definition_resolved=False,upper_candidates_are_field_validation=False,
        native_inputs_changed=False,new_native_simulations=0,new_training_runs=0,
        research_ready=False,main_training_allowed=False,
        source_sha256={item['file']:item['sha256'] for item in original['files'] if item['file'].startswith('LIRF_Maize_') or item['file']=='LIRF_Methodology_r1.pdf'},
        scope='source depth/formula inventory and treatment-mean storage arithmetic, no native/field scoring')
    shutil.copy2(ROOT/'outputs/lirf-water-method-09.png',run/'methodology-page09.png')
    write_json(run/'verification.json',report)
    write_json(run/'derived_files_sha256.json',{p.name:sha256(p) for p in run.iterdir() if p.is_file()})
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
