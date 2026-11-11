"""Reconcile preserved BRPI0202 inputs against the published trial and ESALQ weather."""

import argparse
from calendar import monthrange
from datetime import date
from hashlib import sha256
import json
from math import sqrt
from pathlib import Path
import re
from statistics import mean

import xlrd


SOURCE_RUN = "20261109T045443Z_environment_validation_sweep_673f708f"
WEATHER_COLUMNS = {"SRAD": 15, "TMAX": 4, "TMIN": 10, "RAIN": 14}
PUBLISHED_COEFFICIENTS = {
    "IB0171": (196.0, 0.5, 758.0, 990, 5.20, 46.6),
    "IB0172": (240.0, 0.5, 747.8, 990, 5.00, 43.4),
    "IB0173": (263.0, 0.5, 842.0, 940, 4.40, 44.1),
    "IB0174": (232.0, 0.5, 766.0, 990, 5.15, 42.3),
}
SOIL_COLUMNS = ("SLLL", "SDUL", "SSAT", "SBDM", "SLOC", "SLCL", "SLSI")
PUBLISHED_SOIL = {
    "BRPI020001": {20: (0.17, 0.28, 0.45, 0.90, 1.40, 60, 15),
                   40: (0.18, 0.29, 0.45, 0.91, 1.10, 61, 18)},
    "BRPI020002": {20: (0.28, 0.34, 0.53, 1.23, 1.47, 65, 15),
                   40: (0.27, 0.33, 0.53, 1.13, 1.11, 65, 15)},
}


def esalq_weather(path):
    sheet = xlrd.open_workbook(path).sheet_by_name("Plan1")
    records = {}
    headers = [i for i, value in enumerate(sheet.col_values(0)) if value == "DIA"]
    if len(headers) != 12:
        raise ValueError("Expected 12 ESALQ monthly day headers")
    for month, header in enumerate(headers, start=1):
        for day in range(1, monthrange(2002, month)[1] + 1):
            row = sheet.row(header + 2 + day)
            if row[0].value != day:
                raise ValueError(f"Expected ESALQ date 2002-{month:02}-{day:02}")
            key = date(2002, month, day).timetuple().tm_yday
            records[key] = {
                name: row[index].value if row[index].ctype == xlrd.XL_CELL_NUMBER else None
                for name, index in WEATHER_COLUMNS.items()
            }
    return records


def compare_weather(path, observations):
    records = {}
    for match in re.finditer(r"^02(\d{3})[ \t]+([^\r\n]+)", path.read_text(), re.M):
        day = int(match[1])
        if day in records:
            raise ValueError(f"Duplicate DSSAT weather day {day}")
        records[day] = dict(zip(WEATHER_COLUMNS, map(float, match[2].split()), strict=True))
    if records.keys() != observations.keys() or set(records) != set(range(1, 366)):
        raise ValueError("Weather files must both contain all 365 dates in 2002")

    result = {}
    for name in WEATHER_COLUMNS:
        missing = []
        mismatches = []
        deltas = []
        for day, station in observations.items():
            observed = station[name]
            simulated_input = records[day][name]
            if observed is None or observed <= -99 or simulated_input <= -99:
                missing.append({"day_of_year": day, "esalq": observed, "dssat": simulated_input})
                continue
            delta = round(simulated_input - observed, 6)
            deltas.append(abs(delta))
            if abs(delta) > 0.05:
                mismatches.append({"day_of_year": day, "esalq": observed, "dssat": simulated_input})
        result[name] = {
            "compared_days": len(deltas),
            "max_absolute_difference": max(deltas),
            "missing_days": missing,
            "differences_over_half_input_unit": mismatches,
            "differences_during_replay_days_60_to_215": sum(
                60 <= item["day_of_year"] <= 215 for item in mismatches
            ),
            "differences_over_half_integer_unit_during_replay": [
                item for item in mismatches if 60 <= item["day_of_year"] <= 215
                and abs(round(item["esalq"] - item["dssat"], 6)) > 0.5
            ],
        }
    return result


def compare_soil(path):
    profiles = {}
    current = None
    for line in path.read_text(encoding="latin-1").splitlines():
        if line.startswith("*"):
            current = line.split()[0].removeprefix("*")
        values = line.split()
        if current in PUBLISHED_SOIL and len(values) == 17 and values[0].isdigit():
            depth = int(values[0])
            profiles.setdefault(current, {})[depth] = tuple(
                float(values[index]) for index in (2, 3, 4, 7, 8, 9, 10)
            )
    return {
        profile: {
            "package_only_layer_bottoms_cm": sorted(profiles[profile].keys() - layers.keys()),
            "published_layer_differences": {
                depth: {
                    name: {"paper": reference, "dssat": package}
                    for name, reference, package in zip(
                        SOIL_COLUMNS, values, profiles[profile][depth], strict=True
                    ) if reference != package
                } for depth, values in layers.items()
            },
        } for profile, layers in PUBLISHED_SOIL.items()
    }


def audit(run, weather_path):
    official = run / "official_maize"
    source_paths = [weather_path, run / "brpi_replay_verification.json",
                    run / "brpi2001_published_MZCER048.CUL"]
    source_paths.extend(official / name for name in ("BRPI0201.WTH", "BR.SOL", "BRPI0202.MZA", "BRPI0202.MZX"))
    replay = json.loads(source_paths[1].read_text(encoding="utf-8-sig"))
    coefficients = {}
    for line in source_paths[2].read_text(encoding="latin-1").splitlines():
        code = line[:6]
        if code in PUBLISHED_COEFFICIENTS:
            coefficients[code] = tuple(map(float, line[36:72].split()))
            if line[30:36].strip() != "IB0001":
                raise ValueError(f"Unexpected ecotype for {code}")
    if coefficients != PUBLISHED_COEFFICIENTS:
        raise ValueError("Preserved cultivar card disagrees with Soler et al. Table 2")

    observations = {}
    for line in source_paths[-2].read_text(encoding="latin-1").splitlines():
        fields = line.split()
        if fields and fields[0].isdigit():
            observations[int(fields[0])] = (int(fields[1]), int(fields[9]))
    if sorted(observations) != list(range(1, 9)):
        raise ValueError("Expected eight FileA treatment means")

    management = {}
    for group, treatment, published_n in (("rainfed", 1, 70.0), ("irrigated", 5, 130.4)):
        native_input = run / "brpi_replay" / f"t{treatment:02}" / "DSSAT48.INP"
        source_paths.append(native_input)
        native = native_input.read_text(encoding="latin-1")
        irrigation = re.findall(r"^\s*(2002\d{3})\s+IR004\s+(\d+\.\d+)\s*$", native, re.M)
        nitrogen = re.findall(r"^\s*(2002\d{3})\s+FE\d+\s+AP\d+\s+\d+\.\s+(\d+\.)", native, re.M)
        irrigation_total = sum(float(amount) for _, amount in irrigation)
        nitrogen_total = sum(float(amount) for _, amount in nitrogen)
        for row in replay["records"][treatment - 1:treatment + 3]:
            if (irrigation_total, nitrogen_total) != (row["summary"]["IRCM"], row["summary"]["NICM"]):
                raise ValueError(f"Native schedules disagree with reported totals for {group}")
        management[group] = {
            "irrigation_events": irrigation, "native_irrigation_mm": irrigation_total,
            "nitrogen_events": nitrogen, "native_nitrogen_kg_ha": nitrogen_total,
            "published_nitrogen_kg_ha": published_n,
        }

    yield_errors = []
    maturity_errors = []
    if [row["treatment"] for row in replay["records"]] != list(range(1, 9)):
        raise ValueError("Replay treatment IDs do not match FileA")
    for row in replay["records"]:
        observed_yield, observed_maturity = observations[row["treatment"]]
        if row["observed_hwAM"] != observed_yield or not row["completed"] or row["returncode"] != 0:
            raise ValueError(f"Invalid replay treatment {row['treatment']}")
        yield_errors.append(row["summary"]["HWAM"] - observed_yield)
        maturity_errors.append(int(row["summary"]["MDAT"]) % 1000 - observed_maturity)
    return {
        "scope": "preserved technical replay and source reconciliation",
        "sources": {
            "weather": "https://www.esalq.usp.br/departamentos/leb/automatica/jan-dez2002.xls",
            "field_management": "https://doi.org/10.1017/S0021859605005198",
            "yield_soil_coefficients": "https://doi.org/10.1016/j.eja.2007.03.002",
            "field_design": "https://doi.org/10.11606/T.11.2004.tde-09112004-164934",
        },
        "research_ready": False, "main_training_allowed": False,
        "replay_image": replay["image"], "replay_binary_sha256": replay["binary_sha256"],
        "source_sha256": {path.name if path == weather_path else path.relative_to(run).as_posix():
                          sha256(path.read_bytes()).hexdigest() for path in source_paths},
        "weather": compare_weather(official / "BRPI0201.WTH", esalq_weather(weather_path)),
        "soil": compare_soil(official / "BR.SOL"),
        "management": management,
        "published_cultivar_cards_matched": len(coefficients),
        "ecotype": {"id": "IB0001", "original_calibration_lineage_confirmed": False},
        "yield_bias_kg_ha": mean(yield_errors),
        "yield_rmse_kg_ha": sqrt(mean(error**2 for error in yield_errors)),
        "maturity_errors_days": maturity_errors,
        "plot_yield_variance_available": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("esalq_xls", type=Path)
    args = parser.parse_args()
    run = args.project / "outputs" / "runs" / SOURCE_RUN
    print(json.dumps(audit(run, args.esalq_xls), indent=2, allow_nan=False))
