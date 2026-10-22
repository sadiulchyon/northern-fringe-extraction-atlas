"""Flag single-season dips: water+sand area in the AOI below 35% of the median of the 3 usable seasons before and
3 after (unflagged cloud, fog or bad scenes). Real gradual change is not flagged. Pit-field sites skipped.
Clears earlier 'outlier' flags first. Edits SITE_series.csv in place."""
import csv, sys, os, statistics
for sid in sys.argv[1:]:
    fn=f'sites/lowflow/{sid}_series.csv'
    rows=list(csv.DictReader(open(fn)))
    for r in rows:
        if r['flag']=='outlier': r['flag']=''
    POND={'E048','E065','E067','E070'}  # pond/pit AOIs: totals swing with rainfall, test not meaningful
    if not os.path.exists(f'sites/lowflow/{sid}_mode.txt') and sid not in POND:
        tot=[float(r['water_ha'])+float(r['sand_ha']) for r in rows]
        ok=[i for i,r in enumerate(rows) if not r['flag']]
        hit=[]
        for k,i in enumerate(ok):
            nb=[tot[j] for j in ok[max(0,k-3):k]+ok[k+1:k+4]]
            if len(nb)>=3 and tot[i]<0.35*statistics.median(nb): hit.append(i)
        for i in hit: rows[i]['flag']='outlier'
        if hit: print(sid,[rows[i]['season'] for i in hit])
    with open(fn,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
