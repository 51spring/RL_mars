"""Apply a narrowly anchored patch to a container copy, preserving vendor source."""
from pathlib import Path
import sys

root = Path(sys.argv[1])
path = root / "Plant/CERES-Maize/MZ_GROSUB.for"
text = path.read_text()
decl = "      IMPLICIT  NONE\n"
anchor = "      ELSEIF(DYNAMIC.EQ.OUTPUT) THEN"
assert text.count(decl) == 1 and text.count(anchor) == 1
block = Path(__file__).with_name("leaf_integration.for").read_text()
text = text.replace(decl, decl + "      REAL MARS_DELTA, MARS_DM, MARS_N\n      REAL MARS_CUM_DM, MARS_CUM_N, MARS_ROOT_SEN_N\n      REAL MARS_SEED_N\n")
init = "          CumLfNSenes = 0.0"
assert text.count(init) == 1
text = text.replace(init, init + "\n          MARS_CUM_DM = 0.0\n          MARS_CUM_N = 0.0\n          MARS_ROOT_SEN_N = 0.0\n          MARS_SEED_N = 0.0")
seed_anchor = "                  STOVN = STOVWT * TANC"
assert text.count(seed_anchor) == 1
text = text.replace(seed_anchor, seed_anchor + "\n                  MARS_SEED_N = (ROOTN+STOVN)*PLTPOP")
text = text.replace(anchor, block + "\n" + anchor)
audit_anchor = '      CALL pdi_transaction_begin("send_state_mz_grosub")'
assert text.count(audit_anchor) == 1
audit = '      MARS_ROOT_SEN_N = SUM(SENESCE % ResE(1:NLAYR,1))\n' + audit_anchor + '\n'
for name, variable in {"ROOTN": "ROOTN", "RTWT": "RTWT", "WTNUP": "WTNUP", "CARBO": "CARBO", "TRNU": "TRNU",
                       "POPULATION": "PLTPOP", "CANOPY_N": "WTNCAN", "DEAD_LEAF_N": "CumLfNSenes", "DEAD_LEAF_DM": "CumLeafSenes",
                       "ROOT_SEN_N": "MARS_ROOT_SEN_N", "CUM_DM": "MARS_CUM_DM", "CUM_N": "MARS_CUM_N", "SEED_N": "MARS_SEED_N"}.items():
    audit += f'      CALL pdi_expose("MARS_{name}", {variable}, pdi_out)\n'
text = text.replace(audit_anchor, audit)
path.write_text(text)

# The daily close event runs even before emergence and on the final day.
main = root / "CSM_Main/CSM.for"
text = main.read_text()
day_end = "      ENDDO DAY_LOOP"
assert text.count(day_end) == 1
text = text.replace(day_end, '      CALL pdi_transaction_begin("mars_day_finish")\n      CALL pdi_transaction_end()\n' + day_end)
main.write_text(text)
