"""Reduction draws of the training seasons met in each step window of a pilot (policy b, 8 environments).

All fits see the same training season sequence (season_id = rank + count * n_envs), so a step window maps to a
season-id range. Compares reduction day and fraction in each window with the rest. No DSSAT run.
"""
from pathlib import Path
import sys

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from mars_env.exogenous import generate_season

STEPS_PER_SEASON = 132.8  # decision days per season (rule policy, section 6)


def main():
    config = yaml.safe_load((ROOT / "configs/proposal_v2.yaml").read_text(encoding="utf-8"))
    probability = config["scenarios"]["reduction_probability"]
    windows = [(0, 100_000), (100_000, 300_000), (300_000, 460_000), (460_000, 700_000), (700_000, 1_024_000)]
    for start, end in windows:
        ids = range(int(start / STEPS_PER_SEASON), int(end / STEPS_PER_SEASON))
        days, fractions, cut = [], [], 0
        for season_id in ids:
            shock = generate_season(config, split="train", season_id=season_id, reduction_probability=probability).shock
            if shock is not None:
                cut += 1
                days.append(shock.day)
                fractions.append(shock.fraction)
        days, fractions = np.array(days), np.array(fractions)
        early = np.mean(days <= 40) if days.size else 0
        print(f"steps {start:>9,}-{end:>9,} seasons {ids.start:>5}-{ids.stop:>5} n={len(ids):5d} cut share {cut/len(ids):.3f} "
              f"day mean {days.mean():5.1f} early(<=40) {early:.3f} fraction mean {fractions.mean():.3f} "
              f"large(>=0.5) {np.mean(fractions >= 0.5):.3f} early&large {np.mean((days <= 40) & (fractions >= 0.5)):.3f}")


if __name__ == "__main__":
    main()
