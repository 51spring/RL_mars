"""Linux-only upstream DSSAT/PDI bridge, with fresh end-of-season output.

The installed Fortran code exposes MZ_CERES variables again after SEASEND.
Build the terminal message from those current callbacks, never the preceding
interact dictionary. The original executable and crop equations are unchanged.
"""
from dataclasses import dataclass
import math
import os
from operator import index
from pathlib import Path


class BackendContractError(RuntimeError):
    pass


def terminal_template(template):
    """Fail closed if the supported upstream template changes."""
    marker = "          message = {'done': done, 'state': {}}"
    start = template.index("          state = {'yrdoy': yrdoy,")
    end = template.index("          message_to_client =", start)
    block = template[start:end].rstrip()
    if template.count(marker) != 1 or not block.endswith("}"):
        raise BackendContractError("Unsupported upstream PDI template")
    return template.replace(marker, block + "\n          message = {'done': done, 'state': state}")


def enable_summary(template):
    lines = template.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("@N OUTPUTS"):
            row = lines[i + 1]
            # DSSAT FileX fixed-width OU line: FNAME / OVVEW / SUMRY.
            tokens = row.split()
            if tokens[:2] != ["1", "OU"] or tokens[4] != "N":
                raise BackendContractError("Unsupported FileX outputs layout")
            import re
            spans = list(re.finditer(r"\S+", row))
            field = spans[4]
            lines[i + 1] = row[:field.start()] + "Y" + row[field.end():]
            return "\n".join(lines) + "\n"
    raise BackendContractError("Missing FileX output controls")


def read_summary(text):
    """Read numeric fields by right-aligned header ends, not split title text."""
    import re
    header, rows = None, []
    for line in text.splitlines():
        if line.startswith("@") and "HWAH" in line and "MDAT" in line:
            header, rows = line, []
        elif header and line.strip() and not line.startswith(("*", "!", "@")):
            if re.match(r"\s+\d+\s", line):
                rows.append(line)
    if header is None or len(rows) != 1:
        raise BackendContractError("Expected exactly one completed summary row")
    fields = list(re.finditer(r"\S+", header))
    data = {}
    for i, match in enumerate(fields):
        name = match.group().lstrip("@")
        if name in ("PDAT", "MDAT", "HDAT", "HWAM", "HWAH", "IRCM", "NICM"):
            left = fields[i - 1].end() if i else 0
            try:
                value = float(rows[0][left:match.end()].strip())
            except ValueError as exc:
                raise BackendContractError(f"Invalid Summary.OUT {name}") from exc
            if not math.isfinite(value):
                raise BackendContractError(f"Non-finite Summary.OUT {name}")
            data[name] = value
    if not {"MDAT", "HDAT", "HWAH"} <= data.keys():
        raise BackendContractError("Missing summary outcome columns")
    return data


@dataclass(frozen=True)
class TerminalOutcome:
    reason: str
    harvested_grain_kg_ha: float
    summary: dict


def classify_terminal(state, summary, warnings):
    # Explicit model warning is required: stage 6 alone is also a normal stage.
    failure = any(marker in warnings.lower() for marker in (
        "crop failure growth program terminated", "crop failure because of lack of germination",
        "seed ran out of metabolite due to deep planting"))
    if failure:
        return TerminalOutcome("crop_failure", 0.0, summary)
    if (state.get("istage") != 10 or summary.get("MDAT", -99) <= 0
            or summary.get("HDAT", -99) < summary["MDAT"]):
        raise BackendContractError("Unclassified termination: no proven maturity/harvest or failure")
    grain = summary.get("HWAH", -99)
    if not math.isfinite(grain) or grain < 0:
        raise BackendContractError("Missing actual harvested yield")
    return TerminalOutcome("harvest", grain, summary)


class DssatBackend:
    """One fresh simulator per reset. Full states are privileged backend data."""
    supports_leaf_damage = False
    planting_yrdoy = 1982057  # Fixed UFGA8201 planting factor 1, PDATE=82057.

    def __init__(self, *, pest_enabled=False, filex_transform=None, run_dssat_location=None):
        if pest_enabled:
            raise BackendContractError("No validated research Fortran/PDI leaf-damage writer; experimental diagnostics are separate")
        self._env = None
        self.state = None
        self.finished = True
        self.broken = False
        self.filex_transform = filex_transform
        self.run_dssat_location = run_dssat_location or os.environ.get('MARS_DSSAT_RUN_LOCATION','run_dssat')
        profile=os.environ.get('MARS_CANONICAL_UFGA_METADATA','0')
        if profile not in ('0','1'):raise ValueError('Unknown FileX metadata profile')
        self.canonical_metadata = profile=='1'

    def reset(self, seed=123456, *, wgen_seed=None):
        if wgen_seed is not None:
            if isinstance(wgen_seed, bool):
                raise ValueError("Expected an integer WGEN seed in 1..99998")
            try:
                wgen_seed = index(wgen_seed)
            except TypeError as exc:
                raise ValueError("Expected an integer WGEN seed in 1..99998") from exc
            if not 1 <= wgen_seed <= 99998:
                raise ValueError("WGEN seed outside 1..99998")
        self.close()
        # Legacy Gym is intentionally only imported inside the Linux backend.
        from gym_dssat_pdi.envs.dssat_pdi import DssatPdi
        filex_transform = self.filex_transform
        canonical_metadata = self.canonical_metadata
        instrumentation = getattr(self, "_instrumentation", None)

        class TerminalDssat(DssatPdi):
            def _close_client(inner):
                from .native_lifecycle import close_native_client
                close_native_client(inner)

            def _write_pdi_yaml(inner):
                if not getattr(inner, "_terminal_patched", False):
                    inner._pdi_yaml_template = terminal_template(inner._pdi_yaml_template)
                    if instrumentation is not None:
                        inner._pdi_yaml_template = instrumentation.patch_template(inner._pdi_yaml_template)
                    inner._terminal_patched = True
                if wgen_seed is not None:
                    # Gym redraws _rseed1 during construction; the PDI template passes this value to IPSIM.
                    inner._rseed1 = wgen_seed
                super()._write_pdi_yaml()

            def _make_fileX_template(inner):
                super()._make_fileX_template()
                inner._fileX = enable_summary(inner._fileX)
                if canonical_metadata:
                    from .input_metadata import canonical_ufga_metadata
                    inner._fileX = canonical_ufga_metadata(inner._fileX)
                if filex_transform is not None:
                    inner._fileX = filex_transform(inner._fileX)

            def _get_state(inner):
                result = super()._get_state()
                inner.received_state = result[1]
                return result

            def _clip_action_dict(inner, action):
                result = super()._clip_action_dict(action)
                if instrumentation is not None:
                    result.update(instrumentation.action_fields())
                return result

        self._env = TerminalDssat(mode="all", cultivar="maize", seed=int(seed), random_weather=True,
                                  run_dssat_location=self.run_dssat_location,
                                  log_saving_path=getattr(self, "_runtime_log_path", None))
        self.state = dict(self._env.received_state)
        self.finished, self.broken = False, False
        return self.state

    def step(self, water_mm, nitrogen_kg_ha):
        if self._env is None or self.finished or self.broken:
            raise BackendContractError("Reset a usable backend before stepping")
        for value, limit in ((water_mm, 50), (nitrogen_kg_ha, 200)):
            if not math.isfinite(value) or not 0 <= value <= limit:
                raise ValueError("Action outside upstream DSSAT bounds")
        try:
            result = self._env.step({"amir": water_mm, "anfer": nitrogen_kg_ha})
            if result is None:
                raise BackendContractError("Upstream swallowed a simulator exception")
            self.state = dict(self._env.received_state)
            self.finished = bool(result[2])
            outcome = None
            if self.finished:
                folder = Path(self._env._tmp_folder)
                summary = read_summary((folder / "Summary.OUT").read_text())
                warning_file = folder / "WARNING.OUT"
                warnings = warning_file.read_text() if warning_file.exists() else ""
                outcome = classify_terminal(self.state, summary, warnings)
            return self.state, self.finished, outcome
        except Exception:
            self.broken = True
            raise

    def close(self):
        if self._env is not None:
            self._env.close()
            self._env = None
        self.finished = True
