#!/bin/bash
# usage: scripts/dash_pack.sh TAG SITE... : outliers, onset table, series, kml, chips, tar -> maps/dash/TAG_x.tgz
python3 scripts/flag_outliers.py "$@" 2>/dev/null | tail -n +1 >/dev/null
shift 0
S=$(tail -n +2 maps/dash/site_results.csv | cut -d, -f1 | tr '\n' ' ')
python3 scripts/onset_table.py $S > /dev/null 2>&1; cp sites/lowflow/onset_summary.csv maps/dash/onset.csv
python3 - <<'P'
import csv,glob,os
rows=[]
for fn in sorted(glob.glob('sites/lowflow/[EN][0-9]*_series.csv')):
    sid=os.path.basename(fn).split('_')[0]
    for x in csv.DictReader(open(fn)):
        rows.append([sid,x['season'],x['date'],x['sensor'],x['flag'],x['aoi_ha'],x['water_ha'],x['sand_ha'],x['veg_ha'],x['sand_to_water_ha']])
with open('maps/dash/series.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['site','season','date','sensor','flag','aoi_ha','water_ha','sand_ha','veg_ha','s2w_ha']); w.writerows(rows)
P
python3 scripts/inventory_kml.py >/dev/null; python3 scripts/site_chips.py >/dev/null
cd maps/dash; sleep 2; tar czf pack.tgz onset.csv series.csv chips.json sites_extra.csv 2>/dev/null; F=${TAG:-p}_$(date +%s).tgz; cat pack.tgz > tmp_$F; cat tmp_$F > $F; rm -f pack.tgz tmp_$F; echo $F
