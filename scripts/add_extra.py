"""Append new reaches to sites/sites_extra.csv and maps/dash/sites_extra.csv.
Usage: python3 scripts/add_extra.py 'SID|lon|lat|window_m|admin0|admin1|name|mode' ...  (mode: river or pitfield)"""
import csv, math, sys
pts=[]
for fn in ['sites/sites_v1.csv','sites/sites_extra.csv']:
    for r in csv.DictReader(open(fn)): pts.append((float(r['lon']),float(r['lat']),r['sector']))
hdr=open('sites/sites_extra.csv').readline().strip().split(',')
rows=[]
for a in sys.argv[1:]:
    sid,lon,lat,w,a0,a1,name,mode=a.split('|'); lon=float(lon); lat=float(lat); w=int(w)
    sec=next(k for k,hi in [('S1',89.30),('S2',89.92),('S3',90.30),('S4',90.95),('S5',91.60),('S6',99)] if lon<hi)  # Table 4.1 longitude bands
    h=w/2; dl=h/111320; dn=h/(111320*math.cos(math.radians(lat)))
    d=dict.fromkeys(hdr,''); d.update(site_id=sid,n_rec=0,lon=lon,lat=lat,window_m=w,sector=sec,admin0=a0,admin1=a1,names=name,
        west=round(lon-dn,5),east=round(lon+dn,5),south=round(lat-dl,5),north=round(lat+dl,5))
    rows.append(d)
    if mode=='pitfield': open(f'sites/lowflow/{sid}_mode.txt','w').write('pitfield')
for fn in ['sites/sites_extra.csv','maps/dash/sites_extra.csv']:
    ex=open(fn).read()
    with open(fn,'a',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=hdr)
        for d in rows:
            if '\n'+d['site_id']+',' not in ex: wr.writerow(d)
print('[' + ', '.join(f'["{d["site_id"]}", {d["west"]}, {d["south"]}, {d["east"]}, {d["north"]}]' for d in rows) + ']')
for d in rows: print(d['site_id'], d['sector'])
