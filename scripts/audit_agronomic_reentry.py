"""Cross-check active agronomic evidence against independent validation requirements."""
from decimal import Decimal
from itertools import product
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from mars_env.agronomic_scenarios import build_registry, readiness
from mars_env.artifacts import new_run, sha256, write_json
from mars_env.validation_lineage import independent_lineage_status


def main():
    sources_file = ROOT / 'configs/agronomic_sources.json'
    priorities_file = ROOT / 'configs/agronomic_input_priorities.json'
    sources = json.loads(sources_file.read_text(encoding='utf-8'))['studies']
    priorities = json.loads(priorities_file.read_text(encoding='utf-8'))
    registry = build_registry(ROOT)
    lineage = [independent_lineage_status(ROOT, study) for study in sources]
    assessments = [{'scenario_id': row['scenario_id'], **readiness(row)} for row in registry]
    assert {study['id'] for study in sources} == {study['id'] for study in priorities['studies']}

    means = {(row['factors']['water'], row['factors']['defoliation']): Decimal(str(row['observed_mean']))
             for row in registry if row['study_id'] == 'oveysi2010'}
    assert set(means) == set(product(('W1', 'W2'), ('D1', 'D2', 'D3', 'D4', 'D5')))
    contrasts = []
    for damage in ('D2', 'D3', 'D4', 'D5'):
        w1 = means['W1', damage] - means['W1', 'D1']
        w2 = means['W2', damage] - means['W2', 'D1']
        contrasts.append({'damage': damage, 'w1_damage_minus_control_t_ha': float(w1),
                          'w2_damage_minus_control_t_ha': float(w2),
                          'w2_minus_w1_effect_t_ha': float(w2 - w1),
                          'uncertainty': None, 'descriptive_only': True})

    cells = list(product((0, 1), repeat=3))
    parity = np.array([(-1)**(3 - sum(cell)) for cell in cells])
    # Equal-weight sums along one dimension expose every possible two-way margin.
    margins = np.array([[int(all(cell[i] == assignment[j] for j, i in enumerate(axes)))
                         for cell in cells]
                        for axes in ((0, 1), (0, 2), (1, 2))
                        for assignment in product((0, 1), repeat=2)])
    rank = int(np.linalg.matrix_rank(margins))
    assert rank == 7 and not (margins @ parity).any()
    assert parity @ parity == 8
    run = new_run(ROOT, 'agronomic_reentry_audit')
    write_json(run / 'verification.json', {
        'passed': True,
        'scope': 'local scenario/lineage recheck and descriptive contrasts; no scientific qualification',
        'registry_sha256': sha256(sources_file),
        'priorities_sha256': sha256(priorities_file),
        'public_studies': len(sources),
        'quantitative_fit_ready_studies': [s['id'] for s in sources if s['quantitative_fit_ready']],
        'independent_lineage': [row for row in lineage if row['required']],
        'scenarios': assessments,
        'oveysi_water_by_damage': contrasts,
        'three_way_design': {
            'cell_axes': ['water_stress', 'nitrogen_treatment', 'damage_treatment'],
            'cell_order': cells, 'three_way_contrast_coefficients': parity.tolist(),
            'required_cells_for_direct_contrast': 8,
            'two_way_margin_matrix_rank': rank,
            'observed_eligible_joint_designs_in_review': 0,
            'assumption': 'binary factorial direct contrast; equal-weight margins used only for identifiability demonstration',
        },
        'independent_recovery_validated': False,
        'water_nitrogen_damage_interaction_validated': False,
        'research_ready': False,
        'main_training_allowed': False,
    })
    print(run.relative_to(ROOT).as_posix())


if __name__ == '__main__':
    main()
