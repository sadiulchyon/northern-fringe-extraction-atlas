"""Contact sheet of site AOIs: an early and a late January scene with the AOI outline and records. Usage: python3 scripts/aoi_sheet.py OUT.jpg SITE..."""
import sys, csv, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
out=sys.argv[1]; sids=sys.argv[2:]
inv={r['rid']:r for r in csv.DictReader(open('inventory_411_sectors.csv'))}
sites={r['site_id']:r for r in csv.DictReader(open('sites/sites_v1.csv'))}
fig,axes=plt.subplots(len(sids),2,figsize=(10,4.6*len(sids)))
axes=np.atleast_2d(axes)
for k,sid in enumerate(sids):
    d=np.load(f'sites/lowflow/{sid}_lowflow.npz'); W,S,E,N=d['region']; yrs=list(d['years']); aoi=d['aoi']
    tc=np.where(d['nod'][...,None],np.nan,d['true']); lo=np.nanpercentile(tc,2,axis=(0,1,2)); hi=np.nanpercentile(tc,99.7,axis=(0,1,2))
    tc=np.nan_to_num(np.clip((tc-lo)/(hi-lo),0,1),nan=0.5)
    for j,y in enumerate([1995,2020]):
        t=int(np.argmin(np.abs(np.array(yrs)-y))); ax=axes[k,j]
        ax.imshow(tc[t],extent=[W,E,S,N]); ax.contour(aoi.astype(float),levels=[.5],colors='yellow',linewidths=1,extent=[W,E,S,N],origin='upper')
        for rid in sites[sid]['rids'].split(';'): ax.plot(float(inv[rid]['lon']),float(inv[rid]['lat']),'o',mfc='none',mec='red',ms=7,mew=1.5)
        ax.set_xlim(W,E); ax.set_ylim(S,N); ax.set_title(f'{sid} {yrs[t]}  AOI {aoi.sum()*0.09:.0f} ha',fontsize=10); ax.tick_params(labelsize=6)
plt.tight_layout(); plt.savefig('/tmp/sheet.png',dpi=60)
from PIL import Image; Image.open('/tmp/sheet.png').convert('RGB').save(out,quality=72); print(Image.open('/tmp/sheet.png').size)
