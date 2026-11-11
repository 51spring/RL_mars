"""Recheck the preserved Q/F domain evidence used in the pretraining review."""

import argparse
import json
from pathlib import Path
import sys


def audit(project):
    sys.path.insert(0, str(project / "src"))
    from mars_env.artifacts import sha256
    from mars_env.carbon_audit import audit_soil_carbon, carbon_coverage, carbon_runs
    from mars_env.integrated_n import analyze_integrated_n

    source = project / "outputs/runs/20261106T070340Z_actual_harvest_domain_3ef3f2a6"
    index_path = source / "verification.json"
    index = json.loads(index_path.read_text())
    if not index["passed"] or index["contract_version"] != "standing_stock_actual_yield_v2":
        raise ValueError("Expected the preserved v2 harvest-domain comparison")

    results = []
    for case in index["cases"]:
        for label in ("control", "candidate"):
            folder = source / case["name"] / label
            contract_path = folder / "contract_diagnostics.json"
            trace_path = folder / "trace.json"
            contract = json.loads(contract_path.read_text())
            trace = json.loads(trace_path.read_text())
            for filename, digest in contract["files"].items():
                if sha256(folder / filename) != digest:
                    raise ValueError(f"Changed native artifact {folder / filename}")
            soil_path = folder / "SoilCBal.OUT"
            carbon = carbon_runs(soil_path.read_text(encoding="latin-1"))
            nitrogen = analyze_integrated_n(folder, contract, trace)
            results.append({
                "case": case["name"], "mode": case["mode"], "managed": case["managed"],
                "image_role": label,
                "soil_carbon_arithmetic": audit_soil_carbon(carbon),
                "soil_carbon_coverage": carbon_coverage(carbon, int(trace[-1]["yrdoy"])),
                "modeled_n_inventory_passed": nitrogen["daily_inventory_passed"],
                "modeled_n_final_residual_kg_ha": nitrogen["final_residual_kg_ha"],
                "artifact_sha256": {path.name: sha256(path) for path in (soil_path, contract_path, trace_path)},
            })
    return {
        "scope": "preserved generic-soil Q/F managed and no-input comparisons",
        "source_report_sha256": sha256(index_path),
        "source_manifest_sha256": sha256(source / "manifest.json"),
        "results": results,
        "whole_elemental_carbon_verified": False,
        "research_ready": False, "main_training_allowed": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    print(json.dumps(audit(parser.parse_args().project), indent=2, allow_nan=False))
