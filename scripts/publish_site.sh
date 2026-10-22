#!/bin/bash
# Copy the atlas data from maps/dash into docs/data, the folder GitHub Pages serves.
# Run from the repository root after dash_pack.sh has refreshed maps/dash.
set -e
cd "$(dirname "$0")/.."
for f in inventory.csv sites.csv site_results.csv onset.csv series.csv chips.json screening.csv events.csv countries.json rivers.json labels.csv; do
  cp "maps/dash/$f" "docs/data/$f"
done
echo "docs/data updated; commit and push to publish."
