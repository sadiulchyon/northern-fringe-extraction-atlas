#!/bin/bash
# usage: wait_process.sh SITE [maxsec]: wait for ~/Downloads/SITE_scenes_v2*.bin, then process_ready.sh SITE
cd "$(dirname "$0")/.."
S=$1; T=${2:-150}; t=0
until ls $HOME/mnt/Downloads/${S}_scenes_v2*.bin >/dev/null 2>&1; do sleep 5; t=$((t+5)); [ $t -ge $T ] && { echo "$S not yet"; exit 0; }; done
timeout 170 bash scripts/process_ready.sh $S 2>&1 | grep -v "^$" | tail -2
