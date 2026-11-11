"""Compare Varella supplemental cohort counts with published life-table rates."""
import argparse
from decimal import Decimal
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from mars_env.artifacts import new_run, sha256, write_json

SEASON = re.compile(r'20\d\d/[12](?:st|nd)')
EGG_CAUSES = ('predation', 'dislodgement', 'desiccation', 'unknown', 'parasitism', 'inviability')
LARVA_CAUSES = ('other', 'parasitism')


def cohort_rows(rows):
    release = None
    for label, *values in rows:
        if not isinstance(label, str):
            continue
        if label.startswith(('With ', 'Without ')):
            release = label.startswith('With ')
        if SEASON.fullmatch(label):
            yield (label, release), values


def workbook_rows(path):
    with path.open('rb') as source:
        workbook = load_workbook(source, read_only=True, data_only=True)
        try:
            return list(workbook['Plan1'].values)
        finally:
            workbook.close()


def article_rows(article, table_number):
    table = article.find(f'.//table-wrap[@id="pone.0130437.t{table_number:03d}"]')
    return [[' '.join(''.join(cell.itertext()).split()) for cell in row]
            for row in table.findall('.//tr')]


def compatible(count, initial, reported):
    rate = Decimal(count) / initial
    if reported.startswith('<'):
        return rate < Decimal(reported[1:].strip())
    displayed = Decimal(reported)
    tolerance = Decimal('0.0005')  # Table precision, including displayed integer zeros.
    return abs(rate - displayed) <= tolerance


def compare(workbook, reported, causes):
    result = []
    for (season, release), values in cohort_rows(workbook):
        initial, *raw_counts = values[:1 + len(causes)]
        assert all(type(v) is int and v >= 0 for v in (initial, *raw_counts))
        total = sum(raw_counts)
        assert 0 <= total <= initial and initial > 0
        counts = {'total': total, **dict(zip(causes, raw_counts, strict=True))}
        rates = reported[season, release]
        assert set(rates) == set(counts)
        checks = {key: {'count': count, 'count_over_initial': count / initial,
                        'reported_rate': rates[key], 'compatible': compatible(count, initial, rates[key])}
                  for key, count in counts.items()}
        result.append({'season': season, 'parasitoid_release': release, 'initial': initial,
                       'unassigned_count_remainder': initial - total,
                       'unassigned_fraction': (initial - total) / initial,
                       'checks': checks})
    assert len({(r['season'], r['parasitoid_release']) for r in result}) == len(result) == len(reported)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    source = parser.parse_args().source.resolve()
    metadata = json.loads((source / 'sources.json').read_text(encoding='utf-8'))
    assert set(metadata) == {'article.xml', 'S1.xlsx', 'S2.xlsx'}
    assert all(sha256(source / name) == item['sha256'] for name, item in metadata.items())
    article = ET.parse(source / 'article.xml')
    egg_rates = {}
    for key, values in cohort_rows(article_rows(article, 2)):
        total, _, predation, parasitism, dislodgement, inviability, desiccation, unknown = values
        egg_rates[key] = dict(total=total, predation=predation, parasitism=parasitism,
                              dislodgement=dislodgement, inviability=inviability,
                              desiccation=desiccation, unknown=unknown)
    larva_rates = {key: dict(total=values[0], other=values[2], parasitism=values[4])
                   for key, values in cohort_rows(article_rows(article, 4))}
    eggs = compare(workbook_rows(source / 'S1.xlsx'), egg_rates, EGG_CAUSES)
    larvae = compare(workbook_rows(source / 'S2.xlsx'), larva_rates, LARVA_CAUSES)
    assert len(eggs) == 10 and len(larvae) == 6

    weather = {row[0]: {'characteristic': row[1], 'mean_air_temperature_c': float(row[2]),
                        'mean_daily_precipitation_mm': float(row[6])}
               for row in article_rows(article, 1) if SEASON.fullmatch(row[0])}
    assert set(weather) == {r['season'] for r in larvae}
    run = new_run(ROOT, 'varella_stage_survival_audit')
    write_json(run / 'stage_survival.json', {
        'doi': '10.1371/journal.pone.0130437',
        'source_archive': source.relative_to(ROOT).as_posix(),
        'sources': metadata,
        'weather_season_summaries': weather,
        'egg_cohorts': eggs,
        'larval_cohorts': larvae,
        'count_comparison_scope': 'Supplement count divided by initial count versus article table; no reconciliation assumed.',
        'unassigned_remainder_scope': 'Arithmetic remainder after listed causes; not independently verified survivors.',
        'verified_daily_weather_joins': 0,
        'separately_observed_larval_dispersal_or_nondetection_counts': None,
        'quantitative_fit_ready': False,
        'research_ready': False,
        'main_training_allowed': False,
    })
    print(run.relative_to(ROOT).as_posix())
    for name, cohorts in [('eggs', eggs), ('larvae', larvae)]:
        failures = [(r['season'], r['parasitoid_release'], key) for r in cohorts
                    for key, cell in r['checks'].items() if not cell['compatible']]
        print(name, len(failures), failures)
        print('initial total and remainder range:', sum(r['initial'] for r in cohorts),
              min(r['unassigned_fraction'] for r in cohorts), max(r['unassigned_fraction'] for r in cohorts))


if __name__ == '__main__':
    main()
