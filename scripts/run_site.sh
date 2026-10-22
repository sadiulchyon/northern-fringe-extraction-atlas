#!/bin/bash
# Usage: [DOWNLOADS=folder] scripts/run_site.sh SITE  -> copies newest SITE_scenes_v2*.bin from the downloads folder, runs analysis and figures
S=$1; cd "$(dirname "$0")/.."
DL="${DOWNLOADS:-$HOME/Downloads}"
f=$(ls -t "$DL/${S}_scenes_v2"*.bin 2>/dev/null | head -1)
[ -z "$f" ] && { echo "no download for $S"; exit 1; }
cp "$f" "sites/lowflow/${S}_scenes.bin"
python3 scripts/site_lowflow.py "$S" | head -1
for w in series first strip class; do python3 scripts/lowflow_figs.py "$S" $w || exit 1; done
python3 scripts/lowflow_figs.py "$S" panel
