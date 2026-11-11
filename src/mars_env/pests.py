"""Uncalibrated pest/damage/survey equations; no mutation of DSSAT crop state."""
from dataclasses import dataclass, replace
import math


@dataclass(frozen=True)
class PestParameters:
    temperature_low_c: float
    temperature_high_c: float
    growth_low: float = 0.05
    growth_high: float = 0.15
    efficacy: float = 0.8
    residual_days: float = 5
    alpha: float = 0.03

    def __post_init__(self):
        if not all(math.isfinite(v) for v in vars(self).values()):
            raise ValueError("Pest parameters must be finite")
        if (self.temperature_low_c >= self.temperature_high_c or self.residual_days <= 0
                or not 0 <= self.efficacy <= 1 or self.alpha < 0 or not 0 <= self.growth_low <= self.growth_high):
            raise ValueError("Invalid pest parameters")

    def growth(self, temperature):
        if not math.isfinite(temperature):
            raise ValueError("Temperature must be finite")
        fraction = min(1, max(0, (temperature - self.temperature_low_c) /
                              (self.temperature_high_c - self.temperature_low_c)))
        return self.growth_low + fraction * (self.growth_high - self.growth_low)

    @classmethod
    def from_config(cls, config):
        p = config["pest"]
        if p["temperature_low_c"] is None or p["temperature_high_c"] is None:
            raise ValueError("Declare/calibrate pest temperature anchors before use")
        return cls(**{name: p[name] for name in cls.__dataclass_fields__})


SURVEY_INTERVAL_DAYS = 7
SURVEY_WINDOW_DAYS = 7


def pest_settings(config):
    """Pest coefficients and survey noise for the experimental environment, all from the config.

    The online controller builds its survey with the default 7-day interval and window, so the
    config must declare exactly those values until they are passed through as well.
    """
    management = config["management"]
    if (management["survey_interval_days"], management["survey_window_days"]) != (SURVEY_INTERVAL_DAYS, SURVEY_WINDOW_DAYS):
        raise ValueError("Survey interval/window other than 7 days are not wired into the online controller")
    noise = config["pest"]["survey_noise_std"]
    if noise is None or not math.isfinite(noise) or noise < 0:
        raise ValueError("Declare a finite survey noise before use")
    return PestParameters.from_config(config), float(noise)


@dataclass(frozen=True)
class PestState:
    density: float = 0
    last_spray_day: int | None = None
    completed_day: int = -1

    def __post_init__(self):
        if (not math.isfinite(self.density) or not 0 <= self.density <= 1
                or type(self.completed_day) is not int or self.completed_day < -1
                or (self.last_spray_day is not None and
                    (type(self.last_spray_day) is not int or not 0 <= self.last_spray_day <= self.completed_day))):
            raise ValueError("Invalid pest state/history")

    def advance(self, day, temperature, arrival, spray, parameters):
        if (not isinstance(day, int) or isinstance(day, bool) or day != self.completed_day + 1
                or not isinstance(spray, bool)):
            raise ValueError("One pest transition per consecutive action day required")
        if (not all(math.isfinite(x) for x in (self.density, temperature, arrival))
                or not 0 <= self.density <= 1 or arrival < 0):
            raise ValueError("Invalid density/weather/arrival")
        last_spray = day if spray else self.last_spray_day
        effect = 0 if last_spray is None else parameters.efficacy * math.exp(-(day - last_spray) / parameters.residual_days)
        pre_control = self.density + parameters.growth(temperature) * self.density * (1 - self.density) + arrival
        density = min(1, max(0, (1 - effect) * pre_control))
        loss = min(1, max(0, parameters.alpha * density))
        return PestState(density, last_spray, day), loss, effect


@dataclass(frozen=True)
class SurveyReading:
    value: float
    day: int


@dataclass(frozen=True)
class DamageSurvey:
    alpha: float
    noise_std: float  # Required: proposal does not specify the noise standard deviation.
    interval_days: int = 7
    window_days: int = 7
    damage: tuple = ()
    reading: SurveyReading | None = None
    morning_day: int = -1
    completed_day: int = -1

    def __post_init__(self):
        if not math.isfinite(self.alpha) or self.alpha < 0 or not math.isfinite(self.noise_std) or self.noise_std < 0:
            raise ValueError("Invalid survey parameters")
        if (type(self.interval_days) is not int or type(self.window_days) is not int
                or self.interval_days <= 0 or self.window_days <= 0):
            raise ValueError("Positive integer survey interval/window required")

    @classmethod
    def from_config(cls, config):
        p, m = config["pest"], config["management"]
        if p["survey_noise_std"] is None:
            raise ValueError("Declare/calibrate survey noise before use")
        return cls(p["alpha"], p["survey_noise_std"], m["survey_interval_days"], m["survey_window_days"])

    def morning(self, day, standard_noise):
        if (not isinstance(day, int) or isinstance(day, bool) or day != self.morning_day + 1
                or self.completed_day != day - 1 or not math.isfinite(standard_noise)):
            raise ValueError("Survey morning must follow the previous completed day")
        history = tuple((d, loss) for d, loss in self.damage if day - self.window_days <= d < day)
        reading = self.reading
        if day % self.interval_days == 0:
            mean = sum(loss for _, loss in history) / len(history) if history else 0
            proxy = mean / self.alpha if self.alpha > 0 else 0
            reading = SurveyReading(min(1, max(0, proxy + self.noise_std * standard_noise)), day)
        return replace(self, damage=history, reading=reading, morning_day=day)

    def complete_day(self, day, leaf_loss):
        if type(day) is not int or day != self.morning_day or day != self.completed_day + 1:
            raise ValueError("Complete each surveyed decision day once")
        if not math.isfinite(leaf_loss) or not 0 <= leaf_loss <= 1:
            raise ValueError("Leaf loss must be a fraction")
        history = tuple((d, loss) for d, loss in self.damage if d > day - self.window_days)
        return replace(self, damage=history + ((day, leaf_loss),), completed_day=day)

    def observation(self):
        if self.morning_day < 0:
            raise ValueError("Prepare the first survey morning")
        return {"survey_value": self.reading.value if self.reading else 0,
                "survey_age": self.morning_day - self.reading.day if self.reading else 0,
                "survey_available": self.reading is not None}
