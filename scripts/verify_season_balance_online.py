"""Repeated/severe injury exports, N inventory drift, and experimental online coupling."""
from dataclasses import replace
import json
import math
from pathlib import Path
import sys

import numpy as np
import yaml

sys.path.insert(0, "/workspace/src")
from mars_env.balances import RemovalLedger, NitrogenInventoryDiagnostic
from mars_env.dssat_backend import DssatBackend
from mars_env.exogenous import generate_season
from mars_env.leaf_diagnostics import LeafDiagnosticBackend
from mars_env.online_pests import ExperimentalOnlineBackend
from mars_env.pests import PestParameters, PestState, DamageSurvey
from mars_env.resources import ResourceLedger, Action


def normal(value):
    return value.tolist() if hasattr(value, "tolist") else value


def run_case(name, backend, seed, pulses=None, online=False, spray_days=(), *, wgen_seed=None):
    print(f"Case {name}", flush=True)
    removal, inventory = RemovalLedger(), NitrogenInventoryDiagnostic()
    trace, diagnostics = [], []
    try:
        state = backend.reset(seed, wgen_seed=wgen_seed)
        while state["yrdoy"] < backend.planting_yrdoy:
            state, done, _ = backend.step(0, 0)
            assert not done
        ledger = ResourceLedger.create()
        total_reward = 0
        for day in range(240):
            ledger = ledger.open_day(day, int(state["istage"]))
            dap, completed_date = int(state["dap"]), int(state["yrdoy"])
            trace.append({k: normal(v) for k, v in state.items() if not k.startswith("mars_")})
            water = 10 if dap in (10, 20, 30, 40, 50, 60, 70, 80) else 0
            nitrogen = {40: 27, 45: 35, 80: 54}.get(dap, 0)
            spray = online and day in spray_days and bool(ledger.action_masks()[-1])
            action = Action(water, nitrogen, int(spray))
            ledger.validate(action)
            if online:
                state, done, outcome = backend.step_online(water, nitrogen, bool(spray))
            else:
                fraction = pulses(dap) if pulses else 0
                state, done, outcome = backend.step_damage(water, nitrogen, fraction)
            ledger, cost = ledger.commit(action)
            total_reward -= cost.total
            assert all(math.isfinite(float(state[k])) and state[k] >= 0 for k in ("xlai", "topwt", "grnwt"))
            audit = state["mars_plant_audit"]
            inventory.append(completed_date, audit)
            record = state.get("mars_leaf_diagnostic")
            if record is not None and record["yrdoy"] == completed_date:
                removal.append(record)
            assert math.isclose(audit["cum_dm"], removal.dry_matter_g_m2, rel_tol=5e-5, abs_tol=3e-5)
            assert math.isclose(audit["cum_n"], removal.nitrogen_g_m2, rel_tol=5e-5, abs_tol=3e-5)
            if online:
                diagnostic = state["mars_pest_diagnostic"]
                assert diagnostic["day"] == day
                assert math.isclose(diagnostic["mean_temperature_c"], (state["tmin"] + state["tmax"]) / 2, abs_tol=1e-6)
                diagnostics.append(diagnostic)
            if done:
                assert outcome is not None
                total_reward += outcome.harvested_grain_kg_ha * 0.158
                assert math.isclose(total_reward, outcome.harvested_grain_kg_ha * 0.158 - ledger.total_cost, abs_tol=1e-6)
                report = {"name": name, "days": day + 1, "harvested_grain_kg_ha": outcome.harvested_grain_kg_ha,
                          "reason": outcome.reason, "net_return": total_reward, "sprays": ledger.sprays,
                          "removal": removal.summary(), "nitrogen_inventory_diagnostic": inventory.summary(),
                          "nitrogen_rows": inventory.rows, "online_diagnostics": diagnostics}
                return report, trace
        raise RuntimeError("Scenario did not end")
    finally:
        backend.close()


def check_online_replay(report, parameters, season, noise_std):
    pest = PestState()
    survey = DamageSurvey(parameters.alpha, noise_std).morning(0, float(season.survey_standard_noise[0]))
    for row in report["online_diagnostics"]:
        day = row["day"]
        pest, requested, effect = pest.advance(day, row["mean_temperature_c"], float(season.pest_arrivals[day]), row["spray"], parameters)
        assert math.isclose(pest.density, row["density"], abs_tol=1e-12)
        assert math.isclose(requested, row["requested_fraction"], abs_tol=1e-12)
        assert math.isclose(effect, row["effect"], abs_tol=1e-12)
        # Native REAL writes round the applied fraction to float32.
        survey = survey.complete_day(day, row["applied_fraction"]).morning(day + 1, float(season.survey_standard_noise[day + 1]))
        assert survey.observation() == row["next_morning_survey"]


def main():
    reports = []
    for name, pulses in (("zero", lambda d: 0), ("daily_3pct", lambda d: 0.03 if 15 <= d <= 100 else 0),
                         ("single_95pct", lambda d: 0.95 if d == 35 else 0),
                         ("late_50pct", lambda d: 0.5 if d == 90 else 0)):
        report, _ = run_case(name, LeafDiagnosticBackend(), 123456, pulses)
        reports.append(report)
    assert reports[0]["removal"]["removed_nitrogen_kg_ha"] == 0
    assert all(r["removal"]["injury_days"] > 0 for r in reports[1:])
    config = yaml.safe_load(Path("/workspace/configs/proposal_v2.yaml").read_text())
    season = generate_season(config, split="validation", season_id=0)
    # Explicit diagnostic anchors; not calibrated and not written into default config.
    parameters = PestParameters(temperature_low_c=10, temperature_high_c=30)
    for name, sprays in (("online_unsprayed", ()), ("online_sprayed", (20, 27))):
        backend = ExperimentalOnlineBackend(parameters=parameters, noise_std=0.01, season=season)
        report, _ = run_case(name, backend, season.backend_seed, online=True, spray_days=sprays,
                             wgen_seed=season.wgen_seed)
        check_online_replay(report, parameters, season, 0.01)
        reports.append(report)
    zero_parameters = replace(parameters, alpha=0)
    online_zero, zero_trace = run_case("online_alpha_zero", ExperimentalOnlineBackend(
        parameters=zero_parameters, noise_std=0.01, season=season), season.backend_seed, online=True, wgen_seed=season.wgen_seed)
    check_online_replay(online_zero, zero_parameters, season, 0.01)
    native_zero, native_trace = run_case("matching_native_zero", LeafDiagnosticBackend(), season.backend_seed,
                                         wgen_seed=season.wgen_seed)
    assert zero_trace == native_trace
    assert online_zero["harvested_grain_kg_ha"] == native_zero["harvested_grain_kg_ha"]
    reports.extend((online_zero, native_zero))
    assert all(r["nitrogen_inventory_diagnostic"]["plant_n_inventory_balance_within_tolerance"] for r in reports)
    result = {"diagnostic_pipeline_passed": True, "cases": reports,
              "online_density_and_survey_replay_passed": True, "completed_day_weather_checked": True,
              "alpha_zero_original_crop_trajectory_exact": True,
              "plant_n_inventory_balance_checked": True,
              "temperature_anchors_c": [10, 30], "survey_noise_std": 0.01,
              "temperature_statistic": "mean of completed-day Tmin and Tmax",
              "calibrated_parameters": False, "whole_season_carbon_nitrogen_balance_validated": False,
              "research_pest_execution_enabled": False}
    Path("/workspace/outputs/season_balance_online_verification.json").write_text(json.dumps(result, indent=2))
    print(json.dumps({"diagnostic_pipeline_passed": True, "cases": [
        {k:r[k] for k in ("name", "days", "removal", "nitrogen_inventory_diagnostic")} for r in reports]}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        Path("/workspace/outputs/season_balance_online_verification.json").write_text(json.dumps({"diagnostic_pipeline_passed": False, "error": str(exc)}))
        raise
