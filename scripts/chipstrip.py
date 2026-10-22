"""Annual chip strip for one site. Usage: python3 chipstrip.py SITE_ID [cube.npz]
False colour SWIR1/NIR/RED, one fixed stretch (2-98 percentile over all years) so changes are comparable.
Inventory points of the site drawn as small circles. Output sites/strips/SITE_strip.png"""
import sys, csv, math, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
sid=sys.argv[1]; fn=sys.argv[2] if len(sys.argv)>2 else f'sites/cubes/{sid}_cube.npz'
d=np.load(fn); cube=d['cube'].astype(float); years=d['years']; bands=list(d['bands']); W,S,E,N=d['region']
nobs=cube[...,bands.index('NOBS')]
rgb=np.stack([cube[...,bands.index(b)] for b in ('SWIR1','NIR','RED')],axis=-1)/1e4
nod=(cube[...,bands.index('NDVI')]==-32768)
rgb[nod]=np.nan
lo=np.nanpercentile(rgb,2,axis=(0,1,2)); hi=np.nanpercentile(rgb,98,axis=(0,1,2))
img=np.clip((rgb-lo)/(hi-lo),0,1); img[nod]=0.5  # masked (outside corridor) = grey
pts=[(float(r['lon']),float(r['lat']),r['rid']) for r in csv.DictReader(open('inventory_411_sectors.csv')) if r['label_group'] in ('Sand Mining','Other extraction')]
site=[r for r in csv.DictReader(open('sites/sites_v1.csv')) if r['site_id']==sid]
rids=set(site[0]['rids'].split(';')) if site else set()
ny,nr,nc=img.shape[:3]
cols=7; rows=math.ceil(ny/cols)
fig,axes=plt.subplots(rows,cols,figsize=(cols*2.6,rows*2.6*nr/nc+0.6))
for ax in axes.flat: ax.axis('off')
for i,ax in enumerate(axes.flat[:ny]):
    ax.imshow(img[i],extent=[W,E,S,N],interpolation='nearest')
    for lon,lat,rid in pts:
        if rid in rids: ax.plot(lon,lat,'o',mfc='none',mec='yellow',ms=7,mew=1.2)
    ax.set_title(f'{int(years[i])}  (n={int(np.median(nobs[i][~nod[i]]))})',fontsize=10,pad=2)
    ax.set_xlim(W,E); ax.set_ylim(S,N)
title=f'{sid}: {site[0]["sector"]}, {site[0]["n_rec"]} records, window {site[0]["window_m"]} m' if site else sid
fig.suptitle(title+'  |  Landsat dry-season (Nov-Apr) composites, SWIR1/NIR/red; n = median scenes per pixel',fontsize=11)
plt.tight_layout(rect=[0,0,1,0.97]); out=f'sites/strips/{sid}_strip.png'; plt.savefig(out,dpi=110); print(out, img.shape)
