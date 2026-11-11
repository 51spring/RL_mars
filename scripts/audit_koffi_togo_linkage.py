"""Check published Koffi station Pearson statistics for rounding compatibility."""
import json
import math
from pathlib import Path
import sys

from scipy.stats import t

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from mars_env.artifacts import new_run, sha256, write_json

# Tables 2 and 3, in the published row order.
PAIRS = ('adult_egg', 'adult_larva', 'adult_infestation',
         'egg_larva', 'egg_infestation', 'larva_infestation')
TABLES = {
    'Lome': [
        (4, PAIRS, [(0.85, .147), (-.85, .147), (.85, .182), (-.50, .500), (-.43, .570), (.85, .147)]),
        (16, PAIRS, [(.12, .659), (.97, .266), (-.63, .009), (.41, .120), (.14, .614), (.21, .438)]),
        (8, PAIRS[1:3], [(-.43, .292), (.83, .011)]),
        (20, (*PAIRS[1:3], PAIRS[-1]), [(.14, .545), (-.07, .759), (-.09, .716)]),
    ],
    'Toaga': [
        (4, PAIRS, [(.75, .255), (.89, .106), (.73, .270), (-.67, .333), (-.27, .730), (-.41, .590)]),
        (16, (*PAIRS[1:3], PAIRS[-1]), [(.41, .120), (-.08, .762), (.02, .928)]),
        (8, (*PAIRS[1:3], PAIRS[-1]), [(-.17, .685), (.84, .009), (-.28, .510)]),
        (20, (*PAIRS[1:3], PAIRS[-1]), [(-.01, .982), (-.26, .266), (-.15, .530)]),
    ],
}


def pearson_p(r, n):
    return float(2 * t.sf(abs(r) * math.sqrt((n - 2) / (1 - r * r)), n - 2))


def check_tables():
    results = []
    for station, blocks in TABLES.items():
        for stage, (n, pairs, values) in zip(
                ('emergence', 'vegetative', 'tasselling', 'maturity'), blocks, strict=True):
            for pair, (r, p) in zip(pairs, values, strict=True):
                lo = pearson_p(abs(r) + .005, n)
                hi = pearson_p(max(0, abs(r) - .005), n)
                results.append(dict(station=station, stage=stage, variables=pair,
                                    n=n, reported_r=r, reported_p=p,
                                    p_at_displayed_r=pearson_p(r, n),
                                    p_from_rounded_r_interval=[lo, hi],
                                    compatible=lo <= p + .0005 and p - .0005 <= hi))
    return results


def main():
    source = Path(sys.argv[1]).resolve()
    attempts = json.loads(source.read_text(encoding='utf-8'))
    assert sha256(source.with_name('metadata.json')) == attempts['metadata.json']['sha256']
    rows = check_tables()
    conflicts = [row for row in rows if not row['compatible']]
    assert len(rows) == 32
    run = new_run(ROOT, 'koffi_togo_linkage_audit')
    write_json(run / 'linkage_audit.json', {
        'article_doi': '10.1111/afe.12693',
        'dataset_doi': '10.5061/dryad.5dv41nsgz',
        'acquisition_evidence': source.relative_to(ROOT).as_posix(),
        'acquisition': attempts,
        'verified_worksheet_rows': 0,
        'verified_dated_plot_visits': 0,
        'verified_weather_joins': 0,
        'verified_crop_application_events': 0,
        'methods_report_no_faw_crop_control_at_stations': True,
        'reported_station_pearson_checks': rows,
        'reported_station_pearson_incompatible_count': len(conflicts),
        'pearson_check_scope': 'Two-sided standard test from reported n and r. Rounding bounds for displayed r and p. No raw refit.',
        'quantitative_fit_ready': False,
        'research_ready': False,
        'main_training_allowed': False,
    })
    print(run.relative_to(ROOT).as_posix())
    print(json.dumps(conflicts, indent=2))


if __name__ == '__main__':
    main()
