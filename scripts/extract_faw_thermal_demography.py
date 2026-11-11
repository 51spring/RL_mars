"""Extract maize thermal demography from archived Europe PMC JATS tables."""
import argparse
from decimal import Decimal
import json
import math
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from mars_env.artifacts import new_run, sha256, write_json


def table_rows(article, table_id):
    table = article.find(f'.//table-wrap[@id="{table_id}"]')
    return [
        [' '.join(''.join(cell.itertext()).split()) for cell in row]
        for row in table.findall('.//tr')
    ]


def maize_cells(rows, index):
    cells = {}
    for row in rows:
        if row[0].isdigit():
            temperature = int(row[0])
            if temperature in cells:
                raise ValueError(f'Duplicate temperature {temperature}')
            raw = row[index]
            match = re.fullmatch(r'(\d+(?:\.\d+)?) ± (\d+(?:\.\d+)?)\s*([a-zA-Z]+)', raw)
            cells[temperature] = {
                'raw': raw,
                'mean': float(match[1]) if match else None,
                'se': float(match[2]) if match else None,
            }
    return cells


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sources', type=Path)
    args = parser.parse_args()
    source_dir = args.sources.resolve()
    sources = json.loads((source_dir / 'sources.json').read_text(encoding='utf-8'))
    articles = {}
    for name in ('hosts2022', 'ilcym2024'):
        xml = source_dir / f'{name}.xml'
        if sha256(xml) != sources[name]['sha256']:
            raise ValueError(f'Source digest mismatch for {xml}')
        articles[name] = ET.parse(xml)

    reproduction = table_rows(articles['hosts2022'], 'insects-13-00211-t003')
    demography = table_rows(articles['hosts2022'], 'insects-13-00211-t004')
    assert reproduction[11][3] == demography[1][0] == demography[1][3] == 'Maize'
    assert reproduction[10][2].startswith('Fecundity')
    chen = {
        'fecundity_eggs': maize_cells(reproduction[12:15], 4),
        'r_per_day': maize_cells(demography[2:5], 1),
        'lambda': maize_cells(demography[2:5], 4),
        'R0': maize_cells(demography[7:10], 1),
        'T_days': maize_cells(demography[7:10], 4),
        'GRR': maize_cells(demography[12:15], 1),
    }
    assert all(set(cells) == {20, 25, 30} for cells in chen.values())
    missing = [(metric, t) for metric, cells in chen.items()
               for t, cell in cells.items() if cell['mean'] is None]
    assert missing == [('fecundity_eggs', 20)]

    rows = table_rows(articles['ilcym2024'], 'pone.0299154.t008')
    assert rows[0] == ['Temperature', 'rm', 'Ro', 'GRR', 'Tc', 'λ', 'Dt']
    adan = {}
    lambda_check = {}
    for temp, *values in rows[1:-1]:
        t = int(temp)
        assert t not in adan
        adan[t] = dict(zip(('r_per_day', 'R0', 'GRR', 'T_days', 'lambda', 'doubling_days'),
                           map(float, values), strict=True))
        r, lam = Decimal(values[0]), Decimal(values[4])
        r_upper = r + Decimal('0.0000005')
        r_lower = r - Decimal('0.0000005')
        lam_rounding = Decimal('0.0000005')
        lambda_check[t] = {
            'reported_minus_exp_r': float(lam) - math.exp(float(r)),
            'compatible_with_six_decimal_rounding': (
                r_lower.exp() <= lam + lam_rounding and lam - lam_rounding <= r_upper.exp()),
        }
    assert set(adan) == {20, 25, 28, 30, 32}
    chen_delta = chen['r_per_day'][30]['mean'] - chen['r_per_day'][25]['mean']
    adan_delta = adan[30]['r_per_day'] - adan[25]['r_per_day']
    assert chen_delta > 0 > adan_delta
    assert max(adan, key=lambda t: adan[t]['r_per_day']) == 28

    run = new_run(ROOT, 'faw_thermal_demography')
    write_json(run / 'thermal_demography.json', {
        'source_directory': source_dir.relative_to(ROOT).as_posix(),
        'sources': sources,
        'chen_2022': {'tables': [3, 4], 'estimate_type': 'cohort life table',
                      'uncertainty': 'bootstrap SE', 'maize': chen},
        'adan_2024': {'table': 8, 'estimate_type': 'ILCYM stochastic simulation',
                      'per_temperature_uncertainty': None, 'sprouted_maize': adan},
        'common_temperature_c': [20, 25, 30],
        'r_25_to_30_change_per_day': {'chen_2022': chen_delta, 'adan_2024': adan_delta},
        'adan_lambda_consistency': lambda_check,
        'scope': 'laboratory thermal response shape and sensitivity evidence',
        'quantitative_fit_ready': False,
        'research_ready': False,
        'main_training_allowed': False,
    })
    print(run.relative_to(ROOT).as_posix())


if __name__ == '__main__':
    main()
