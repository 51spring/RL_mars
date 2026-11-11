"""Private JSON-lines backend worker, executed by the unchanged legacy Python."""
from contextlib import redirect_stdout
from dataclasses import asdict
import json
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from mars_env.dssat_backend import DssatBackend
from mars_env.exogenous import SeasonExogenous
from mars_env.online_pests import ExperimentalOnlineBackend
from mars_env.pests import PestParameters
from mars_env.resources import WaterShock


def normal(value):
    if isinstance(value, dict):
        return {k: normal(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [normal(v) for v in value]
    return value.tolist() if hasattr(value, "tolist") else value


def main():
    wire = sys.stdout
    backend = None
    try:
        with redirect_stdout(sys.stderr):
            for line in sys.stdin:
                request = json.loads(line)
                try:
                    command = request["command"]
                    if command == "close":
                        break
                    if command == "reset":
                        if backend is not None:
                            backend.close()
                        config = request["backend_config"]
                        if config["mode"] == "no_pest":
                            backend = DssatBackend()
                        elif config["mode"] == "experimental_pest":
                            season = dict(config["season"])
                            season["shock"] = WaterShock(**season["shock"]) if season["shock"] else None
                            season["pest_arrivals"] = np.asarray(season["pest_arrivals"])
                            season["survey_standard_noise"] = np.asarray(season["survey_standard_noise"])
                            backend = ExperimentalOnlineBackend(parameters=PestParameters(**config["parameters"]),
                                noise_std=config["noise_std"], season=SeasonExogenous(**season))
                        else:
                            raise ValueError("Unknown backend mode")
                        result = {"state": backend.reset(request["seed"], wgen_seed=request.get("wgen_seed"))}
                    elif command == "step" and backend is not None:
                        if request.get("experimental_online", False):
                            state, done, outcome = backend.step_online(request["water"], request["nitrogen"], request["spray"])
                        else:
                            state, done, outcome = backend.step(request["water"], request["nitrogen"])
                        result = {"state": state, "done": done, "outcome": asdict(outcome) if outcome else None}
                    else:
                        raise ValueError("Invalid worker command/state")
                    response = {"version": 1, "ok": True, **normal(result)}
                except Exception as exc:
                    response = {"version": 1, "ok": False, "error": f"{type(exc).__name__}: {exc}"}
                wire.write(json.dumps(response, allow_nan=False) + "\n")
                wire.flush()
    finally:
        if backend is not None:
            backend.close()


if __name__ == "__main__":
    main()
