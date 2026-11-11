"""Verify dated native CERES growth IPAR against uninstrumented UFGA seasons."""
from datetime import datetime, timedelta
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mars_env.artifacts import new_run, sha256, write_json
from mars_env.harvest_diagnostics import HarvestBoundaryBackend
from mars_env.input_metadata import canonical_ufga_metadata
from mars_env.ipar_diagnostics import CeresIparProtocol
from verify_metadata_harvest import normal

SEED = 123456
PULSE_DAP = 45
PULSE = 0.75


def next_day(yrdoy):
    day = datetime.strptime(str(yrdoy), "%Y%j") + timedelta(days=1)
    return int(day.strftime("%Y%j"))


def season(folder, instrumented, fraction, *, filex_transform=canonical_ufga_metadata, seed=SEED):
    folder.mkdir()
    backend = HarvestBoundaryBackend(
        filex_transform=filex_transform,
        run_dssat_location="/opt/mars/run_ipar" if instrumented else "/opt/mars/run_boundary",
    )
    backend._runtime_log_path = str(folder / "runtime.log")
    sidecar = folder / "growth_ipar.jsonl"
    if instrumented:
        backend._instrumentation = CeresIparProtocol(sidecar)
    trace = []
    try:
        state = backend.reset(seed)
        for _ in range(400):
            day, dap = int(state["yrdoy"]), int(state["dap"])
            damage = fraction if dap == PULSE_DAP else 0
            water = 10 if dap in (10, 20, 30, 40, 50, 60, 70, 80) else 0
            nitrogen = {40: 27, 45: 35, 80: 54}.get(dap, 0)
            state, done, outcome = backend.step_damage(water, nitrogen, damage)
            trace.append({"action_date": day, "dap": dap, "fraction": damage, "after": normal(state)})
            if done:
                assert outcome.reason == "harvest"
                break
        else:
            raise AssertionError("Season did not finish")
    finally:
        backend.close()
    write_json(folder / "states.json", trace)
    write_json(folder / "outcome.json", vars(outcome))
    samples = [json.loads(line) for line in sidecar.read_text().splitlines()] if instrumented else []
    return trace, outcome, samples


def check_growth(trace, outcome, samples):
    by_date = {row["date"]: row for row in samples}
    actions = {row["action_date"]: row for row in trace}
    assert samples and len(by_date) == len(samples)
    dates = list(by_date)
    assert all(next_day(a) == b for a, b in zip(dates, dates[1:]))
    assert by_date.keys() <= actions.keys()
    terminal = trace[-1]["after"]
    maturity = int(outcome.summary["MDAT"])
    harvest = int(outcome.summary["HDAT"])
    assert terminal["mars_harvest_boundary"]["date"] == harvest
    assert dates[0] > int(outcome.summary["PDAT"]) and next_day(dates[-1]) == maturity
    assert maturity not in by_date and harvest not in by_date
    errors = []
    for row in samples:
        assert all(math.isfinite(v) for v in row.values())
        assert row["pop"] > 0 and row["row_cm"] > 0 and row["lai"] >= 0 and row["srad"] >= 0
        extinction = 1.5 - 0.768 * ((row["row_cm"] / 100) ** 2 * row["pop"]) ** 0.1
        assert math.isclose(row["lifac"], extinction, abs_tol=2e-7)
        assert math.isclose(row["par"], row["srad"] * 0.5, abs_tol=1e-6)
        expected = row["par"] / row["pop"] * -math.expm1(-row["lifac"] * row["lai"])
        assert 0 <= row["energy"] <= row["par"] / row["pop"]
        assert math.isclose(row["energy"], expected, abs_tol=3e-7)
        errors.append(abs(row["energy"] - expected))
    return by_date, {"rows": len(samples), "first_growth": dates[0], "last_growth": dates[-1],
                     "maturity": maturity, "harvest": harvest, "max_energy_abs_error": max(errors)}


def main():
    run = new_run(ROOT, "native_ceres_ipar")
    print(f"RUN_DIR={run}", flush=True)
    evidence = {}
    growth = {}
    try:
        for label, fraction in (("control", 0), ("pulse", PULSE)):
            baseline, expected, _ = season(run / f"{label}_baseline", False, fraction)
            trace, outcome, samples = season(run / f"{label}_instrumented", True, fraction)
            assert baseline == trace and expected == outcome
            growth[label], evidence[label] = check_growth(trace, outcome, samples)
            evidence[label]["baseline_state_and_outcome_exact"] = True
            if label == "pulse":
                pulse, = [row for row in trace if row["fraction"]]
                day = pulse["action_date"]
                leaf = pulse["after"]["mars_leaf_diagnostic"]
                assert leaf["yrdoy"] == day
                assert growth["control"][day] == growth["pulse"][day]
                next_date = next_day(day)
                next_rate = growth["pulse"][next_date]
                assert next_rate["lai"] == leaf["after"]["xlai"]
                assert next_rate["lai"] < growth["control"][next_date]["lai"]
                assert next_rate["energy"] < growth["control"][next_date]["energy"]
                evidence[label]["pulse_timing"] = {"pulse_date": day, "next_growth_date": next_date,
                    "pulse_day_growth_identical_to_control": True, "pre_damage_close_lai": leaf["before"]["xlai"],
                    "post_damage_close_lai": leaf["after"]["xlai"],
                    "next_growth_lai": next_rate["lai"], "next_growth_ipar": next_rate["energy"],
                    "control_next_growth_ipar": growth["control"][next_date]["energy"]}
            print(label, evidence[label], flush=True)
        write_json(run / "verification.json", {"passed": True, "cases": evidence, "seasons": 4,
            "seed": SEED, "diagnostic_only": True, "research_ready": False,
            "source_sha256": sha256(ROOT / "vendor/dssat-pdi-source/Plant/CERES-Maize/MZ_GROSUB.for")})
    except BaseException as exc:
        write_json(run / "failure.json", {"passed": False, "error": repr(exc)})
        raise


if __name__ == "__main__":
    main()
