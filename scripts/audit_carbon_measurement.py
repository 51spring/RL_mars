"""Source-backed C observability and preserved Q/F soil arithmetic audit."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from mars_env.artifacts import new_run,write_json,sha256
from mars_env.carbon_audit import carbon_runs,audit_soil_carbon,verify_soil_residue_carbon,carbon_coverage

ANCHORS={
 'Plant/CERES-Maize/MZ_GROSUB.for':['Daily biomass production, g/plant/day',
    'Potential dry matter production under optimum water, nitrogen and temperature, g/plant',
    'RTWT   = RTWT  + 0.5*GRORT-0.005*RTWT','SEEDRV  = SEEDRVE',
    'CARBO = PCARB*AMIN1 (PRFT,SWFAC,NSTRES, PStres1,KSTRES)*SLPF'],
 'Soil/CERES_OrganicMatter/SoilOrg.for':['FOMCFrac = 0.4','HumusCFrac = 0.526',
    'LITC(L) = FOM(L) * FOMCFrac','newCO2(L) = newCO2_HUM(L) + newCO2_FOM(L)'],
 'Soil/SoilUtilities/SoilCBal.for':['kg[C]/ha','HarvCTot = SUM(HARVRES % ResWt) * 0.4',
    'SNCLD = SENESCE % ResWt(0) * 0.4','TotalAdd = RESC0D + RESC1D + SNCLDY + SNCSDY + THRC0D + THRC1D',
    'CumBal = CumBal + DayBal','THRC0D = 0.0'],
 'Plant/CERES-SharedFiles/HResCeres.for':['HResWt(0:NL)','Residue mass (kg[dry matter]/ha)'],
 'Soil/GHG/Methane.for':['newCO2Tot = newCO2Tot + newCO2(i)',
    'CO2Emission    = newCO2Tot - CH4Production - StorageFlux']}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('source',type=Path);args=parser.parse_args()
    source=args.source.resolve();index=json.loads((source/'verification.json').read_text())
    assert index['passed'] and index['contract_version']=='standing_stock_actual_yield_v2'
    run=new_run(ROOT,'carbon_measurement_audit');print('RUN_DIR='+str(run),flush=True)
    try:
        evidence={}
        for relative,anchors in ANCHORS.items():
            path=Path('/build/source')/relative;lines=path.read_text(encoding='latin-1').splitlines()
            hits={a:[{'line':i,'text':line.strip()} for i,line in enumerate(lines,1) if a in line] for a in anchors}
            if not all(hits.values()):raise ValueError('Source anchor missing: '+relative)
            evidence[relative]={'built_sha256':sha256(path),'anchors':hits,
                'vendor_sha256':sha256(ROOT/'vendor/dssat-pdi-source'/relative)}
        previous=ROOT/'outputs/runs/20261106T034354Z_actual_harvest_source_e7fc7428/verification.json'
        prior=json.loads(previous.read_text())
        key='Plant/CERES-Maize/MZ_GROSUB.for'
        assert evidence[key]['built_sha256']==prior['source_files'][key]['built_sha256']
        write_json(run/'source_anchors.json',evidence)
        contract=json.loads((ROOT/'configs/carbon_measurement_contract.json').read_text())
        write_json(run/'measurement_contract.json',contract)
        cases=[]
        for case in index['cases']:
            for label in ('control','candidate'):
                folder=source/case['name']/label
                d=json.loads((folder/'contract_diagnostics.json').read_text())
                for filename,digest in d['files'].items():assert sha256(folder/filename)==digest
                rows=carbon_runs((folder/'SoilCBal.OUT').read_text(encoding='latin-1'))
                result=audit_soil_carbon(rows)
                terminal=json.loads((folder/'trace.json').read_text())[-1]['yrdoy']
                result['terminal_coverage']=carbon_coverage(rows,int(terminal))
                result['residue_interface']=verify_soil_residue_carbon(rows,d)
                result['nonzero_native_plant_methane_consumption_days']=sum(
                    float(row['CH4COD'])!=0 for values in rows.values() for row in values)
                result.update(name=case['name'],label=label,
                    soil_carbon_output_sha256=sha256(folder/'SoilCBal.OUT'),
                    source_diagnostics_sha256=sha256(folder/'contract_diagnostics.json'))
                write_json(run/(case['name']+'_'+label+'.json'),result);cases.append(result)
        manifest=json.loads((source/'manifest.json').read_text())
        write_json(run/'verification.json',{'passed':True,
            'scope':'built-source unit/observability mapping and separate-run soil carbon output arithmetic, not whole elemental C closure',
            'source_native_run':str(source),'source_native_report_sha256':sha256(source/'verification.json'),
            'source_native_image_id':manifest['image_id'],'source_native_manifest_sha256':sha256(source/'manifest.json'),
            'source_native_config_sha256':sha256(source/'config.yaml'),
            'case_count':len(cases),'soil_output_days':sum(c['days'] for c in cases),'cases':cases,
            'all_terminal_output_coverage_complete':all(c['terminal_coverage']['complete'] for c in cases),
            'source_anchor_sha256':sha256(run/'source_anchors.json'),
            'prior_built_growth_source_provenance_sha256':sha256(previous),
            'measurement_contract_sha256':sha256(ROOT/'configs/carbon_measurement_contract.json'),
            'unmeasured_elemental_terms':[t['id'] for t in contract['terms'] if not t['observed']],
            'soil_native_assumed_residue_fraction':.4,'plant_or_harvest_c_fraction_inferred':False,
            'new_native_runs':0,'whole_elemental_carbon_verified':False,'research_ready':False})
        print(run,flush=True)
    except Exception as exc:
        write_json(run/'failure.json',{'passed':False,'exception':repr(exc),'source':str(source),'research_ready':False})
        raise


if __name__=='__main__':main()
