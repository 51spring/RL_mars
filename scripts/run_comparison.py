"""Train the a/b policy chains, then evaluate every table cell on common seasons.

Uses the validation split only; the final test split stays closed until the design is frozen.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from functools import partial
import json
from math import isclose
from multiprocessing import get_context
import os
from pathlib import Path
import sys
import time

import numpy as np
import torch
import yaml
from sb3_contrib import MaskablePPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.vec_env import SubprocVecEnv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from mars_env.economics import grain_price
from mars_env.artifacts import new_run, sha256, write_json
from mars_env.baseline_evaluation import evaluate_episode
from mars_env.comparison import (ROWS, contrasts, inference, resource_violations, results_table, supply_variant,
                                 survey_noise_variant, table_cells,
                                 training_plan)
from mars_env.experimental_env import ExperimentalPestEnv
from mars_env.exogenous import evaluation_conditions, generate_season
from mars_env.pests import pest_settings
from mars_env.policies import CompositePolicy, FrozenChannels, ReductionResponseRule, RulePolicy
from mars_env.process_backend import LegacyProcessBackend
from mars_env.resources import ResourceRules
from mars_env.training_env import ChannelCycler

NAMES = ("irrigation", "nitrogen", "spray")
SIZES = (6, 9, 2)


class Audit(BaseCallback):
    def __init__(self):
        super().__init__()
        self.returns, self.truncations = [], 0

    def _on_step(self):
        for info in self.locals["infos"]:
            audit = info.get("reward_audit")
            if audit is None:
                continue
            assert abs(audit["telescoping_residual"]) < 1e-5
            self.truncations += int(audit["administrative_truncation"])
            if audit["complete_episode"]:
                assert isclose(audit["raw_return"], info["episode_result"]["net_return"], abs_tol=1e-5)
                self.returns.append(audit["raw_return"])
        return True


def checkpoint(run, label):
    return run / f"{label}.zip"


def train(run, config, fit):
    path, record = checkpoint(run, fit.label), run / f"{fit.label}_training.json"
    if record.exists():
        assert json.loads(record.read_text())["checkpoint_sha256"] == sha256(path)
        return
    frozen = tuple((str(checkpoint(run, label)), channels) for label, channels in fit.frozen)
    cfg = config["training"]
    n_envs = cfg["n_envs"]
    partial_zip, partial_record = run / f"{fit.label}_partial.zip", run / f"{fit.label}_partial.json"
    env = SubprocVecEnv([partial(ChannelCycler, config, learn=fit.learn, frozen=frozen, rank=rank, n_envs=n_envs,
                                 reduction_probability=fit.reduction_probability) for rank in range(n_envs)],
                        start_method="spawn")
    try:
        if partial_record.exists():
            # Resume after an interruption: policy/optimizer continuation from the last saved chunk,
            # next unused season per worker; the incomplete seasons of the interrupted chunk are skipped.
            progress = json.loads(partial_record.read_text())
            assert progress["checkpoint_sha256"] == sha256(partial_zip), "partial checkpoint changed"
            model = MaskablePPO.load(partial_zip, env=env, device="cpu")
            for rank, cursor in enumerate(progress["season_cursors"]):
                env.env_method("set_season_cursor", cursor, indices=[rank])
            print("RESUME", fit.label, model.num_timesteps, flush=True)
        else:
            progress = {"seconds": 0.0, "completed_train_seasons": 0, "chunks": 0}
            model = MaskablePPO("MlpPolicy", env, device="cpu", seed=fit.seed, gamma=cfg["gamma"],
                                gae_lambda=cfg["gae_lambda"], n_steps=cfg["n_steps"], batch_size=cfg["batch_size"],
                                n_epochs=cfg["n_epochs"],
                                policy_kwargs={"net_arch": {"pi": cfg["policy_layers"], "vf": cfg["value_layers"]}})
            with torch.no_grad():
                offset = 0
                for channel in fit.learn:
                    count, mass = SIZES[channel], cfg["sparse_nonzero_mass"][NAMES[channel]]
                    model.policy.action_net.weight[offset:offset + count].zero_()
                    model.policy.action_net.bias[offset:offset + count].copy_(
                        torch.tensor([1 - mass] + [mass / (count - 1)] * (count - 1)).log())
                    offset += count
        chunk = cfg["checkpoint_steps"]
        while model.num_timesteps < fit.steps:
            audit, start = Audit(), time.perf_counter()
            model.learn(total_timesteps=min(chunk, fit.steps - model.num_timesteps), reset_num_timesteps=False,
                        callback=audit)
            assert audit.truncations == 0 and all(torch.isfinite(p).all() for p in model.policy.parameters())
            model.save(partial_zip)
            progress.update(steps=model.num_timesteps, season_cursors=env.env_method("season_cursor"),
                            checkpoint_sha256=sha256(partial_zip), seconds=progress["seconds"] + time.perf_counter() - start,
                            completed_train_seasons=progress["completed_train_seasons"] + len(audit.returns),
                            chunks=progress["chunks"] + 1)
            write_json(partial_record, progress)
            print("CHUNK", fit.label, model.num_timesteps, flush=True)
        assert model.num_timesteps == fit.steps
        model.save(path)
        write_json(record, {**asdict(fit), "checkpoint_sha256": sha256(path), "seconds": progress["seconds"],
                            "completed_train_seasons": progress["completed_train_seasons"], "chunks": progress["chunks"],
                            "n_envs": n_envs,
                            "frozen_checkpoint_sha256": {label: sha256(checkpoint(run, label)) for label, _ in fit.frozen}})
    finally:
        env.close()


def build_policies(run, config, plan):
    deterministic = config["training"]["deterministic_policy"]
    rule = RulePolicy.from_config(config)
    policies = {("0", None): rule, ("b0p", None): ReductionResponseRule.from_config(config)}
    fits = {fit.label: fit for fit in plan}
    load = lambda label, channels: FrozenChannels(MaskablePPO.load(checkpoint(run, label), device="cpu"), channels, deterministic)
    for fit in plan:
        parts = tuple(load(label, channels) for label, channels in fit.frozen) + (load(fit.label, fit.learn),)
        assert all(label in fits for label, _ in fit.frozen)
        policies[f"{fit.regime}{fit.policy}", fit.seed] = CompositePolicy(rule, parts)
    return policies


def evaluate_seasons(payload):
    run, config, plan, season_ids, seeds, table_rows = payload
    torch.set_num_threads(1)
    os.environ["MARS_RUN_DIR"] = str(run)
    rules, price = ResourceRules.from_config(config), grain_price(config)
    conditions, policies = evaluation_conditions(config), build_policies(run, config, plan)
    cells, beta, rows = table_cells(conditions, table_rows), config["scenarios"]["evaluation_beta"], []
    parameters, noise = pest_settings(config)
    for season_id in season_ids:
        base, weather = generate_season(config, split="validation", season_id=season_id), {}
        for row_name, column, policy_id, condition in cells:
            season = base.with_condition(beta=beta, shock=conditions[condition])
            for seed in ((None,) if policy_id in ("0", "b0p") else seeds):
                env = ExperimentalPestEnv(season=season, parameters=parameters, noise_std=noise, rules=rules, grain_price=price,
                                          backend_factory=partial(LegacyProcessBackend, mode="experimental_pest", season=season,
                                                                  parameters=parameters, noise_std=noise))
                try:
                    record = evaluate_episode(env, policies[policy_id, seed], season, rules, price,
                                              reset_options={}, record_decision_context=True)
                finally:
                    env.close()
                result = record["episode_result"]
                trace = {day["yrdoy"]: day["weather"] for day in record["daily_tape"]}
                assert all(weather[day] == trace[day] for day in weather.keys() & trace.keys())
                weather.update(trace)
                stage_water, stage_sprays, spray_days = {}, {}, []
                for day in record["daily_tape"]:
                    stage_water[day["istage"]] = stage_water.get(day["istage"], 0) + rules.water_grid[day["action_indices"][0]]
                    if day["action_indices"][2]:
                        stage_sprays[day["istage"]] = stage_sprays.get(day["istage"], 0) + 1
                        spray_days.append(day["decision_day"])
                cut_day = result["water_cut_day"]
                rows.append({"row": row_name, "column": column, "policy": policy_id, "seed": seed, "condition": condition,
                             "season_id": season_id, **result, "stage_water_mm": stage_water,
                             "stage_sprays": stage_sprays, "spray_days": spray_days,
                             "sprays_before_cut": sum(d < cut_day for d in spray_days) if cut_day is not None else None,
                             "sprays_before_v7": sum(day["action_indices"][2] and day["vstage"] < 7 for day in record["daily_tape"]),
                             "transpiration_mm": float(sum(day["ep"] for day in record["daily_tape"])),
                             "resource_violations": resource_violations(result, result["water_cut_mm"], rules, beta)})
        print("EVALUATED", season_id, flush=True)
    return rows


def evaluate_all(run, config, plan, seasons, seeds, table_rows=ROWS):
    workers = config["scenarios"]["evaluation_workers"]
    groups = [(run, config, plan, seasons[index::workers], seeds, tuple(table_rows))
              for index in range(workers) if seasons[index::workers]]
    rows = []
    with ProcessPoolExecutor(max_workers=workers, mp_context=get_context("fork")) as pool:
        for part in pool.map(evaluate_seasons, groups):
            rows.extend(part)
    return rows


def assemble(rows, seeds, seasons):
    """(row, column, condition) -> seed x season net returns; rule policies repeat across seeds."""
    position, out = {season: index for index, season in enumerate(seasons)}, {}
    for item in rows:
        key = (item["row"], item["column"], item["condition"])
        matrix = out.setdefault(key, np.full((len(seeds), len(seasons)), np.nan))
        targets = range(len(seeds)) if item["seed"] is None else (seeds.index(item["seed"]),)
        for target in targets:
            matrix[target, position[item["season_id"]]] = item["net_return"]
    assert all(np.isfinite(matrix).all() for matrix in out.values())
    return out


def auxiliary(rows):
    groups = {}
    for item in rows:
        groups.setdefault(f"{item['row']}|{item['column']}", []).append(item)
    summary = {}
    for name, items in groups.items():
        stages = sorted({stage for item in items for stage in item["stage_water_mm"]})
        summary[name] = {
            **{key: float(np.mean([item[key] for item in items])) for key in
               ("harvested_grain_kg_ha", "water_mm", "nitrogen_kg_ha", "sprays")},
            "failure_rate": float(np.mean([item["reason"] == "crop_failure" for item in items])),
            "resource_violations": int(sum(item["resource_violations"] for item in items)),
            "mean_water_mm_by_stage": {str(stage): float(np.mean([item["stage_water_mm"].get(stage, 0) for item in items]))
                                       for stage in stages},
            # Policy interpretation: when sprays happen relative to growth and to the reduction, and the water path.
            "mean_sprays_by_stage": {str(stage): float(np.mean([item["stage_sprays"].get(stage, 0) for item in items]))
                                     for stage in sorted({s for item in items for s in item["stage_sprays"]})},
            "mean_sprays_before_v7": float(np.mean([item["sprays_before_v7"] for item in items])),
            "mean_transpiration_mm": float(np.mean([item["transpiration_mm"] for item in items])),
            "by_condition": {condition: {
                "sprays": float(np.mean([i["sprays"] for i in group])),
                "sprays_before_cut": (float(np.mean([i["sprays_before_cut"] for i in group]))
                                      if group[0]["sprays_before_cut"] is not None else None),
                "water_mm": float(np.mean([i["water_mm"] for i in group])),
                "transpiration_mm": float(np.mean([i["transpiration_mm"] for i in group]))}
                for condition in sorted({i["condition"] for i in items})
                for group in [[i for i in items if i["condition"] == condition]]}}
    cuts = {}
    for item in rows:
        if item["condition"] != "none":
            cuts.setdefault(item["condition"], []).append(item["water_cut_mm"])
    return {"by_cell": summary, "actual_cut_mm_by_condition": {name: float(np.mean(values)) for name, values in cuts.items()}}


def checks(rows, returns, conditions):
    expected = {cell[:2] for cell in table_cells(conditions)}
    a0, b0 = returns["a", "0", "none"], returns["b_none", "0", "none"]
    days, mismatched = {}, 0
    for item in rows:
        if item["condition"] != "none":
            days.setdefault((item["season_id"], item["condition"]), set()).add(item["water_cut_day"])
            mismatched += item["water_cut_day"] != conditions[item["condition"]].day
    return {"table_cells_expected": len(expected), "table_cells_generated": len({key[:2] for key in returns}),
            "all_cells_generated": {key[:2] for key in returns} == expected,
            "distinct_policies": sorted({item["policy"] for item in rows}),
            "a0_equals_b_none_b0": bool(np.array_equal(a0, b0)),
            "max_abs_a0_minus_b_none_b0": float(np.abs(a0 - b0).max()),
            "reduction_day_shared_across_policies": all(len(value) == 1 for value in days.values()),
            "reduction_day_mismatches_with_condition": int(mismatched),
            "resource_violations": int(sum(item["resource_violations"] for item in rows))}


def markdown(table, aux):
    columns = ("0", "1", "2", "3", "4", "b0p")
    lines = ["| 행 | " + " | ".join(columns) + " |", "|---|" + "---:|" * len(columns)]
    for row in ("a", "a_cut", "b_none", "b_cut"):
        cells = [f"{table[row, c]['mean']:.1f} / {table[row, c]['lower_10_mean']:.1f}" if (row, c) in table else "" for c in columns]
        lines.append(f"| {row} | " + " | ".join(cells) + " |")
    lines += ["", "각 칸: 평균 순수익 / 하위 10% 평균 (USD/ha)", "", "실감축량(mm): " +
              ", ".join(f"{k}={v:.1f}" for k, v in sorted(aux["actual_cut_mm_by_condition"].items()))]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, help="Steps per sequential fit; default is the configured value")
    parser.add_argument("--seeds", type=int, nargs="+")
    parser.add_argument("--seasons", type=int)
    parser.add_argument("--first-season", type=int, default=2000)
    parser.add_argument("--bootstrap", type=int)
    parser.add_argument("--resume", type=Path)
    args = parser.parse_args()
    config_path = args.resume / "config.yaml" if args.resume else ROOT / "configs/proposal_v2.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert config["scenarios"]["timing"] == "calendar_day"
    seeds = args.seeds or config["training"]["seeds"]
    count = args.seasons or config["scenarios"]["evaluation_seasons_per_condition"]
    seasons = list(range(args.first_season, args.first_season + count))
    if (args.steps or config["training"]["timesteps_per_seed"]) % (config["training"]["n_steps"] * config["training"]["n_envs"]):
        parser.error("Steps must be whole rollouts")
    run = args.resume or new_run(ROOT, "policy_comparison", config_source=config_path)
    os.environ["MARS_RUN_DIR"] = str(run)
    print("RUN_DIR=" + str(run), flush=True)
    torch.set_num_threads(1)
    plan = training_plan(config, steps=args.steps, seeds=seeds)
    write_json(run / "design.json", {"fits": [asdict(fit) for fit in plan], "seeds": seeds, "seasons": seasons,
                                     "split": "validation", "config_sha256": sha256(run / "config.yaml"),
                                     "conditions": {k: None if v is None else vars(v) for k, v in evaluation_conditions(config).items()},
                                     "final_test_split_used": False, "research_ready": False})
    for fit in plan:
        print("TRAIN", fit.label, fit.steps, flush=True)
        train(run, config, fit)
    start = time.perf_counter()
    rows = evaluate_all(run, config, plan, seasons, seeds)
    write_json(run / "episodes.json", rows)
    returns, conditions = assemble(rows, seeds, seasons), evaluation_conditions(config)
    table, aux = results_table(returns), auxiliary(rows)
    scenario = config["scenarios"]
    statistics = inference(contrasts(returns, list(scenario["evaluation_days"]), scenario["evaluation_reductions"]),
                           replicates=args.bootstrap or scenario["bootstrap_replicates"])
    report = {"checks": checks(rows, returns, conditions), "episodes": len(rows), "evaluation_seconds": time.perf_counter() - start,
              "table": {f"{row}|{column}": value for (row, column), value in table.items()}, "auxiliary": aux,
              "contrasts": statistics, "split": "validation", "final_test_split_used": False, "research_ready": False}
    # Sensitivity re-evaluations: the first seasons of the main table, without the a_cut row (decision_project.md 5).
    sensitivity_seasons = seasons[:min(len(seasons), scenario["sensitivity_seasons_per_condition"])]
    sensitivity_rows = tuple(scenario["sensitivity_rows"])
    report["sensitivity_design"] = {"seasons": len(sensitivity_seasons), "rows": list(sensitivity_rows)}
    # The same trained policies at other seasonal supplies; no retraining.
    supply_violations = 0
    for supply in scenario["evaluation_supply_mm"]:
        print("SUPPLY", supply, flush=True)
        supply_rows = evaluate_all(run, supply_variant(config, supply), plan, sensitivity_seasons, seeds, sensitivity_rows)
        supply_returns = assemble(supply_rows, seeds, sensitivity_seasons)
        violations = int(sum(item["resource_violations"] for item in supply_rows))
        supply_violations += violations
        supply_table = results_table(supply_returns)
        write_json(run / f"water_supply_{int(supply)}.json", {
            "supply_mm": supply, "episodes": len(supply_rows), "resource_violations": violations,
            "table": {f"{row}|{column}": value for (row, column), value in supply_table.items()},
            "auxiliary": auxiliary(supply_rows),
            "contrasts": inference(contrasts(supply_returns, list(scenario["evaluation_days"]), scenario["evaluation_reductions"]),
                                   replicates=args.bootstrap or scenario["bootstrap_replicates"]),
            "retrained": False, "split": "validation", "final_test_split_used": False})
    report["supply_resource_violations"] = supply_violations
    # The same trained policies with a noisier pest survey; no retraining.
    for noise in scenario.get("evaluation_survey_noise_std", []):
        print("SURVEY_NOISE", noise, flush=True)
        noise_rows = evaluate_all(run, survey_noise_variant(config, noise), plan, sensitivity_seasons, seeds, sensitivity_rows)
        noise_returns = assemble(noise_rows, seeds, sensitivity_seasons)
        violations = int(sum(item["resource_violations"] for item in noise_rows))
        supply_violations += violations
        write_json(run / f"survey_noise_{noise}.json", {
            "survey_noise_std": noise, "episodes": len(noise_rows), "resource_violations": violations,
            "table": {f"{row}|{column}": value for (row, column), value in results_table(noise_returns).items()},
            "auxiliary": auxiliary(noise_rows),
            "contrasts": inference(contrasts(noise_returns, list(scenario["evaluation_days"]), scenario["evaluation_reductions"]),
                                   replicates=args.bootstrap or scenario["bootstrap_replicates"]),
            "retrained": False, "split": "validation", "final_test_split_used": False})
    report["sensitivity_resource_violations"] = supply_violations
    report["passed"] = all((report["checks"]["all_cells_generated"], report["checks"]["a0_equals_b_none_b0"],
                            report["checks"]["reduction_day_shared_across_policies"],
                            report["checks"]["reduction_day_mismatches_with_condition"] == 0,
                            report["checks"]["resource_violations"] == 0, supply_violations == 0))
    write_json(run / "verification.json", report)
    (run / "results_table.md").write_text(markdown(table, aux), encoding="utf-8")
    print(json.dumps(report["checks"], ensure_ascii=False), flush=True)
    print(markdown(table, aux), flush=True)


if __name__ == "__main__":
    main()
