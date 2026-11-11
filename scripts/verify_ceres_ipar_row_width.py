"""Compare native growth IPAR across two UFGA row widths with no leaf damage."""
import argparse
import hashlib
import json
import math
from statistics import fmean

from verify_ceres_ipar import ROOT, SEED, check_growth, season
from mars_env.artifacts import new_run, sha256, write_json
from mars_env.input_metadata import canonical_ufga_metadata


def planting_columns(template):
    lines = template.splitlines(keepends=True)
    index, = [i for i, line in enumerate(lines) if line.startswith("@P PDATE")]
    header = lines[index]
    end = header.index("PLRS") + len("PLRS")
    assert header[end - 6:end].strip() == "PLRS"
    assert lines[index + 1][:2] == " 1" and not lines[index + 2].strip()
    return lines, index + 1, end - 6, end


def with_width(template, width):
    lines, index, start, end = planting_columns(template)
    row = lines[index]
    int(row[start:end])
    lines[index] = row[:start] + f"{width:6d}" + row[end:]
    return "".join(lines)


def field_transform(folder, width):
    def transform(template):
        changed = with_width(canonical_ufga_metadata(template), width)
        (folder / "fileX.MZX").write_text(changed, encoding="ascii")
        return changed
    return transform


def fraction(extinction, lai):
    return -math.expm1(-extinction * lai)


def pair_day(narrow, wide):
    assert narrow["date"] == wide["date"]
    assert all(narrow[key] == wide[key] for key in ("pop", "srad", "par"))
    k_narrow, k_wide = narrow["lifac"], wide["lifac"]
    lai_narrow, lai_wide = narrow["lai"], wide["lai"]
    narrow_native = fraction(k_narrow, lai_narrow)
    wide_native = fraction(k_wide, lai_wide)
    narrow_at_wide_lai = fraction(k_narrow, lai_wide)
    wide_at_narrow_lai = fraction(k_wide, lai_narrow)
    # Average the two orders of changing width and LAI.
    direct = ((narrow_native - wide_at_narrow_lai) + (narrow_at_wide_lai - wide_native)) / 2
    lai_component = ((narrow_native - narrow_at_wide_lai) + (wide_at_narrow_lai - wide_native)) / 2
    total = narrow_native - wide_native
    assert math.isclose(direct + lai_component, total, abs_tol=1e-15)
    assert direct >= 0
    return {
        "date": narrow["date"], "lai_38": lai_narrow, "lai_76": lai_wide,
        "fipar_38": narrow_native, "fipar_76": wide_native,
        "direct_width_pp": 100 * direct, "lai_component_pp": 100 * lai_component,
        "total_pp": 100 * total, "energy_delta_mj_plant_day": narrow["energy"] - wide["energy"],
    }


def compare_seed(run, seed):
    growth, cases, weather = {}, {}, {}
    for width in (38, 76):
        folder = run / f"width_{width}"
        trace, outcome, samples = season(
            folder, True, 0, filex_transform=field_transform(folder, width), seed=seed,
        )
        growth[width], stats = check_growth(trace, outcome, samples)
        assert all(row["row_cm"] == width for row in samples)
        assert all(row["fraction"] == 0 for row in trace)
        weather[width] = {
            row["after"]["yrdoy"]: [row["after"][field] for field in ("rain", "srad", "tmin", "tmax")]
            for row in trace
        }
        cases[width] = {
            **stats, "planting": int(outcome.summary["PDAT"]), "population": samples[0]["pop"],
            "irrigation_mm": outcome.summary["IRCM"], "nitrogen_kg_ha": outcome.summary["NICM"],
            "grain_kg_ha": outcome.harvested_grain_kg_ha,
            "filex_sha256": sha256(folder / "fileX.MZX"),
        }
        print(f"seed={seed} width={width} grain_kg_ha={cases[width]['grain_kg_ha']}", flush=True)

    files = [(run / f"width_{width}" / "fileX.MZX").read_text() for width in (38, 76)]
    assert with_width(files[0], 76) == files[1] and files[0] != files[1]
    for field in ("planting", "population", "irrigation_mm", "nitrogen_kg_ha"):
        assert cases[38][field] == cases[76][field]
    weather_dates = weather[38].keys() & weather[76].keys()
    assert weather_dates and all(weather[38][day] == weather[76][day] for day in weather_dates)
    weather_prefix = sorted(weather_dates)[:30]
    assert len(weather_prefix) == 30
    weather_prefix_hash = hashlib.sha256(
        json.dumps([(day, weather[38][day]) for day in weather_prefix]).encode("utf-8")
    ).hexdigest()
    shared = sorted(growth[38].keys() & growth[76].keys())
    pairs = [pair_day(growth[38][day], growth[76][day]) for day in shared]
    assert pairs
    keys = ("direct_width_pp", "lai_component_pp", "total_pp", "energy_delta_mj_plant_day")
    write_json(run / "daily_pairs.json", pairs)
    result = {
        "passed": True, "seasons": 2, "seed": seed, "cases": cases,
        "filex_only_plrs_differs": True, "identical_weather_dates": len(weather_dates),
        "common_growth_dates": len(pairs),
        "first_30_common_weather_dates": weather_prefix,
        "first_30_common_weather_sha256": weather_prefix_hash,
        "harvest_delta_kg_ha": cases[38]["grain_kg_ha"] - cases[76]["grain_kg_ha"],
        "unpaired_growth_dates": {width: sorted(growth[width].keys() - set(shared)) for width in growth},
        "means": {key: fmean(row[key] for row in pairs) for key in keys},
        "ranges": {key: [min(row[key] for row in pairs), max(row[key] for row in pairs)] for key in keys},
        "max_abs_lai_difference": max(abs(row["lai_38"] - row["lai_76"]) for row in pairs),
        "summed_energy_delta_mj_plant_common_days": math.fsum(row["energy_delta_mj_plant_day"] for row in pairs),
        "diagnostic_only": True, "research_ready": False, "main_training_allowed": False,
    }
    write_json(run / "verification.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, nargs="+", default=[SEED])
    seeds = parser.parse_args().seeds
    if len(set(seeds)) != len(seeds) or any(seed <= 0 for seed in seeds):
        parser.error("seeds must be unique positive integers")

    multiple = len(seeds) > 1
    purpose = "native_ceres_ipar_row_width_multiseed" if multiple else "native_ceres_ipar_row_width"
    run = new_run(ROOT, purpose)
    print(f"RUN_DIR={run}", flush=True)
    current_seed = None
    comparisons = {}
    try:
        for current_seed in seeds:
            folder = run / f"seed_{current_seed}" if multiple else run
            folder.mkdir(exist_ok=True)
            comparisons[current_seed] = compare_seed(folder, current_seed)
        if not multiple:
            return

        results = list(comparisons.values())
        assert all(row["first_30_common_weather_dates"] == results[0]["first_30_common_weather_dates"]
                   for row in results)
        assert len({row["first_30_common_weather_sha256"] for row in results}) == len(seeds)
        by_seed = [
            {"seed": row["seed"], "common_growth_dates": row["common_growth_dates"],
             **row["means"], "harvest_delta_kg_ha": row["harvest_delta_kg_ha"]}
            for row in results
        ]
        metrics = ("total_pp", "direct_width_pp", "lai_component_pp", "harvest_delta_kg_ha")
        write_json(run / "verification.json", {
            "passed": True, "seeds": seeds, "seasons": 2 * len(seeds),
            "distinct_weather_prefixes": len(seeds), "by_seed": by_seed,
            "ranges_across_seed_pairs": {
                name: [min(row[name] for row in by_seed), max(row[name] for row in by_seed)]
                for name in metrics
            },
            "diagnostic_only": True, "research_ready": False, "main_training_allowed": False,
        })
    except BaseException as exc:
        write_json(run / "failure.json", {
            "passed": False, "error": repr(exc), "last_seed_attempted": current_seed,
            "completed_seeds": list(comparisons),
        })
        raise


if __name__ == "__main__":
    main()
