"""Export ledger and diagnostic N inventory. Not a certified whole-system budget."""
import math

from .dssat_backend import BackendContractError
from .leaf_diagnostics import verify_leaf_accounting


class RemovalLedger:
    def __init__(self):
        self.last_date = -1
        self.dry_matter_g_m2 = 0.0
        self.nitrogen_g_m2 = 0.0
        self.records = 0
        self.injury_days = 0

    def append(self, record):
        if record["yrdoy"] <= self.last_date:
            raise BackendContractError("Duplicate or out-of-order removal record")
        verify_leaf_accounting(record)
        dm, nitrogen = record["export_dm_g_m2"], record["export_n_g_m2"]
        if not math.isfinite(dm + nitrogen) or min(dm, nitrogen) < 0:
            raise BackendContractError("Invalid removed stocks")
        total_dm, total_n = self.dry_matter_g_m2 + dm, self.nitrogen_g_m2 + nitrogen
        for actual, expected in ((record["cum_export_dm_g_m2"], total_dm),
                                 (record["cum_export_n_g_m2"], total_n)):
            if not math.isclose(actual, expected, rel_tol=5e-5, abs_tol=3e-5):
                raise BackendContractError("Native cumulative removal differs from independent sum")
        self.dry_matter_g_m2, self.nitrogen_g_m2 = total_dm, total_n
        self.last_date = record["yrdoy"]
        self.records += 1
        self.injury_days += int(dm > 0)

    def summary(self):
        return {"records": self.records, "injury_days": self.injury_days,
                "removed_dry_matter_kg_ha": self.dry_matter_g_m2 * 10,
                "removed_nitrogen_kg_ha": self.nitrogen_g_m2 * 10}


class NitrogenInventoryDiagnostic:
    """Reads independent uptake, root loss, seed inputs, and standing plant stocks.

    Native emergence initialization supplies seed N independently of residuals.
    CumLfNSenes is a subset of standing canopy N; do not sum it a second time.
    Daily root senescence is taken from native SENESCE.ResE in kg N/ha.
    This diagnostic cannot by itself validate the whole-season N balance.
    """
    def __init__(self):
        self.root_senescence_kg_ha = 0.0
        self.rows = []

    def append(self, completed_date, audit):
        if self.rows and completed_date <= self.rows[-1]["completed_date"]:
            raise BackendContractError("Nitrogen diagnostic requires each completed date once")
        if not all(math.isfinite(float(v)) for v in audit.values()):
            raise BackendContractError("Non-finite nitrogen inventory")
        self.root_senescence_kg_ha += audit["root_sen_n"]
        standing = 10 * (audit["canopy_n"] + audit["rootn"] * audit["population"])
        uptake, removed = 10 * audit["wtnup"], 10 * audit["cum_n"]
        seed = 10 * audit["seed_n"]
        residual = standing + self.root_senescence_kg_ha + removed - uptake - seed
        row = {"completed_date": completed_date, "standing_plant_n_kg_ha": standing, "uptake_n_kg_ha": uptake,
               "dead_leaf_n_kg_ha_included_in_canopy": audit["dead_leaf_n"],
               "root_senesced_n_kg_ha": self.root_senescence_kg_ha,
               "exported_n_kg_ha": removed, "seed_input_n_kg_ha": seed, "residual_kg_ha": residual}
        self.rows.append(row)

    def summary(self):
        maximum = max((abs(r["residual_kg_ha"]) for r in self.rows), default=0)
        return {"observed_days": len(self.rows), "initial_offset_inferred": False,
                "seed_input_from_native_initialization": True,
                "plant_n_inventory_balance_within_tolerance": bool(self.rows) and maximum <= 0.001,
                "tolerance_kg_ha": 0.001, "max_abs_residual_kg_ha": maximum,
                "final_residual_kg_ha": self.rows[-1]["residual_kg_ha"] if self.rows else None,
                "whole_season_balance_validated": False,
                "carbon_element_balance_validated": False}
