"""Frozen experiment identities and independently checked evaluation batches."""
import hashlib
import json
import math

from .artifacts import write_json
from .comparison import table_cells
from .exogenous import WGEN_SEED_RANGES


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def freeze_json(path, value):
    if path.exists():
        if json.loads(path.read_text(encoding='utf-8')) != json.loads(json.dumps(value)):
            raise ValueError(f'Frozen identity changed: {path}')
    else:
        write_json(path, value)


def initialization(config, channels):
    values = config['training']['sparse_nonzero_mass']
    names = ('irrigation', 'nitrogen', 'spray')
    spec = {names[c]: values[names[c]] for c in channels}
    for value in spec.values():
        if value is not None and (isinstance(value, bool) or not 0 < value < 1):
            raise ValueError('Nonzero prior mass must be null (library default) or between zero and one')
    return spec


def validate_split(config, split, seasons):
    if split not in ('validation', 'test') or not seasons or len(set(seasons)) != len(seasons):
        raise ValueError('Explicit validation/test split and unique nonempty seasons required')
    lo, hi = WGEN_SEED_RANGES[split]
    if any(type(s) is not int or not 0 <= s < hi-lo+1 for s in seasons):
        raise ValueError('Season address outside WGEN partition')
    selection = config['training']['checkpoint_selection']
    if split == 'validation' and set(seasons) & set(range(selection['first_season'],
            selection['first_season']+selection['seasons'])):
        raise ValueError('Evaluation seasons overlap checkpoint selection')


def validate_batch(rows, season, seeds, conditions, table_rows, split):
    expected = {(row, col, policy, cond, seed) for row,col,policy,cond in table_cells(conditions, table_rows)
                for seed in ([None] if policy in ('0', 'b0p') else seeds)}
    keys = [(r['row'],r['column'],r['policy'],r['condition'],r['seed']) for r in rows]
    if len(keys) != len(expected) or set(keys) != expected:
        raise ValueError('Incomplete or duplicate evaluation cells')
    for r in rows:
        if r['season_id'] != season or r.get('split') != split:
            raise ValueError('Evaluation season/split mismatch')
        if r['resource_violations'] or not math.isfinite(r['net_return']):
            raise ValueError('Invalid evaluation return or resource violation')
        shock = conditions[r['condition']]
        if shock is not None and r['water_cut_day'] != shock.day:
            raise ValueError('Reduction calendar mismatch')
