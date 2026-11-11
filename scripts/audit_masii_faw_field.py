"""Audit paired pest observations in the two public Masii trial workbooks."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime
import json
from pathlib import Path
import sys

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from mars_env.artifacts import new_run, sha256, write_json


def records(sheet):
    rows = iter(sheet.values)
    header = [value.strip() if isinstance(value, str) else None for value in next(rows)]
    return header, [dict(zip(header, row, strict=True)) for row in rows if any(v is not None for v in row)]


def visit_key(row, sampling):
    assert isinstance(row['Date'], datetime)
    return (row['Date'].date(), row[sampling], row['Farm No'], row['Plot No'])


def audit_crop(book, season):
    crop_name = {1: 'Crop & pest', 2: 'Crop & pest data'}[season]
    crop_columns, crop = records(book[crop_name])
    incidence_columns, incidence = records(book['Incidence (%)'])
    score = {1: 'FAW damage', 2: 'FAW damage score'}[season]
    visits = Counter(visit_key(row, 'Sampling') for row in crop)
    plants = Counter((*visit_key(row, 'Sampling'), row['Plant No']) for row in crop)
    incidence_visits = Counter(visit_key(row, 'Sampling' if season == 1 else 'Sampling No')
                               for row in incidence)
    labels_by_plot = defaultdict(Counter)
    dates_by_plot = defaultdict(set)
    for row in crop:
        plot = row['Farm No'], row['Plot No']
        labels_by_plot[plot][row['Main plot'], row['Sub plot']] += 1
        dates_by_plot[plot].add(row['Date'].date())
    observed_treatment = Counter((row['Main plot'], row['Sub plot']) for row in crop)
    dates = sorted({v[0] for v in visits})
    plot_gaps = Counter()
    for plot_dates in dates_by_plot.values():
        ordered = sorted(plot_dates)
        plot_gaps.update((b - a).days for a, b in zip(ordered, ordered[1:]))
    damage = Counter(row[score] for row in crop)
    larvae = Counter(row['Live FAW larvae'] for row in crop)
    missing_larvae = {repr(v): n for v, n in larvae.items() if type(v) is not int}
    assert all(type(v) is int and v >= 0 for v in damage)
    return {
        'plant_sheet': crop_name,
        'plant_columns': crop_columns,
        'incidence_columns': incidence_columns,
        'visits_by_date': {date.isoformat(): sum(v[0] == date for v in visits) for date in dates},
        'days_between_consecutive_dates': [(b - a).days for a, b in zip(dates, dates[1:])],
        'farms': len({key[0] for key in labels_by_plot}),
        'plots': len(labels_by_plot),
        'within_plot_gap_days': dict(sorted(plot_gaps.items())),
        'plot_label_conflicts': [
            {'farm': farm, 'plot': plot,
             'labels': [{'main': main, 'sub': sub, 'n': n}
                        for (main, sub), n in sorted(labels.items())]}
            for (farm, plot), labels in labels_by_plot.items() if len(labels) > 1
        ],
        'plant_rows_by_treatment': [{'main': main, 'sub': sub, 'n': n}
                                    for (main, sub), n in sorted(observed_treatment.items())],
        'plant_rows': len(crop),
        'paired_numeric_rows': sum(type(row[score]) is int and type(row['Live FAW larvae']) is int
                                   for row in crop),
        'plot_visits': len(visits),
        'sample_size_distribution_per_visit': dict(Counter(visits.values())),
        'duplicate_visit_plant_keys': sum(n - 1 for n in plants.values()),
        'ordinal_damage_counts': dict(sorted(damage.items())),
        'live_larvae_counts': {v: n for v, n in larvae.items() if type(v) is int},
        'nonnumeric_live_larvae': missing_larvae,
        'incidence_rows': len(incidence),
        'matched_incidence_keys': len(visits.keys() & incidence_visits.keys()),
        'crop_only_visit_keys': [list(map(str, key)) for key in sorted(visits.keys() - incidence_visits.keys())],
        'incidence_only_visit_keys': [list(map(str, key)) for key in sorted(incidence_visits.keys() - visits.keys())],
        'duplicate_incidence_keys': [
            {'visit_key': list(map(str, key)), 'rows': n}
            for key, n in sorted(incidence_visits.items()) if n > 1
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('acquisition', type=Path)
    source = parser.parse_args().acquisition.resolve()
    provenance = json.loads((source / 'verification.json').read_text(encoding='utf-8'))
    assert provenance['doi'] == '10.17632/g8fsd6dpxk.1'
    inventory = {}
    seasons = {}
    for item in provenance['files']:
        path = source / item['local_file']
        assert item['acquired'] and sha256(path) == item['sha256']
        book = load_workbook(path, read_only=True, data_only=True)
        try:
            inventory[item['filename']] = {
                sheet.title: [v.strip() for v in next(sheet.values) if isinstance(v, str)]
                for sheet in book
            }
            if 'crop & pest' in item['filename']:
                season = 1 if 'season one' in item['filename'] else 2
                assert season not in seasons
                seasons[season] = audit_crop(book, season)
        finally:
            book.close()
    assert set(seasons) == {1, 2}
    run = new_run(ROOT, 'masii_faw_field_audit')
    write_json(run / 'field_audit.json', {
        'source_acquisition': (source / 'verification.json').relative_to(ROOT).as_posix(),
        'doi': provenance['doi'],
        'inventory': inventory,
        'season_audits': seasons,
        'scope': 'Workbook headers and recorded plant and visit keys. Plant tags across visits and observer replicates unverified.',
        'quantitative_fit_ready': False,
        'research_ready': False,
        'main_training_allowed': False,
    })
    print(run.relative_to(ROOT).as_posix())


if __name__ == '__main__':
    main()
