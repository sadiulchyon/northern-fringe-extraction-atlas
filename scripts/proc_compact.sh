#!/bin/bash
# usage: proc_compact.sh SITE... : process downloaded bins (like process_ready.sh) but print one compact line per site
cd "$(dirname "$0")/.."
DL="${DOWNLOADS:-$HOME/mnt/Downloads}"
for s in "$@"; do
  f=$(ls -t "$DL/${s}_scenes_v2"*.bin 2>/dev/null | head -1); [ -z "$f" ] && continue
  if [ -f "sites/lowflow/${s}_panel.png" ] && [ -f "sites/lowflow/${s}_scenes.bin" ] && cmp -s "$f" "sites/lowflow/${s}_scenes.bin"; then [ -z "$SUMMARY" ] && continue; else DOWNLOADS="$DL" timeout 100 bash scripts/run_site.sh "$s" >/dev/null 2>&1; fi
  l=$(python3 scripts/onset_table.py "$s" 2>/dev/null | tail -1 | sed 's/^[^:]*AOI/AOI/')
  v=$(python3 - "$s" <<'P'
import csv,sys,statistics as st
r=[x for x in csv.DictReader(open(f'sites/lowflow/{sys.argv[1]}_series.csv')) if x['flag']=='' and x['veg_ha']]
f=lambda k,a:st.mean(float(x[k]) for x in a) if a else 0
e,l=r[:10],r[-10:]
w=[float(x['water_ha']) for x in r]
print(f"veg {f('veg_ha',e):.0f}->{f('veg_ha',l):.0f} sand {f('sand_ha',e):.0f}->{f('sand_ha',l):.0f} water {f('water_ha',e):.0f}->{f('water_ha',l):.0f} wrange {min(w):.0f}-{max(w):.0f}")
P
)
  echo "$s | $l | $v"
done
