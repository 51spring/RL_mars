"""Experimental Fortran leaf writes, mass/N identities, and zero-injury regression."""
import json
import math
from pathlib import Path
import sys

sys.path.insert(0, "/workspace/src")
from mars_env.dssat_backend import DssatBackend
from mars_env.leaf_diagnostics import LeafDiagnosticBackend, verify_leaf_accounting


def normal(value):
    if isinstance(value, dict):
        return {k: normal(v) for k, v in value.items()}
    return value.tolist() if hasattr(value, "tolist") else value


def run(backend, pulses):
    trace, records, outcome = [], {}, None
    if getattr(backend, "_runtime_log_path", None) is None:
        backend._runtime_log_path = "/workspace/outputs/native_control_runtime.log"
    print(f"Starting {backend.run_dssat_location}, pulses={pulses}", flush=True)
    try:
        state = backend.reset(seed=123456)
        for _ in range(400):
            trace.append(normal(state))
            dap = int(state["dap"])
            nitrogen = {40: 27, 45: 35, 80: 54}.get(dap, 0)
            water = 10 if dap in (10, 20, 30, 40, 50, 60, 70, 80) else 0
            # Apply a pulse only once per DAP (preplant DAP is repeatedly zero).
            fraction = pulses.get(dap, 0) if dap not in records else 0
            if isinstance(backend, LeafDiagnosticBackend):
                state, done, outcome = backend.step_damage(water, nitrogen, fraction)
            else:
                state, done, outcome = backend.step(water, nitrogen)
            record = state.get("mars_leaf_diagnostic")
            if record is not None and record["dap"] == dap:
                verify_leaf_accounting(record)
                records[dap] = record
                assert math.isclose(state["xlai"], record["after"]["xlai"], abs_tol=2e-5)
                assert math.isclose(state["topwt"] / 10, record["after"]["topwt"], abs_tol=2e-5)
            if done:
                assert outcome is not None
                return trace, records, outcome
        raise RuntimeError("Native leaf test did not terminate")
    finally:
        backend.close()


def main():
    packaged, _, packaged_outcome = run(DssatBackend(), {})
    control, _, control_outcome = run(DssatBackend(run_dssat_location="/opt/mars/run_control"), {})
    zero, zero_records, zero_outcome = run(LeafDiagnosticBackend(), {})
    assert len(control) == len(zero)
    for index, (a, b) in enumerate(zip(control, zero)):
        mismatches = [key for key in a if a[key] != b[key]]
        assert not mismatches, f"Zero injury changed source-built crop trajectory at {index}: {mismatches}"
    assert control_outcome == zero_outcome
    packaged_exact = packaged == control and packaged_outcome == control_outcome
    pulse, pulse_records, pulse_outcome = run(LeafDiagnosticBackend(), {15: 0.25, 50: 0.25})
    applied = [r for r in pulse_records.values() if r["fraction"] > 0]
    Path("/workspace/outputs/native_leaf_probe_records.json").write_text(json.dumps(pulse_records, indent=2))
    assert len(applied) == 2, f"Expected two pulses; received {[(r['dap'], r['fraction']) for r in applied]}, recorded days={list(pulse_records)}"
    for record in applied:
        assert record["export_dm_g_m2"] > 0 and record["export_n_g_m2"] > 0
    first = applied[0]
    assert first["vstage"] < 7, "Early injury case did not occur before V7"
    # Current day's growth completed identically before the first injury.
    assert first["before"] == zero_records[15]["before"]
    first_next = next(s for s in pulse if int(s["dap"]) == 16)
    zero_next = next(s for s in zero if int(s["dap"]) == 16)
    assert first_next["xlai"] != zero_next["xlai"]
    assert all(x["xlai"] >= 0 and x["topwt"] >= 0 for x in pulse)
    report = {"passed": True, "experimental_only": True,
              "control_zero_injury_trajectory_exact": True,
              "packaged_vs_source_control_exact": packaged_exact,
              "zero_diagnostic_days": len(zero_records),
              "before_first_injury_growth_unchanged": True,
              "next_decision_observes_native_injury": True,
              "early_vstage": first["vstage"], "applied_records": applied,
              "harvested_grain_kg_ha": {"packaged": packaged_outcome.harvested_grain_kg_ha,
                                         "control": control_outcome.harvested_grain_kg_ha,
                                         "zero": zero_outcome.harvested_grain_kg_ha,
                                         "pulses": pulse_outcome.harvested_grain_kg_ha},
              "research_pest_execution_enabled": False,
              "agronomic_recovery_validated": False,
              "whole_season_carbon_nitrogen_balance_validated": False}
    Path("/workspace/outputs/native_leaf_verification.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        Path("/workspace/outputs/native_leaf_verification.json").write_text(
            json.dumps({"passed": False, "experimental_only": True, "error": str(exc)}, indent=2))
        raise
