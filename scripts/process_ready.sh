#!/bin/bash
# Process every downloaded SITE_scenes_v2.bin in ~/Downloads (or $DOWNLOADS) for the listed sites that has no series yet; print the Pettitt line and a compact series.
cd "$(dirname "$0")/.."
DL="${DOWNLOADS:-$HOME/Downloads}"
for s in "$@"; do
  f=$(ls -t "$DL/${s}_scenes_v2"*.bin 2>/dev/null | head -1); [ -z "$f" ] && continue
  [ -f "sites/lowflow/${s}_scenes.bin" ] && cmp -s "$f" "sites/lowflow/${s}_scenes.bin" && [ -f "sites/lowflow/${s}_panel.png" ] && continue
  DOWNLOADS="$DL" bash scripts/run_site.sh "$s" >/dev/null 2>&1
  python3 scripts/onset_table.py "$s" | tail -1
  awk -F, 'NR>1 && $7==""{printf "%s w%.0f s%.0f v%.0f s2w%.0f| ", $1,$9,$11,$12,$16}' "sites/lowflow/${s}_series.csv"; echo
done
