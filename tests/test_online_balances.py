from copy import deepcopy
from pathlib import Path
import unittest

from jinja2 import Template
import numpy as np
import yaml

from mars_env.balances import NitrogenInventoryDiagnostic, RemovalLedger
from mars_env.dssat_backend import BackendContractError, terminal_template
from mars_env.exogenous import SeasonExogenous
from mars_env.online_pests import DayCloseController, OnlinePestProtocol
from mars_env.pests import PestParameters


def params():
    return PestParameters(10, 30)


def removal_record():
    b = dict(lfwt=2, pla=110, senla=10, stovn=0.3, stmwt=1,
             xlai=0.01, topwt=4, wtncan=0.4, grainn=0.1, cls=1, cns=0.01)
    a = dict(lfwt=1.5, pla=85, senla=10, stovn=0.25, stmwt=1,
             xlai=0.0075, topwt=3.5, wtncan=0.35, grainn=0.1, cls=1, cns=0.01)
    return dict(yrdoy=1982072, population=1, fraction=0.25, before=b, after=a,
                export_dm_g_m2=0.5, export_n_g_m2=0.05,
                cum_export_dm_g_m2=0.5, cum_export_n_g_m2=0.05)


class BalanceTests(unittest.TestCase):
    def test_independent_sum_rejects_missing_native_export(self):
        ledger = RemovalLedger()
        r = removal_record()
        ledger.append(r)
        self.assertEqual(ledger.summary()["removed_dry_matter_kg_ha"], 5)
        with self.assertRaises(BackendContractError):
            ledger.append(r)
        r2 = deepcopy(r)
        r2["yrdoy"] += 1
        with self.assertRaises(BackendContractError):
            ledger.append(r2)
        self.assertEqual(ledger.records, 1)

    def test_n_inventory_uses_native_seed_input_and_export_without_dead_n_double_counting(self):
        audit = dict(root_sen_n=0, canopy_n=1, rootn=0.1, population=1,
                     wtnup=0, cum_n=0, dead_leaf_n=2, seed_n=1.1)
        inventory = NitrogenInventoryDiagnostic()
        inventory.append(1, audit)
        inventory.append(2, dict(audit, canopy_n=0.9, cum_n=0.1))
        self.assertAlmostEqual(inventory.summary()["final_residual_kg_ha"], 0)
        self.assertTrue(inventory.summary()["plant_n_inventory_balance_within_tolerance"])
        self.assertFalse(inventory.summary()["initial_offset_inferred"])
        self.assertFalse(inventory.summary()["whole_season_balance_validated"])
        inventory.append(3, dict(audit, canopy_n=0.9))
        self.assertAlmostEqual(inventory.summary()["final_residual_kg_ha"], -1)
        with self.assertRaises(BackendContractError):
            inventory.append(3, audit)


class OnlineTests(unittest.TestCase):
    def controller(self):
        return DayCloseController(params(), 0, np.full(20, 0.05), np.zeros(20))

    def test_preemergence_density_advances_but_actual_damage_can_be_zero(self):
        c = self.controller()
        c.finish_day(0, 20, False, 0)
        self.assertGreater(c.pest.density, 0)
        self.assertEqual(c.last_diagnostic["applied_fraction"], 0)
        self.assertEqual(c.public_survey()["survey_value"], 0)
        c.prepare_day(1, 20, False)
        fraction = c.requested_fraction
        c.finish_day(1, 20, False, fraction)
        self.assertEqual(c.finished_day, 1)

    def test_spray_effect_uses_current_completed_day(self):
        a, b = self.controller(), self.controller()
        a.prepare_day(0, 20, False)
        b.prepare_day(0, 20, True)
        self.assertAlmostEqual(b.pest.density, a.pest.density * 0.2)

    def test_repeat_prepare_idempotent_but_changed_weather_and_double_finish_fail(self):
        c = self.controller()
        c.prepare_day(0, 20, False)
        density = c.pest.density
        c.prepare_day(0, 20, False)
        self.assertEqual(c.pest.density, density)
        with self.assertRaises(ValueError):
            c.prepare_day(0, 25, False)
        c.finish_day(0, 20, False, 0)
        with self.assertRaises(ValueError):
            c.finish_day(0, 20, False, 0)

    def test_future_day_and_excess_applied_loss_are_rejected(self):
        c = self.controller()
        with self.assertRaises(ValueError):
            c.prepare_day(1, 20, False)
        with self.assertRaises(ValueError):
            c.finish_day(0, 20, False, 0.5)

    def test_online_template_uses_day_finish_and_keeps_density_private(self):
        source = Path(__file__).parents[1] / "vendor/gym_dssat_pdi/gym-dssat-pdi/gym_dssat_pdi/envs/configs/maize/dssat_pdi.jinja2"
        season = SeasonExogenous("validation", 22001, 0, 12345, 1, None, np.zeros(20), np.zeros(20))
        protocol = OnlinePestProtocol(params(), 0.01, season)
        template = protocol.patch_template(terminal_template(source.read_text()))
        rendered = yaml.safe_load(Template(template).render(port=12345, rseed1=123456))
        self.assertIn("mars_day_finish", rendered["plugins"]["pycall"]["on_event"])
        self.assertIn("mars_controller.prepare_day", rendered["plugins"]["pycall"]["on_event"]["mars_leaf_before"]["exec"])
        c = self.controller()
        self.assertEqual(set(c.public_survey()), {"survey_value", "survey_age", "survey_available"})


if __name__ == "__main__":
    unittest.main()
