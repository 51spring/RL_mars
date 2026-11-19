"""Private process bridge keeps old Gym/PDI isolated from the modern learner."""
from dataclasses import asdict
import json
import os
from pathlib import Path
import select
import signal
import subprocess

from .dssat_backend import BackendContractError, TerminalOutcome


class LegacyProcessBackend:
    supports_leaf_damage = False
    planting_yrdoy = 1982057

    def __init__(self, *, pest_enabled=False, mode="no_pest", parameters=None, noise_std=None, season=None):
        if pest_enabled or mode not in ("no_pest", "experimental_pest"):
            raise BackendContractError("Research pest execution is not enabled")
        self.config = {"mode": mode}
        if mode == "experimental_pest":
            value = asdict(season)
            value["pest_arrivals"] = season.pest_arrivals.tolist()
            value["survey_standard_noise"] = season.survey_standard_noise.tolist()
            self.config.update(parameters=asdict(parameters), noise_std=noise_std, season=value)
        self.process = None
        self.log = None

    def _request(self, request):
        try:
            self.process.stdin.write(json.dumps(request, allow_nan=False) + "\n")
            self.process.stdin.flush()
            if not select.select([self.process.stdout], [], [], 30)[0]:
                raise BackendContractError("Legacy DSSAT worker response timed out")
            line = self.process.stdout.readline()
            result = json.loads(line)
            if result.get("version") != 1 or not result.get("ok"):
                raise BackendContractError(result.get("error", "Invalid legacy worker response"))
            return result
        except Exception:
            self.close()
            raise

    def reset(self, seed=123456, *, wgen_seed=None):
        self.close()
        if os.name != "posix":
            raise BackendContractError("Run the process backend inside the Linux PPO container")
        root = Path(__file__).resolve().parents[2]
        log_dir = Path(os.environ['MARS_RUN_DIR']) / 'legacy_worker_logs' if 'MARS_RUN_DIR' in os.environ else root / "outputs/legacy_worker_logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        self.log = (log_dir / f"worker-{os.getpid()}.log").open("a", encoding="utf-8")
        self.process = subprocess.Popen(
            ["/opt/gym_dssat_pdi/bin/python", "-u", str(root / "scripts/legacy_backend_worker.py")],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self.log,
            text=True, encoding="utf-8", bufsize=1, start_new_session=True)
        request = {"command": "reset", "seed": int(seed), "backend_config": self.config}
        if wgen_seed is not None:
            request["wgen_seed"] = wgen_seed
        return self._request(request)["state"]

    def step(self, water_mm, nitrogen_kg_ha):
        return self._step(water_mm, nitrogen_kg_ha, False, False)

    def step_online(self, water_mm, nitrogen_kg_ha, spray):
        return self._step(water_mm, nitrogen_kg_ha, bool(spray), True)

    def _step(self, water, nitrogen, spray, online):
        if self.process is None:
            raise BackendContractError("Reset process backend first")
        result = self._request({"command": "step", "water": water, "nitrogen": nitrogen,
                               "spray": spray, "experimental_online": online})
        return result["state"], result["done"], TerminalOutcome(**result["outcome"]) if result["outcome"] else None

    def close(self):
        process, self.process = self.process, None
        if process is not None:
            try:
                if process.poll() is None:
                    try:
                        process.stdin.write('{"command":"close"}\n')
                        process.stdin.flush()
                        process.wait(timeout=3)
                    except (OSError, subprocess.TimeoutExpired):
                        try:
                            os.killpg(process.pid, signal.SIGTERM)
                        except ProcessLookupError:
                            pass
                        try:
                            process.wait(timeout=1)
                        except subprocess.TimeoutExpired:
                            try:
                                os.killpg(process.pid, signal.SIGKILL)
                            except ProcessLookupError:
                                pass
                            process.wait(timeout=2)
            finally:
                process.stdin.close()
                process.stdout.close()
        if self.log is not None:
            self.log.close()
            self.log = None
