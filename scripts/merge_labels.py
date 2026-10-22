"""Merge Google Earth / Wayback labels with the candidate list.

Output: ch4_class3_review_labelled.csv with one row per labelled candidate
(label 0 = unresolvable, dropped). The training season is taken from the
image date, not from the candidate epoch:
  Nov-Dec YYYY -> season YYYY+1; Jan-Apr YYYY -> season YYYY;
  May-Jul YYYY -> season YYYY (just ended); Aug-Oct YYYY -> season YYYY+1.
"""
import csv
import sys

src, lab, out = sys.argv[1:4]
pts = {r['id']: r for r in csv.DictReader(open(src))}
rows = []
for r in csv.DictReader(open(lab)):
    if r['label'] == '0':
        continue
    y, m = int(r['img_date'][:4]), int(r['img_date'][5:7])
    season = y + 1 if m >= 8 else y
    p = pts[r['id']]
    rows.append({'id': r['id'], 'lon': p['lon'], 'lat': p['lat'], 'sector': p['sector'],
                 'cand_epoch': p['epoch'], 'img_date': r['img_date'], 'season': season,
                 'label': r['label'], 'confidence': r['confidence'], 'note': r['note']})
with open(out, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(len(rows), 'rows;', 'seasons', sorted({r['season'] for r in rows}))
