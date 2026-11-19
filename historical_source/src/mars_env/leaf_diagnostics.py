"""Experimental native writer protocol. Does not authorize pest research runs."""
import math

from .dssat_backend import BackendContractError, DssatBackend

NATIVE_FIELDS = ("LFWT", "PLA", "SENLA", "STOVN", "STMWT", "XLAI", "TOPWT", "WTNCAN", "GRAINN", "CLS", "CNS")
AUDIT_FIELDS = ("ROOTN", "RTWT", "WTNUP", "CARBO", "TRNU", "ROOT_SEN_N", "CUM_DM", "CUM_N",
                "POPULATION", "CANOPY_N", "DEAD_LEAF_N", "DEAD_LEAF_DM", "SEED_N")


class LeafProtocol:
    def __init__(self):
        self.fraction = 0.0

    def action_fields(self):
        return {"mars_leaf_fraction": self.fraction}

    def patch_template(self, template):
        # Called after the fresh terminal state patch; both dictionaries include diagnostics.
        marker = "          'totir': totir,"
        if template.count(marker) != 2:
            raise BackendContractError("Unsupported leaf diagnostic state template")
        audit_fields = ", ".join(f"'{name.lower()}': float(mars_{name.lower()})" for name in AUDIT_FIELDS)
        template = template.replace(marker, marker + "\n          'mars_leaf_diagnostic': mars_leaf_diagnostic,\n"
                                    + "          'mars_plant_audit': {" + audit_fields + "},")
        template = template.replace("          done = False", "          mars_leaf_diagnostic = None\n          done = False", 1)
        data = "  MARS_DELTA: float\n" + "".join(f"  MARS_{name}: float\n" for name in (*NATIVE_FIELDS, *AUDIT_FIELDS, "DM", "N"))
        template = template.replace("\ndata:\n", "\ndata:\n" + data, 1)
        mappings = "".join(f"      MARS_{name}: |\n        mars_{name.lower()} = MARS_{name}\n" for name in (*NATIVE_FIELDS, *AUDIT_FIELDS, "DM", "N"))
        template = template.replace("    on_data:\n", "    on_data:\n" + mappings, 1)
        fields = ", ".join(f"'{name.lower()}': float(mars_{name.lower()})" for name in NATIVE_FIELDS)
        events = (
            "      mars_leaf_before:\n"
            "        with: {delta: $MARS_DELTA}\n"
            "        exec: |\n"
            "          delta[()] = action.get('mars_leaf_fraction', 0.0)\n"
            "          mars_leaf_diagnostic = {'yrdoy': int(yrdoy), 'dap': int(dap), 'vstage': float(vstage), 'population': float(pltpop), 'fraction': float(delta)}\n"
            f"          mars_leaf_diagnostic['before'] = {{{fields}}}\n"
            "      mars_leaf_after:\n"
            "        exec: |\n"
            f"          mars_leaf_diagnostic['after'] = {{{fields}}}\n"
            "          mars_leaf_diagnostic['export_dm_g_m2'] = float(mars_dm)\n"
            "          mars_leaf_diagnostic['export_n_g_m2'] = float(mars_n)\n"
            "          mars_leaf_diagnostic['cum_export_dm_g_m2'] = float(mars_cum_dm)\n"
            "          mars_leaf_diagnostic['cum_export_n_g_m2'] = float(mars_cum_n)\n"
        )
        return template.replace("    on_event:\n", "    on_event:\n" + events, 1)


class LeafDiagnosticBackend(DssatBackend):
    """Opt-in experimental binary; research capability flag remains False."""
    def __init__(self, **kwargs):
        import os
        super().__init__(run_dssat_location=os.environ.get('MARS_LEAF_RUN_LOCATION','/opt/mars/run_leaf'), **kwargs)
        self._instrumentation = LeafProtocol()
        # Each simulator owns its log; parallel/new runs must not replace old logs.
        import os
        from pathlib import Path
        import uuid
        default_folder = Path(__file__).resolve().parents[2] / 'outputs/runs/legacy_runtime'
        folder = Path(os.environ.get('MARS_RUN_DIR', default_folder)) / 'native_logs'
        self._runtime_log_path = str(folder / f'native_{os.getpid()}_{uuid.uuid4().hex[:12]}.log')

    def reset(self, seed=123456, *, wgen_seed=None):
        self._instrumentation.fraction = 0.0
        from pathlib import Path
        Path(self._runtime_log_path).parent.mkdir(parents=True, exist_ok=True)
        return super().reset(seed, wgen_seed=wgen_seed)

    def step_damage(self, water_mm, nitrogen_kg_ha, fraction):
        if not math.isfinite(fraction) or not 0 <= fraction <= 1:
            raise ValueError("Leaf fraction must be in [0,1]")
        self._instrumentation.fraction = float(fraction)
        return super().step(water_mm, nitrogen_kg_ha)

    def step(self, water_mm, nitrogen_kg_ha):
        # A diagnostic pulse never persists implicitly into another day.
        return self.step_damage(water_mm, nitrogen_kg_ha, 0.0)


def verify_leaf_accounting(record):
    """Check conservation and green-area identities from actual native snapshots."""
    b, a = record["before"], record["after"]
    pop, fraction = record["population"], record["fraction"]
    if not all(math.isfinite(v) for section in (b, a) for v in section.values()):
        raise BackendContractError("Non-finite native leaf state")
    expected = {
        "leaf_mass": (a["lfwt"], b["lfwt"] * (1 - fraction)),
        "green_area": (a["pla"] - a["senla"], (b["pla"] - b["senla"]) * (1 - fraction)),
        "senesced_area": (a["senla"], b["senla"]),
        "dry_mass_export": ((b["topwt"] - a["topwt"]), record["export_dm_g_m2"]),
        "nitrogen_export": ((b["wtncan"] - a["wtncan"]), record["export_n_g_m2"]),
        "lai_identity": (a["xlai"], (a["pla"] - a["senla"]) * pop * 0.0001),
        "dead_mass_unchanged": (a["cls"], b["cls"]),
        "dead_n_unchanged": (a["cns"], b["cns"]),
        "grain_n_unchanged": (a["grainn"], b["grainn"]),
        "stem_unchanged": (a["stmwt"], b["stmwt"]),
    }
    # Native REAL stocks are float32: subtracting two large rounded stocks
    # can lose more absolute precision than the small exported increment.
    # Bound the rounding of the native sum/product operands rather than
    # loosening the relative tolerance on the exported quantity arbitrarily.
    epsilon = 2 ** -23
    stock_roundoff = {
        "dry_mass_export": 4 * epsilon * (abs(b["topwt"]) + abs(a["topwt"]) + abs(record["export_dm_g_m2"])),
        "nitrogen_export": 4 * epsilon * (abs(b["wtncan"]) + abs(a["wtncan"]) + abs(record["export_n_g_m2"])),
    }
    for name, (actual, target) in expected.items():
        if not math.isclose(actual, target, rel_tol=3e-5, abs_tol=max(2e-5, stock_roundoff.get(name, 0))):
            raise BackendContractError(f"Native leaf accounting failed: {name}: {actual} vs {target}")
    if any(a[name] < -1e-6 for name in ("lfwt", "stovn", "xlai", "topwt", "wtncan")):
        raise BackendContractError("Negative post-damage stock")
    return {name: abs(actual - target) for name, (actual, target) in expected.items()}
