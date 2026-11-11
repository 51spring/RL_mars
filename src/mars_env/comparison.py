"""Design of the policy comparison: fits, table cells, contrasts and cross-bootstrap inference."""
import copy
from dataclasses import dataclass
import math

import numpy as np

CHANNELS = {"water": (0,), "nitrogen": (1,), "spray": (2,), "joint": (0, 1, 2)}
EPS = 1e-6


@dataclass(frozen=True)
class Fit:
    label: str
    regime: str
    policy: int
    seed: int
    learn: tuple
    frozen: tuple  # (label of an earlier fit, channels it answers for)
    steps: int
    reduction_probability: float | None  # None keeps the configured training probability


def training_plan(config, *, steps=None, seeds=None):
    """Chains stay within a regime and a seed number; policy 4 costs policies 1+2+3."""
    training = config["training"]
    steps = training["timesteps_per_seed"] if steps is None else steps
    plan = []
    for regime, probability in (("a", 0.0), ("b", None)):
        for seed in (training["seeds"] if seeds is None else seeds):
            first, second = f"{regime}1_s{seed}", f"{regime}2_s{seed}"
            water, nitrogen = (first, CHANNELS["water"]), (second, CHANNELS["nitrogen"])
            for policy, learn, frozen, cost in ((1, "water", (), steps), (2, "nitrogen", (water,), steps),
                                                (3, "spray", (water, nitrogen), steps), (4, "joint", (), 3 * steps)):
                plan.append(Fit(f"{regime}{policy}_s{seed}", regime, policy, seed, CHANNELS[learn], frozen, cost, probability))
    return plan


def supply_variant(config, supply_mm):
    """Same trained policies on another seasonal supply (water is limited by the supply alone)."""
    variant = copy.deepcopy(config)
    variant["environment"]["initial_water_mm"] = float(supply_mm)
    return variant


def survey_noise_variant(config, noise_std):
    """Same trained policies with a noisier pest survey; the season noise tapes are only rescaled."""
    variant = copy.deepcopy(config)
    variant["pest"]["survey_noise_std"] = float(noise_std)
    return variant


ROWS = ("a", "b_none", "b_cut", "a_cut")


def table_cells(conditions, rows=ROWS):
    """(row, column, policy id, condition): a, b-none, b-cut x policies 0-4, b0', and a1-a4 under cuts.

    ``rows`` keeps only the listed table rows (sensitivity re-evaluations skip a_cut).
    """
    if not set(rows) <= set(ROWS):
        raise ValueError(f"Unknown table rows: {sorted(set(rows) - set(ROWS))}")
    cuts = [name for name in conditions if name != "none"]
    cells = []
    for column in range(5):
        for row, regime in (("a", "a"), ("b_none", "b")):
            cells.append((row, str(column), "0" if column == 0 else f"{regime}{column}", "none"))
        cells.extend(("b_cut", str(column), "0" if column == 0 else f"b{column}", cut) for cut in cuts)
    cells.extend(("b_cut", "b0p", "b0p", cut) for cut in cuts)
    cells.extend(("a_cut", str(column), f"a{column}", cut) for column in range(1, 5) for cut in cuts)
    return [cell for cell in cells if cell[0] in rows]


def lower_tail_mean(values, fraction=0.10):
    ordered = np.sort(np.asarray(values, dtype=float))
    return float(ordered[:max(1, math.ceil(fraction * ordered.size))].mean())


def resource_violations(result, water_cut_mm, rules, beta):
    """Independent recount of the season totals against every resource limit."""
    water, nitrogen, sprays = result["water_mm"], result["nitrogen_kg_ha"], result["sprays"]
    return sum((water > rules.initial_water - water_cut_mm + EPS,
                nitrogen * rules.nitrogen_price > beta * rules.nitrogen_budget + EPS,
                sprays * rules.spray_price > beta * rules.spray_budget + EPS))


def cut_conditions(returns):
    return sorted({condition for (row, _, condition) in returns if row == "b_cut"})


def row_matrix(returns, row, column):
    """Seed x season matrix; the reduction row averages its conditions season by season."""
    if row not in ("a_cut", "b_cut"):
        return returns[row, column, "none"]
    return np.mean([returns[row, column, condition] for condition in cut_conditions(returns)], axis=0)


def results_table(returns):
    """Mean and lower-10% mean per cell; a reduction cell averages its nine condition values."""
    table = {}
    for row, column in sorted({key[:2] for key in returns}):
        conditions = [key[2] for key in returns if key[:2] == (row, column)]
        means, tails = [], []
        for condition in conditions:
            matrix = returns[row, column, condition]
            means.append(float(matrix.mean()))
            tails.append(float(np.mean([lower_tail_mean(values) for values in matrix])))
        table[row, column] = {"mean": float(np.mean(means)), "lower_10_mean": float(np.mean(tails)),
                              "conditions": {c: {"mean": m, "lower_10_mean": t}
                                             for c, m, t in zip(conditions, means, tails)}}
    return table


def contrasts(returns, timings, rates):
    """{name: (test family, seed x season matrix, alternative)}; statistics are matrix means.

    C1, C2 and G(0) use the b policies only: G = b4 - b1, G(0) on the no-reduction row.
    """
    def R(row, column):
        return row_matrix(returns, row, str(column))

    def effect(high, low):
        return (R("b_cut", high) - R("b_cut", low)) - (R("b_none", high) - R("b_none", low))

    out = {}
    for policy in (1, 2, 3, 4):  # Policy 0 is the same rule on the same seasons: identically zero.
        out[f"readiness_cost_{policy}"] = ("readiness_cost", R("a", policy) - R("b_none", policy), "two-sided")
    for policy in range(5):
        out[f"reduction_loss_{policy}"] = ("reduction_loss", R("b_none", policy) - R("b_cut", policy), "two-sided")
    out["irrigation_learning"] = ("effects", effect(1, 0), "two-sided")
    out["sequential_optimization"] = ("effects", effect(3, 1), "two-sided")
    out["joint_management"] = ("effects", effect(4, 3), "two-sided")
    out["spray_value"] = ("effects", effect(3, 2), "two-sided")
    out["rule_response"] = ("effects", R("b_cut", 1) - R("b_cut", "b0p"), "two-sided")
    if any(key[0] == "a_cut" for key in returns):  # absent in sensitivity re-evaluations
        for policy in (1, 2, 3, 4):
            out[f"preparedness_gain_{policy}"] = ("preparedness_gain", R("b_cut", policy) - R("a_cut", policy), "two-sided")
    g0 = R("b_none", 4) - R("b_none", 1)
    D = {}
    for timing in timings:
        for rate in rates:
            name = f"{timing}_{round(100 * rate)}"
            D[timing, rate] = returns["b_cut", "4", name] - returns["b_cut", "1", name] - g0
            out[f"delta_delta_{name}"] = ("conditions", D[timing, rate], "two-sided")
    high, low = max(rates), min(rates)
    out["C1"] = ("hypotheses", np.mean([(D[t, high] - D[t, low]) / (high - low) for t in timings], axis=0), "greater")
    out["C2"] = ("hypotheses", np.mean([D[timings[0], r] - D[timings[-1], r] for r in rates], axis=0), "greater")
    return out


def cross_bootstrap(matrices, *, replicates=10000, seed=0, chunk=500):
    """Resample seed rows and season columns independently, jointly for all contrasts."""
    n_seeds, n_seasons = next(iter(matrices.values())).shape
    rng = np.random.default_rng(seed)
    draws = {name: [] for name in matrices}
    for start in range(0, replicates, chunk):
        size = min(chunk, replicates - start)
        rows = rng.multinomial(n_seeds, np.full(n_seeds, 1 / n_seeds), size=size)
        columns = rng.multinomial(n_seasons, np.full(n_seasons, 1 / n_seasons), size=size)
        for name, matrix in matrices.items():
            draws[name].append(((rows @ matrix) * columns).sum(axis=1) / (n_seeds * n_seasons))
    return {name: np.concatenate(values) for name, values in draws.items()}


def holm(p_values):
    """Holm step-down adjusted p-values for {name: p}."""
    adjusted, running = {}, 0.0
    ordered = sorted(p_values, key=p_values.get)
    for index, name in enumerate(ordered):
        running = max(running, min(1.0, (len(ordered) - index) * p_values[name]))
        adjusted[name] = running
    return adjusted


def inference(contrast_set, *, replicates=10000, seed=0):
    """Percentile intervals, null-centred bootstrap p-values and Holm by test family."""
    draws = cross_bootstrap({name: value[1] for name, value in contrast_set.items()}, replicates=replicates, seed=seed)
    results = {}
    for name, (family, matrix, alternative) in contrast_set.items():
        estimate, centred = float(matrix.mean()), draws[name] - matrix.mean()
        exceed = centred >= estimate if alternative == "greater" else np.abs(centred) >= abs(estimate)
        results[name] = {"family": family, "alternative": alternative, "estimate_usd_ha": estimate,
                         "ci95": [float(x) for x in np.percentile(draws[name], (2.5, 97.5))],
                         "p": float((1 + exceed.sum()) / (replicates + 1))}
    for family in {value["family"] for value in results.values()}:
        members = {name: value["p"] for name, value in results.items() if value["family"] == family}
        for name, adjusted in holm(members).items():
            results[name]["p_holm"] = adjusted
    return results
