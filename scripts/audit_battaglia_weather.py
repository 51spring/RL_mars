from argparse import ArgumentParser
import csv
from datetime import date, timedelta
from decimal import Decimal
import json
from pathlib import Path
import re

from mars_env.artifacts import write_json

DATE_HEADER = re.compile(r"^\s*(\d{1,2})-\s*(\d{1,2})-(\d{2})\s+")


def dates_between(start, end):
    return [start + timedelta(days=offset) for offset in range((end - start).days + 1)]


def read_farm_daily(path, year):
    lines = path.read_text(encoding="ascii").splitlines()
    rows = {}
    for index, line in enumerate(lines):
        match = DATE_HEADER.match(line)
        if not match:
            continue
        month, day, short_year = map(int, match.groups())
        day_key = date(2000 + short_year, month, day)
        next_line = lines[index + 1]
        if day_key in rows or next_line[:10].strip():
            raise ValueError(f"Duplicate date or missing minimum temperature row at {day_key}")
        maximum_f, minimum_f = int(line[10:16]), int(next_line[10:16])
        rain_in, solar_ly = Decimal(line[16:22]), int(line[51:56])
        if minimum_f > maximum_f or rain_in < 0 or solar_ly < 0:
            raise ValueError(f"Invalid observation at {day_key}")
        rows[day_key] = (maximum_f, minimum_f, rain_in, solar_ly)
    if list(rows) != dates_between(date(year, 4, 1), date(year, 9, 30)):
        raise ValueError(f"Unexpected dates or order for {year}")
    return rows


def celsius(fahrenheit):
    return (Decimal(fahrenheit - 32) * 5 / 9).quantize(Decimal("0.01"))


def main():
    parser = ArgumentParser(description="Audit archived UK Spindletop daily weather against the published trial calendar.")
    parser.add_argument("run", type=Path)
    parser.add_argument("trial_audit", type=Path)
    args = parser.parse_args()
    run = args.run
    trial = json.loads(args.trial_audit.read_text(encoding="utf-8"))["trial"]
    with (run / "noaa_airport.csv").open(encoding="utf-8", newline="") as stream:
        airport = {}
        for row in csv.DictReader(stream):
            day = date.fromisoformat(row["DATE"])
            if row["STATION"] != "USW00093820" or day in airport:
                raise ValueError(f"Unexpected airport station or duplicate date at {day}")
            airport[day] = row
    summary = {}
    rain_by_month = {}
    with (run / "spindletop_daily.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["date_est", "tmax_f", "tmin_f", "rain_in", "solar_ly", "tmax_c", "tmin_c", "rain_mm", "solar_mj_m2"])
        for year in (2012, 2013):
            rows = read_farm_daily(run / f"spindletop_{year}_daily.html", year)
            for day, (maximum_f, minimum_f, rain_in, solar_ly) in rows.items():
                writer.writerow([day, maximum_f, minimum_f, rain_in, solar_ly, celsius(maximum_f),
                                 celsius(minimum_f), rain_in * Decimal("25.4"), solar_ly * Decimal("0.04184")])
            calendar = trial["years"][str(year)]
            start, end = (date.fromisoformat(calendar[key]) for key in ("planting", "harvest"))
            season = dates_between(start, end)
            surveys = [date.fromisoformat(item["date"]) for item in calendar["phenology_sampling_headers"]]
            if len(surveys) != len(set(surveys)) or not set(surveys).issubset(rows):
                raise ValueError(f"Missing or duplicate phenology dates for {year}")
            rain = sum(rows[day][2] for day in season) * Decimal("25.4")
            airport_missing = [day.isoformat() for day in season if day not in airport or not airport[day]["PRCP"]]
            airport_rain = None if airport_missing else sum(Decimal(airport[day]["PRCP"]) for day in season)
            implied_rain = calendar["precipitation_plus_irrigation_mm"] - calendar["irrigation_mm_approx"]
            rain_by_month[year] = {month: sum(row[2] for day, row in rows.items() if day.month == month) * Decimal("25.4")
                                   for month in (6, 7)}
            summary[str(year)] = {
                "archive_daily_rows": len(rows), "planting": start.isoformat(), "harvest": end.isoformat(),
                "inclusive_season_days": len(season), "survey_dates_matched": len(surveys),
                "farm_season_rain_mm": float(rain),
                "farm_june_rain_mm": float(rain_by_month[year][6]), "farm_july_rain_mm": float(rain_by_month[year][7]),
                "zero_solar_days": [day.isoformat() for day, row in rows.items() if not row[3]],
                "irrigation_days_reported": calendar["irrigation_count"],
                "irrigation_mm_approx_reported": calendar["irrigation_mm_approx"],
                "irrigation_events": None, "paper_implied_approx_rain_mm": implied_rain,
                "farm_minus_paper_implied_rain_mm": float(rain - implied_rain),
                "airport_season_rain_mm": float(airport_rain) if airport_rain is not None else None,
                "airport_missing_season_precip_dates": airport_missing,
                "airport_minus_farm_rain_mm": float(airport_rain - rain) if airport_rain is not None else None,
            }
    write_json(run / "weather_summary.json", {
        "passed": True, "scope": "archive parsing and trial date linkage only",
        "comparison_window": "planting through normal harvest, both dates inclusive",
        "years": summary, "farm_2012_rain_reduction_vs_2013_pct": {
            str(month): float((1 - rain_by_month[2012][month] / rain_by_month[2013][month]) * 100)
            for month in (6, 7)},
        "archive_precision": {"temperature_f": 1, "rain_in": 0.01, "solar_ly": 1},
        "gdd_values_reconciled": False, "irrigation_daily_events_acquired": False,
        "quantitative_fit_ready": False, "research_ready": False, "main_training_allowed": False,
    })


if __name__ == "__main__":
    main()
