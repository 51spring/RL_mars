"""DSSAT yield response to single early defoliation, against Blanco et al. (2022).

Blanco 2022 removed 0, 33 and 66 % of foliage at V1-V2 and V3-V4 and found no yield reduction.
Pre-stated rule: if every simulated mean ratio lies within 1.0 +/- 0.10 (the tier B tolerance),
no early-stage damage weight is added. Uses the tier B seasons and management unchanged.
"""
import os
from pathlib import Path
from statistics import mean, pstdev
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts")]
import judge_damage_recovery_tier_b as tier_b
from mars_env.artifacts import new_run, write_json

tier_b.STAGE_RULES.update({"V2": lambda s: float(s["vstage"]) >= 2, "V4": lambda s: float(s["vstage"]) >= 4,
                           "V6": lambda s: float(s["vstage"]) >= 6})
CELLS = (("V2", 33), ("V2", 66), ("V4", 33), ("V4", 66), ("V6", 66))
SEEDS = list(range(4001, 4017))
TOLERANCE = 0.10


def main():
    run = new_run(ROOT, "early_defoliation_check")
    (run / "native_logs").mkdir()
    os.environ["MARS_RUN_DIR"] = str(run)
    print("RUN_DIR=" + str(run), flush=True)
    records = []
    for seed in SEEDS:
        records.append(tier_b.season(run, f"s{seed}_control", seed, None, 0.0))
        for stage, pct in CELLS:
            records.append(tier_b.season(run, f"s{seed}_{stage}_{pct}", seed, stage, pct / 100))
        print(seed, flush=True)
    controls = {r["wgen_seed"]: r["yield_kg_ha"] for r in records if r["stage"] is None}
    cells = []
    for stage, pct in CELLS:
        rows = [r for r in records if r["stage"] == stage and round(r["fraction"] * 100) == pct]
        ratios = [r["yield_kg_ha"] / controls[r["wgen_seed"]] for r in rows]
        cells.append({"stage": stage, "defoliation_pct": pct, "mean_ratio": mean(ratios), "sd": pstdev(ratios),
                      "min": min(ratios), "max": max(ratios), "within_tolerance": abs(mean(ratios) - 1) <= TOLERANCE,
                      "pulse_dap_mean": mean(r["pulse"]["dap"] for r in rows),
                      "all_valid": all(r["valid"] for r in rows)})
    verdict = all(c["within_tolerance"] and c["all_valid"] for c in cells)
    write_json(run / "verification.json", {"passed": verdict, "rule": "all mean ratios within 1.0 +/- 0.10",
                                           "reference": "Blanco et al. 2022, 0/33/66% at V1-V2 and V3-V4, no yield reduction",
                                           "cells": cells, "control_yield_kg_ha": controls, "records": records,
                                           "research_ready": False})
    for cell in cells:
        print(cell, flush=True)
    print("PASSED", verdict, flush=True)


if __name__ == "__main__":
    main()
