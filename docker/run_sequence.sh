#!/bin/sh
set -eu
cp fileX.MZX MARS8201.SQX
{
  printf '%s\n' '$BATCH(SEQUENCE AUDIT)' '@FILEX                                                                                         TRTNO RP SQ'
  printf '%-92s %6d %6d %6d\n' 'MARS8201.SQX' 1 1 1
 if [ "${MARS_SEQUENCE_MODE:-Q}" = F ]; then
   printf '%-92s %6d %6d %6d\n' 'MARS8201.SQX' 2 1 1
 else
   printf '%-92s %6d %6d %6d\n' 'MARS8201.SQX' 1 1 2
 fi
} > MARS_SEQ.BAT
exec "${MARS_SEQUENCE_BINARY:-/opt/dssat_pdi/mars_sequence_audit_dscsm048}" "${MARS_SEQUENCE_MODE:-Q}" MARS_SEQ.BAT
