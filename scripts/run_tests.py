"""Run core regressions and persist a compact status report."""
import json
import argparse
from pathlib import Path
import sys
import time
from datetime import datetime, timezone, timedelta
import unittest

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT / 'outputs/core_test_results.json')
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    start = time.perf_counter()
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {
        "time_kst": datetime.now(timezone(timedelta(hours=9))).isoformat(),
        "tests_run": result.testsRun,
        "failures": len(result.failures), "errors": len(result.errors),
        "skipped": len(result.skipped), "passed": result.wasSuccessful(),
        "elapsed_seconds": time.perf_counter() - start,
        "scope": "Resources, observations, terminal/Gymnasium contracts, external sampling, experimental online pest/survey, native leaf protocol, plant N audit, potential rewards, date/soil audits, provenance and policy interfaces; real DSSAT reports are separate",
        "checks": ["108-action mask feasibility", "100 random seasons x 120 decisions",
                   "baseline 116kg nitrogen", "one-time water reductions",
                   "spray constraints", "invalid action rejection and atomic ledger updates",
                   "terminal harvest vs truncation", "observation history and hidden-scenario exclusion",
                   "backend failure invalidates episode", "pest-enabled execution refused",
                   "independent named external streams", "paired conditions preserve external arrays",
                   "same-day pest control and residual reset", "seven-day survey with previous-day-only information",
                   "PDI leaf data versus metadata schema", "leaf dry-mass and nitrogen export identities",
                   "independent native cumulative export ledger", "native seed N input without dead-leaf double count",
                   "day-close chronological pest/survey updates", "experimental policy observation excludes private density",
                   "reward telescoping with true terminal versus truncation", "unique configuration YAML keys",
                   "calendar rollover and native weather date mismatches", "soil flux removal is detected",
                   "rule/irrigation-only feasible action contract", "resumed external season addresses",
                   "public evidence independence and calibration readiness"],
    }
    output = args.output.resolve()
    if not output.is_relative_to((ROOT / 'outputs').resolve()):
        raise ValueError('Test report must remain inside this project outputs directory')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
