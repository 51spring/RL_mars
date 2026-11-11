"""Check coverage and embedded records for the Masii protocol comparison."""
import argparse
from datetime import date, timedelta
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from mars_env.artifacts import new_run, sha256, write_json

NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
# Month precision in the conference abstract, recorded as exclusive bounds.
WINDOWS = {'1': (date(2023, 4, 1), date(2023, 9, 1)),
           '2': (date(2023, 10, 1), date(2024, 4, 1))}


def inventory_workbook(path):
    with ZipFile(path) as book:
        parts = book.namelist()
        workbook = ET.fromstring(book.read('xl/workbook.xml'))
        sheets = workbook.findall('s:sheets/s:sheet', NS)
        external = [name for name in parts if name.startswith('xl/externalLinks/')
                    and '/_rels/' not in name and name.endswith('.xml')]
        return {
            'worksheet_count': len(sheets),
            'hidden_sheets': [s.attrib['name'] for s in sheets if s.get('state', 'visible') != 'visible'],
            'comment_parts': [name for name in parts if 'comment' in name.lower() and name.endswith('.xml')],
            'external_workbook_parts': len(external),
            'external_cached_cells': sum(
                len(ET.fromstring(book.read(name)).findall('.//s:cell', NS)) for name in external),
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('field_audit', type=Path)
    audit_path = parser.parse_args().field_audit.resolve()
    audit = json.loads(audit_path.read_text(encoding='utf-8'))
    acquisition = ROOT / audit['source_acquisition']
    records = json.loads(acquisition.read_text(encoding='utf-8'))
    assert audit['doi'] == records['doi'] == '10.17632/g8fsd6dpxk.1'
    snapshot = json.loads((acquisition.parent / 'snapshot.json').read_text(encoding='utf-8'))
    assert snapshot['doi'] == records['doi']
    assert '20 meters apart' in snapshot['description'] and 'radius of 127 m' in snapshot['description']
    workbooks = {}
    for item in records['files']:
        path = acquisition.parent / item['local_file']
        assert item['acquired'] and sha256(path) == item['sha256']
        workbooks[item['filename']] = inventory_workbook(path)
    assert len(workbooks) == 6

    coverage = {}
    for season, observations in audit['season_audits'].items():
        start, stop = WINDOWS[season]
        dates = observations['visits_by_date']
        outside = [day for day in dates if not start <= date.fromisoformat(day) < stop]
        coverage[season] = {
            'abstract_window_start_month': start.isoformat()[:7],
            'abstract_window_end_month': (stop - timedelta(days=1)).isoformat()[:7],
            'first_crop_scouting_date': min(dates),
            'last_crop_scouting_date': max(dates),
            'scouting_dates': len(dates),
            'outside_abstract_month_window': sorted(outside),
            'within_plot_intervals': sum(observations['within_plot_gap_days'].values()),
        }
    assert set(coverage) == set(WINDOWS)
    assert all(not item['outside_abstract_month_window'] for item in coverage.values())
    assert sum(item['within_plot_intervals'] for item in coverage.values()) == 144

    run = new_run(ROOT, 'masii_faw_protocol_linkage')
    write_json(run / 'protocol_linkage.json', {
        'field_audit': audit_path.relative_to(ROOT).as_posix(),
        'field_audit_sha256': sha256(audit_path),
        'sources': {
            'conference': {
                'abstract_id': 'NMK_AKE89', 'printed_page': 184, 'year': 2024,
                'url': ('https://www.researchgate.net/publication/383282319_THEME_Utilization_of_'
                        'Biological_Resources_for_Sustainable_Development_Nature_Conservation_and_Climate_Resilience'),
                'location': 'Masii, Machakos County',
                'farms_by_mdt': [3, 3], 'reported_maize_cultivar': 'KDH 414-12 (Ukamess)',
                'reported_farm_area_m2': 2000, 'dispenser_spacing_m': 20, 'dispenser_radius_m': 112,
            },
            'repository': {
                'doi': records['doi'], 'dispenser_spacing_m': 20, 'dispenser_radius_m': 127,
                'reported_area_wide_coverage_ha': 5, 'related_links_in_snapshot': snapshot['related_links'],
            },
        },
        'linkage_status': 'probable_study_match_no_verified_farm_crosswalk_or_radius_resolution',
        'coverage': coverage,
        'workbook_inventory': workbooks,
        'verified_weather_matches': 0,
        'verified_application_events': 0,
        'verified_independent_same_visit_ratings': 0,
        'required_for_linkage': {
            'weather': ['farm-season mapping', 'plot coordinates or verified station identity',
                        'daily weather source, units and aggregation boundary'],
            'application': ['farm-season-plot key', 'actual local date and pre/post scouting order',
                            'agent, rate and unit', 'confirmed zero-event periods for controls'],
            'measurement_error': ['same plant/visit and score definition', 'independent repeat readers',
                                  'reference new leaf loss over the seven-day window'],
        },
        'quantitative_fit_ready': False,
        'research_ready': False,
        'main_training_allowed': False,
    })
    print(run.relative_to(ROOT).as_posix())


if __name__ == '__main__':
    main()
