"""Extract reported FAW development and mortality from archived JATS tables."""
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from mars_env.artifacts import new_run, sha256, write_json


def mean_se(cell):
    match = re.fullmatch(r"(\d+(?:\.\d+)?) ± (\d+(?:\.\d+)?)(?: ([a-z]+))?", cell)
    if not match:
        raise ValueError(f"Unexpected mean/SE cell: {cell!r}")
    mean, se, group = match.groups()
    return {"mean": float(mean), "se": float(se), "group": group}


def main():
    source = ROOT / "outputs/runs/20261107T023513Z_duplessis_source_10a5e9b4"
    path = source / "article.xml"
    assert sha256(path) == json.loads((source / "source.json").read_text())["sha256"]
    article = ET.parse(path).getroot()
    assert article.findtext(".//article-id[@pub-id-type='doi']") == "10.3390/insects11040228"
    tables = {}
    for number in (1, 2, 3):
        table = article.find(f".//table-wrap[@id='insects-11-00228-t{number:03}']")
        tables[number] = [
            [" ".join("".join(cell.itertext()).split()) for cell in row]
            for row in table.findall(".//tr")
        ]

    t1, t2, t3 = (tables[n] for n in (1, 2, 3))
    temperatures = list(map(int, t1[1]))
    stage = None
    detailed = {}
    degree_day_means = {}
    for label, temp, count, duration, observed_range, degree_days in t3[1:]:
        if label == "Mean":
            degree_day_means[stage] = mean_se(degree_days)
            continue
        stage = label or stage
        detailed[stage, int(temp)] = {
            "n_reported": int(count),
            "duration": mean_se(duration),
            "range": observed_range,
            "degree_days": mean_se(degree_days),
        }

    development = []
    notes = []
    for index in range(2, len(t1) - 1, 2):
        stage, *cells = t1[index]
        for temp, cell, source_range in zip(temperatures, cells, t1[index + 1], strict=True):
            detail = detailed.get((stage, temp))
            # The XML prints “015” for this SE. Table 3 supplies the decimal.
            if (stage, temp) == ("Larvae", 22):
                assert cell == "20.58 ± 015 b" and detail["duration"]["se"] == 0.15
                parsed = mean_se("20.58 ± 0.15 b")
                notes.append({"stage": stage, "temperature_c": temp, "table1": cell,
                              "resolution": "SE 0.15 days from Table 3"})
            else:
                parsed = mean_se(cell)
            if detail:
                assert all(parsed[k] == detail["duration"][k] for k in ("mean", "se"))
            development.append({
                "stage": stage, "temperature_c": temp, "mean_days": parsed["mean"],
                "se_days": parsed["se"], "letter_group": parsed["group"],
                "table1_cell": cell, "table1_range_as_printed": source_range,
                "table3": detail,
            })

    mortality = [
        {"temperature_c": temp, "mortality_percent_reported": int(value),
         "survival_percent_derived": 100 - int(value),
         "starting_count": None, "sampling_se": None}
        for temp, value in zip(temperatures, t1[-1][1:], strict=True)
    ]
    regression = [
        {"stage": stage, "equation_as_printed": equation, "degree_days": mean_se(k),
         "lower_threshold_c": mean_se(t), "r_squared": float(r2)}
        for stage, equation, k, t, r2 in t2[1:]
    ]
    assert temperatures == [18, 22, 26, 30, 32]
    assert len(development) == 50 and len(detailed) == 20 and len(regression) == 10
    assert [r["mortality_percent_reported"] for r in mortality] == [71, 37, 15, 4, 28]
    assert all(r["mean_days"] > 0 and r["se_days"] >= 0 for r in development)

    run = new_run(ROOT, "duplessis_thermal_constraints")
    write_json(run / "thermal_evidence.json", {
        "study_id": "duplessis2020", "doi": "10.3390/insects11040228",
        "constant_temperature_c": temperatures, "temperature_tolerance_c": 1,
        "photoperiod_light_dark_hours": [14, 10],
        "egg_incubator_relative_humidity_percent": {"mean": 70, "tolerance": 5},
        "larval_material": "F6 neonates reared individually on soft-dough sweetcorn kernels NK603",
        "pupal_duration_scope": "prepupal and pupal periods combined",
        "development": development, "larval_mortality": mortality,
        "regression_table2": regression, "table2_caption_temperature_range_c": [18, 30],
        "table3_degree_day_means": degree_day_means, "table_cell_resolution": notes,
        "population_growth_parameters_identified": False,
        "field_survey_noise_identified": False,
    })
    write_json(run / "verification.json", {
        "passed": True, "scope": "Source extraction and Table 1/Table 3 cross-check",
        "source_sha256": sha256(path), "development_cells": len(development),
        "cross_checked_duration_cells": len(detailed), "mortality_cells": len(mortality),
        "regression_rows": len(regression), "population_parameters_assigned": 0,
        "quantitative_fit_ready": False, "research_ready": False,
        "main_training_allowed": False,
        "evidence_sha256": sha256(run / "thermal_evidence.json"),
    })
    print(run)


if __name__ == "__main__":
    main()
