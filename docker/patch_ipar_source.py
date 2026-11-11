"""Expose CERES photosynthesis inputs and result at the calculation site."""
from pathlib import Path
import sys

FIELDS = {
    "DATE": "YRDOY", "LAI": "LAI", "POP": "PLTPOP", "ROW_CM": "ROWSPC",
    "SRAD": "SRAD", "PAR": "PAR", "LIFAC": "LIFAC", "ENERGY": "IPAR",
}


def patch(source):
    anchor = "          PCARB = IPAR * RUE * PCO2\n"
    if source.count(anchor) != 1 or "mars_ipar_growth" in source:
        raise ValueError("Unexpected CERES IPAR source")
    lines = ['          CALL pdi_transaction_begin("mars_ipar_growth")']
    lines.extend(f'          CALL pdi_expose("MARS_IPAR_{name}", {value}, pdi_out)'
                 for name, value in FIELDS.items())
    lines.append("          CALL pdi_transaction_end()")
    if any(len(line) > 72 for line in lines):
        raise ValueError("Diagnostic exceeds fixed-form line width")
    return source.replace(anchor, anchor + "\n".join(lines) + "\n")


if __name__ == "__main__":
    path = Path(sys.argv[1]) / "Plant/CERES-Maize/MZ_GROSUB.for"
    path.write_text(patch(path.read_text()))
