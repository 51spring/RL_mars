"""Audit LIRF weather and management against preserved source files."""
import argparse
from collections import defaultdict
from datetime import datetime, timedelta
from hashlib import sha256
import json
from pathlib import Path
from statistics import mean

from openpyxl import load_workbook


def numeric(value):
    return isinstance(value, (int, float)) and value != -999


def sum_complete(values, count, factor=1):
    return round(sum(values) * factor, 6) if len(values) == count and all(map(numeric, values)) else None


def read_station(path, frequency, fields):
    data = json.loads(path.read_text(encoding="utf-8"))
    assert (data["station"], data["frequency"], data["tzOffset"], data["units"]) == ("gly04", frequency, "-07:00", "m")
    assert len(set(data["time"])) == len(data["time"])
    assert all(len(data[field]) == len(data["time"]) for field in fields)
    return data, dict(zip(data["time"], zip(*(data[field] for field in fields))))


def evidence(workbook, dossier, run):
    dates = {}
    weather = defaultdict(list)
    log = {}
    gross_rain = {}
    book = load_workbook(workbook, read_only=True, data_only=True)
    try:
        for row_number, row in enumerate(book["Weather data"].values, 1):
            if row_number == 1:
                assert (row[6], row[10], row[21]) == ("HrlySolRad_kJ_m^2_min^1", "Rain-Tot", "Rain-Daily")
                continue
            year, doy, stamp = row[:3]
            reported = datetime(year, 1, 1) + timedelta(days=doy - 1)
            assert reported.date() == stamp.date()
            if numeric(row[21]):
                assert stamp.hour == 1 and reported.date().isoformat() not in dates
                dates[reported.date().isoformat()] = row[21]
            weather[(stamp - timedelta(minutes=1)).date().isoformat()].append((row[10], row[6], row[3]))
        for row_number, row in enumerate(book["Crop Log"].values, 1):
            if isinstance(row[0], datetime):
                log[row_number] = {"date": row[0].date().isoformat(), "operation": row[1], "label": row[2], "details": row[3]}
        for row in book["Water Balance ET"].iter_rows(min_row=3, values_only=True):
            if row[0] not in (2012, 2013):
                continue
            day = row[2].date().isoformat()
            assert numeric(row[19])
            assert gross_rain.setdefault(day, row[19]) == row[19]
    finally:
        book.close()

    daily_fields = ("tMax", "tMin", "solarRad", "precip")
    daily_path = run / "gly04_daily_qc.json"
    raw_path = run / "gly04_daily_raw.json"
    qc, station = read_station(daily_path, "daily", daily_fields)
    raw, _ = read_station(raw_path, "daily", daily_fields)
    assert qc["which"] == "qc"
    hourly = defaultdict(list)
    hourly_paths = [run / f"gly04_hourly_{year}.json" for year in (2012, 2013)]
    for path in hourly_paths:
        meta, series = read_station(path, "hourly", ("precip",))
        assert meta["which"] == "qc"
        for stamp, values in series.items():
            day = (datetime.fromisoformat(stamp) - timedelta(minutes=1)).date().isoformat()
            hourly[day].append(values[0])

    comparison = []
    for day, wb_mm in sorted(gross_rain.items()):
        tmax, tmin, solar, rain = [value if numeric(value) else None for value in station[day]]
        plot_rain, plot_solar, plot_temperature = zip(*weather[day])
        assert len(plot_rain) == 24
        comparison.append({
            "date": day,
            "water_balance_mm": wb_mm,
            "weather_daily_mm": dates[day],
            "weather_hourly_mm": sum_complete(plot_rain, 24),
            "station_daily_mm": rain,
            "station_hourly_mm": sum_complete(hourly[day], 24),
            "station_tmax_c": tmax,
            "station_tmin_c": tmin,
            "station_solar_mj_m2": round(solar * 0.0864, 6) if solar is not None else None,
            "weather_solar_mj_m2": sum_complete(plot_solar, 24, 0.06),
            "weather_hourly_tmax_c": max(plot_temperature) if all(map(numeric, plot_temperature)) else None,
            "weather_hourly_tmin_c": min(plot_temperature) if all(map(numeric, plot_temperature)) else None,
        })

    prior = json.loads(dossier.read_text(encoding="utf-8"))
    conflict = [row for row in comparison if abs(row["water_balance_mm"] - row["weather_daily_mm"]) > 0.1]
    assert [(r["date"], r["water_balance_mm"], r["weather_daily_mm"]) for r in conflict] == [
        (r["date"], r["water_balance_mm"], r["weather_daily_mm"]) for r in prior["weather"]["rain_conflicts"]
    ]

    def compare(left, right):
        pairs = [(row[left], row[right]) for row in comparison if row[left] is not None and row[right] is not None]
        differences = [abs(a - b) for a, b in pairs]
        return {"paired_dates": len(pairs), "within_0_1": sum(d <= 0.100000001 for d in differences),
                "mae": round(mean(differences), 6) if differences else None}

    treatment_years = prior["treatment_years"]
    management = []
    for row in treatment_years:
        management.append({
            "year": row["year"],
            "treatment": row["treatment"],
            "planting_water_balance": row["planting_water_balance"],
            "last_water_balance_day": row["last_day"],
            "water_balance_irrigation_mm": row["irrigation_total_mm"],
            "water_balance_fertilizer_n_kg_ha": row["nitrogen_total_kg_ha"],
            "hypothetical_irrigation_n_at_25mg_l_kg_ha": round(row["irrigation_total_mm"] * 0.25, 3),
        })

    anchors = []
    for number in (6, 7, 8, 9, 10, 12, 20, 30, 35, 40, 71, 76, 77, 79, 85, 86, 96, 99, 103, 110, 114, 115, 116, 117):
        event = log[number]
        days = {event["date"]}
        if number == 99:
            days.add("2013-07-16")
        if number == 103:
            days.add("2013-07-28")
        matches = [
            {"treatment": row["treatment"],
             "irrigation": [e for e in row["gross_irrigation_events"] if e["date"] in days],
             "fertilizer": [e for e in row["nitrogen_events"] if e["date"] in days]}
            for row in treatment_years if str(row["year"]) == event["date"][:4]
        ]
        anchors.append({"source_row": number, **event, "water_balance_treatments": matches})

    return {
        "passed": True,
        "scope": "Public field data reconciliation only; no native input assignment or fit.",
        "source_sha256": {p.name: sha256(p.read_bytes()).hexdigest() for p in (workbook, dossier, daily_path, raw_path, *hourly_paths)},
        "station_qc_daily_records": len(station),
        "station_raw_request_returned": raw["which"],
        "station_raw_request_same_bytes_as_qc": raw_path.read_bytes() == daily_path.read_bytes(),
        "station_hourly_records": sum(map(len, hourly.values())),
        "dates_compared": len(comparison),
        "station_complete_daily_four_fields": sum(all(row[key] is not None for key in (
            "station_tmax_c", "station_tmin_c", "station_solar_mj_m2", "station_daily_mm")) for row in comparison),
        "comparisons": {
            "station_daily_vs_station_hourly_precip": compare("station_daily_mm", "station_hourly_mm"),
            "station_daily_vs_water_balance_precip": compare("station_daily_mm", "water_balance_mm"),
            "station_daily_vs_workbook_daily_precip": compare("station_daily_mm", "weather_daily_mm"),
            "workbook_daily_vs_workbook_hourly_precip": compare("weather_daily_mm", "weather_hourly_mm"),
            "station_vs_workbook_solar": compare("station_solar_mj_m2", "weather_solar_mj_m2"),
            "station_tmax_vs_workbook_hourly_max": compare("station_tmax_c", "weather_hourly_tmax_c"),
            "station_tmin_vs_workbook_hourly_min": compare("station_tmin_c", "weather_hourly_tmin_c"),
        },
        "rain_conflicts": conflict,
        "daily_comparison": comparison,
        "management_by_treatment_year": management,
        "crop_log_anchors": anchors,
        "weather_file_assigned": False,
        "irrigation_n_assigned": False,
        "quantitative_fit_ready": False,
        "research_ready": False,
        "main_training_allowed": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("workbook", "dossier", "run"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    result = evidence(args.workbook, args.dossier, args.run)
    (args.run / "verification.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

