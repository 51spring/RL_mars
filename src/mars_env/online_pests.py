"""Experimental day-close pest/survey controller; explicit uncalibrated inputs."""
import json
import math
from dataclasses import asdict

import numpy as np

from .dssat_backend import DssatBackend
from .leaf_diagnostics import LeafDiagnosticBackend, LeafProtocol
from .pests import DamageSurvey, PestParameters, PestState


class DayCloseController:
    def __init__(self, parameters, noise_std, arrivals, noise):
        self.parameters = parameters
        self.arrivals, self.noise = np.array(arrivals, dtype=float), np.array(noise, dtype=float)
        if (self.arrivals.ndim != 1 or len(self.arrivals) < 2 or self.arrivals.shape != self.noise.shape
                or not np.isfinite(self.arrivals).all() or not np.isfinite(self.noise).all()
                or (self.arrivals < 0).any()):
            raise ValueError("Invalid day-close external tapes")
        self.arrivals.setflags(write=False)
        self.noise.setflags(write=False)
        self.pest = PestState()
        self.survey = DamageSurvey(parameters.alpha, noise_std).morning(0, float(self.noise[0]))
        self.prepared_day = -1
        self.finished_day = -1
        self.requested_fraction = 0.0
        self.last_diagnostic = None
        self._prepared = None

    def prepare_day(self, day, mean_temperature, spray):
        if type(day) is not int or type(spray) is not bool or not math.isfinite(mean_temperature):
            raise ValueError("Invalid completed-day inputs")
        inputs = (day, mean_temperature, spray)
        if day == self.prepared_day:
            if inputs != self._prepared:
                raise ValueError("Inconsistent weather/action for the same day")
            return
        if day != self.finished_day + 1 or day != self.prepared_day + 1 or day + 1 >= len(self.noise):
            raise ValueError("Day-close chronology/tape horizon mismatch")
        self.pest, self.requested_fraction, effect = self.pest.advance(
            day, mean_temperature, float(self.arrivals[day]), spray, self.parameters)
        self.prepared_day, self._prepared = day, inputs
        self._effect = effect

    def finish_day(self, day, mean_temperature, spray, actual_leaf_loss):
        if day != self.finished_day + 1:
            raise ValueError("Finish each day exactly once")
        self.prepare_day(day, mean_temperature, spray)
        if (not math.isfinite(actual_leaf_loss) or actual_leaf_loss < 0
                or actual_leaf_loss > self.requested_fraction + 1e-7):
            raise ValueError("Applied loss exceeds the computed loss")
        self.survey = self.survey.complete_day(day, actual_leaf_loss).morning(day + 1, float(self.noise[day + 1]))
        self.finished_day = day
        self.last_diagnostic = {"day": day, "mean_temperature_c": mean_temperature,
            "arrival": float(self.arrivals[day]), "spray": spray, "density": self.pest.density,
            "effect": self._effect, "requested_fraction": self.requested_fraction,
            "applied_fraction": actual_leaf_loss, "next_morning_survey": self.public_survey()}

    def public_survey(self):
        return self.survey.observation()


class OnlinePestProtocol(LeafProtocol):
    def __init__(self, parameters, noise_std, season):
        super().__init__()
        # Validate all inputs in the parent process before starting Fortran.
        DayCloseController(parameters, noise_std, season.pest_arrivals, season.survey_standard_noise)
        self.payload = {"parameters": asdict(parameters), "noise_std": noise_std,
                        "arrivals": season.pest_arrivals.tolist(), "noise": season.survey_standard_noise.tolist()}
        self.spray = False

    def action_fields(self):
        return {"mars_spray": self.spray}

    def patch_template(self, template):
        template = super().patch_template(template)
        init = (
            "          import sys\n"
            "          sys.path.insert(0, '/workspace/src')\n"
            "          from mars_env.online_pests import DayCloseController, PestParameters\n"
            f"          mars_payload = json.loads({json.dumps(self.payload)!r})\n"
            "          mars_controller = DayCloseController(PestParameters(**mars_payload['parameters']), mars_payload['noise_std'], mars_payload['arrivals'], mars_payload['noise'])\n"
        )
        template = template.replace("          mars_leaf_diagnostic = None", init + "          mars_leaf_diagnostic = None", 1)
        setter = "          delta[()] = action.get('mars_leaf_fraction', 0.0)"
        replacement = (
            "          mars_controller.prepare_day(int(dap), (float(tmin)+float(tmax))/2, bool(action.get('mars_spray', False)))\n"
            "          delta[()] = mars_controller.requested_fraction if float(mars_lfwt) > 0 and float(mars_pla) > float(mars_senla) else 0.0"
        )
        assert template.count(setter) == 1
        template = template.replace(setter, replacement)
        marker = "          'mars_leaf_diagnostic': mars_leaf_diagnostic,"
        template = template.replace(marker, marker + "\n          'mars_pest_public': mars_controller.public_survey(),\n          'mars_pest_diagnostic': mars_controller.last_diagnostic,")
        event = (
            "      mars_day_finish:\n"
            "        exec: |\n"
            "          if int(yrdoy) >= 1982057:\n"
            "            applied = float(mars_leaf_diagnostic['fraction']) if mars_leaf_diagnostic is not None and mars_leaf_diagnostic['yrdoy'] == int(yrdoy) else 0.0\n"
            "            mars_controller.finish_day(int(dap), (float(tmin)+float(tmax))/2, bool(action.get('mars_spray', False)), applied)\n"
        )
        return template.replace("    on_event:\n", "    on_event:\n" + event, 1)


class ExperimentalOnlineBackend(LeafDiagnosticBackend):
    """Diagnostic online loop; does not change the research capability flag."""
    def __init__(self, *, parameters, noise_std, season):
        super().__init__()
        self._instrumentation = OnlinePestProtocol(parameters, noise_std, season)

    def step_online(self, water_mm, nitrogen_kg_ha, spray):
        if type(spray) is not bool:
            raise ValueError("Spray must be bool")
        self._instrumentation.spray = spray
        return DssatBackend.step(self, water_mm, nitrogen_kg_ha)

    def step(self, water_mm, nitrogen_kg_ha):
        return self.step_online(water_mm, nitrogen_kg_ha, False)

    def step_damage(self, *args):
        raise ValueError("Online diagnostic computes damage from completed-day weather")
