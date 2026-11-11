import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from mars_env.integrated_n import analyze_integrated_n,run_tables
ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/'tests/fixtures/integrated_n'


class IntegratedNTests(unittest.TestCase):
    def data(self):
        return (json.loads((FIXTURE/'diagnostics.json').read_text()),json.loads((FIXTURE/'trace.json').read_text()))

    def test_native_daily_inventory_and_scheduler_liabilities(self):
        d,t=self.data();r=analyze_integrated_n(FIXTURE,d,t)
        self.assertTrue(r['daily_inventory_passed']);self.assertEqual(r['observations'],367)
        self.assertEqual(r['source_flux_lag_checks'],365)
        self.assertGreater(max(abs(v['unadjusted_scheduler_residual_kg_ha']) for v in r['rows']),20)
        self.assertLess(r['max_abs_residual_kg_ha'],.02)
        self.assertFalse(r['research_ready']);self.assertFalse(r['residual_offsets_fitted'])

    def test_stale_native_rate_does_not_replace_cumulative_uptake_difference(self):
        d,t=self.data();original=analyze_integrated_n(FIXTURE,d,t)
        for row in t:row['mars_plant_audit']['trnu']=99999.
        self.assertEqual(analyze_integrated_n(FIXTURE,d,t)['final_residual_kg_ha'],original['final_residual_kg_ha'])

    def test_missing_grain_or_byproduct_export_is_detected(self):
        for field in ('grain','byproduct'):
            d,t=self.data()
            if field=='grain':d['harvests'][0]['harvest_grain_n']=0.
            else:d['v2_contract']['byproduct_n_kg_ha']=0.
            self.assertFalse(analyze_integrated_n(FIXTURE,d,t)['daily_inventory_passed'])

    def test_fertilizer_event_and_daily_transfer_corruption_refused(self):
        d,t=self.data()
        with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as temp:
            folder=Path(temp);self.assertTrue(folder.resolve().is_relative_to((ROOT/'tmp').resolve()))
            for p in FIXTURE.glob('*.OUT'):shutil.copy2(p,folder/p.name)
            event=folder/'MgmtEvent.OUT';text=event.read_text();self.assertIn('27.',text)
            event.write_text(text.replace('27. kg[N]/ha','28. kg[N]/ha'))
            with self.assertRaises(ValueError):analyze_integrated_n(folder,d,t)
            event.write_text(text)
            p=folder/'SoilNiBal.OUT';lines=p.read_text().splitlines()
            header=next(l[1:].split() for l in lines if l.startswith('@YEAR'))
            i=next(i for i,l in enumerate(lines) if l.split()[:2]==['1982','030'])
            values=lines[i].split();values[header.index('RNUP')]='1.0000';lines[i]=' '+' '.join(values)
            p.write_text('\n'.join(lines))
            with self.assertRaises(ValueError):analyze_integrated_n(folder,d,t)

    def test_run_parser_preserves_initial_boundary_and_refuses_duplicate_day(self):
        text=(FIXTURE/'SoilNoBal.OUT').read_text();tables=run_tables(text)
        self.assertEqual(tables[1][-1]['DOY'],tables[2][0]['DOY'])
        lines=text.splitlines();i=next(i for i,l in enumerate(lines) if l.split()[:2]==['1982','030'])
        lines.insert(i,lines[i])
        with self.assertRaises(ValueError):run_tables('\n'.join(lines))
        d,t=self.data();del t[5]
        with self.assertRaises(ValueError):analyze_integrated_n(FIXTURE,d,t)

    def test_print_precision_cannot_override_a_failed_native_boundary(self):
        folder=ROOT/'tests/fixtures/integrated_n_control'
        d=json.loads((folder/'diagnostics.json').read_text());t=json.loads((folder/'trace.json').read_text())
        r=analyze_integrated_n(folder,d,t)
        self.assertTrue(r['daily_inventory_passed'])
        self.assertFalse(r['native_harvest_contract_passed'])
        self.assertFalse(r['combined_model_n_evidence_passed'])


if __name__=='__main__':unittest.main()
