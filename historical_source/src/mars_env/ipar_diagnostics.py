"""Opt-in CERES photosynthesis sidecar. The backend state schema is unchanged."""
from pathlib import Path

from .harvest_diagnostics import HarvestProtocol

FIELDS = ("DATE", "LAI", "POP", "ROW_CM", "SRAD", "PAR", "LIFAC", "ENERGY")


class CeresIparProtocol(HarvestProtocol):
    def __init__(self, path):
        super().__init__()
        self.path = Path(path).resolve()
        self.path.touch(exist_ok=False)

    def patch_template(self, template):
        template = super().patch_template(template)
        fields = "".join(f"  MARS_IPAR_{name}: {'int' if name == 'DATE' else 'float'}\n"
                         for name in FIELDS)
        template = template.replace("\ndata:\n", "\ndata:\n" + fields, 1)
        bindings = ", ".join(f"{name.lower()}: $MARS_IPAR_{name}" for name in FIELDS)
        row = ", ".join(f"{name.lower()!r}: {'int' if name == 'DATE' else 'float'}({name.lower()})"
                        for name in FIELDS)
        event = (
            "      mars_ipar_growth:\n"
            f"        with: {{{bindings}}}\n"
            "        exec: |\n"
            "          import json\n"
            f"          with open({str(self.path)!r}, 'a', encoding='utf-8') as mars_ipar_stream:\n"
            f"            mars_ipar_stream.write(json.dumps({{{row}}}, allow_nan=False) + '\\n')\n"
        )
        return template.replace("    on_event:\n", "    on_event:\n" + event, 1)
