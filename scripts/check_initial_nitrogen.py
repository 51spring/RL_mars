"""UFGA8201 six treatments with observed 1982 weather, two initial mineral-N profiles and two fertiliser
schedules, compared with observed grain yields in UFGA8201.MZA (dry weight).

Runs through the project's DssatBackend (gym-DSSAT/PDI) with a FileX transform: observed weather (WTHER M),
reported irrigation and fertiliser schedules (IRRIG/FERTI R), and the selected treatment's water and N levels
copied into the treatment slot that gym-DSSAT runs. Python actions are zero. Run with the legacy interpreter
(/opt/gym_dssat_pdi/bin/python). Initial N variants:
- current: template values (NH4 0.5, NO3 0.1 ug/g);
- dssat35: DSSAT v3.5 / Ma et al. 2006 values kept in the FileX comment (NH4 1.5 to 0.5 by layer, NO3 0.6).
Schedule variants: the FileX as distributed, or the paper's totals 62 and 275 kg N/ha (17 May application removed).
"""
import json
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from mars_env.artifacts import new_run, write_json
from mars_env.dssat_backend import DssatBackend

DSSAT35_NH4 = {5: 1.5, 15: 1.5, 30: 1.5, 60: 1.5, 90: 0.6, 120: 0.5, 150: 0.5, 180: 0.5}
TREATMENTS = range(1, 7)


def transform(initial, schedule, treatment):
    def apply(text):
        lines, out, in_ic, rows = text.splitlines(), [], False, {}
        for line in lines:
            match = re.match(r"^ ([1-6]) 1 0 0 ", line)
            if match:
                rows[int(match.group(1))] = line
        for line in lines:
            if re.match(r"^ 3 1 0 0 ", line):
                line = " 3" + rows[treatment][2:]
            elif line.startswith(" 1 ME "):
                line = re.sub(r"^( 1 ME\s+)\S", r"\1M", line)
            elif line.startswith(" 1 MA "):
                parts = re.match(r"^( 1 MA\s+)(\S)(\s+)(\S)(\s+)(\S)(.*)$", line)
                line = parts.group(1) + parts.group(2) + parts.group(3) + "R" + parts.group(5) + "R" + parts.group(7)
            elif line.startswith("@C  ICBL"):
                in_ic = True
            elif in_ic:
                ic = re.match(r"^ 1\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*$", line)
                if ic:
                    if initial == "dssat35":
                        depth = int(ic.group(1))
                        line = f" 1 {depth:5d} {float(ic.group(2)):5.3f} {DSSAT35_NH4[depth]:5.1f} {0.6:5.1f}"
                else:
                    in_ic = False
            if schedule == "paper" and re.match(r"^ [12] 82137 FE001", line):
                continue
            out.append(line)
        return "\n".join(out) + "\n"
    return apply


def observed():
    text = Path("/opt/dssat_pdi/Maize/UFGA8201.MZA").read_text(errors="replace")
    header = next(line for line in text.splitlines() if line.startswith("@TRNO"))
    names = header.lstrip("@").split()
    return {int(v[0]): float(v[names.index("HWAM")].rstrip(".")) for v in
            (line.split() for line in text.splitlines() if re.match(r"^\s+\d+\s", line))}


def run_treatment(initial, schedule, treatment):
    backend = DssatBackend(filex_transform=transform(initial, schedule, treatment))
    try:
        state = backend.reset(seed=123456)
        for _ in range(500):
            state, done, outcome = backend.step(0, 0)
            if done:
                return {"hwam": outcome.summary.get("HWAM"), "hwah": outcome.harvested_grain_kg_ha,
                        "reason": outcome.reason, "fertiliser_n": outcome.summary.get("NICM"),
                        "irrigation_mm": outcome.summary.get("IRCM")}
        raise RuntimeError("season did not finish")
    finally:
        backend.close()


def main():
    run = new_run(ROOT, "initial_nitrogen_check")
    print("RUN_DIR=" + str(run), flush=True)
    obs = observed()
    results = {}
    for initial in ("current", "dssat35"):
        for schedule in ("filex", "paper"):
            rows = []
            for treatment in TREATMENTS:
                sim = run_treatment(initial, schedule, treatment)
                rows.append({"trno": treatment, "observed_hwam": obs[treatment], **sim})
            errors = [r["hwam"] - r["observed_hwam"] for r in rows]
            key = f"{initial}|{schedule}"
            results[key] = {"rows": rows, "rmse": math.sqrt(sum(e * e for e in errors) / len(errors)),
                            "bias": sum(errors) / len(errors)}
            print(key, round(results[key]["rmse"], 1), round(results[key]["bias"], 1),
                  [(r["trno"], round(r["hwam"]), r["observed_hwam"], r["fertiliser_n"], r["irrigation_mm"]) for r in rows], flush=True)
    write_json(run / "verification.json", {"passed": True, "observed": obs, "results": results,
                                           "weather": "observed 1982 UFGA8201.WTH (WTHER M)",
                                           "note": "UFGA8201 may have been used to calibrate cultivar IB0035; consistency check, not independent validation",
                                           "research_ready": False})


if __name__ == "__main__":
    main()
