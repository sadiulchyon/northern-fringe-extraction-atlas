"""SENSITIVITY COPY (harmonised TM/ETM+ to OLI; outputs in sites/lowflow_harm). Chapter 4, low-flow site analysis v1 (22 Oct 2026).
One cloud-free Landsat C2 L2 scene per dry season (closest to 20 Jan within 15 Dec-28 Feb, clear >= 0.85 of window;
fallback to Nov-Apr), pulled from the Earth Engine editor as SITE_scenes.bin.
River AOI: low-flow water (MNDWI > 0) in at least 2 seasons, components connected to the main channel, buffered 100 m.
Per season, inside the AOI: water (MNDWI > 0), sand/bare (NDVI < 0.15, not water), vegetation (NDVI >= 0.30), other.
Sand-to-water conversion: pixels that were sand in the baseline seasons and are water in season t.
Isolated water (pits/ponds): water patches inside the AOI not connected to the season's main channel.
Usage: python3 scripts/site_lowflow.py SITE   (reads sites/lowflow/SITE_scenes.bin)"""
import sys, json, io, csv, numpy as np
sid=sys.argv[1]; src=f'sites/lowflow/{sid}'; base=f'sites/lowflow_harm/{sid}'
raw=open(src+'_scenes.bin','rb').read(); nl=raw.index(b'\n'); man=json.loads(raw[:nl]); data=raw[nl+1:]
arrs=[]; o=0
for L in man['lens']: arrs.append(np.load(io.BytesIO(data[o:o+L]))); o+=L
g=arrs[0]; occ=g['occurrence'].astype(float); 
sc=[a for a in arrs[1:]]; meta=man['scenes']; years=np.array([m['season'] for m in meta])
B=man['bands']; cube=np.stack([np.stack([a[b] for b in B],-1) for a in sc]).astype(float)  # y,r,c,6
nod=(cube[...,0]==-32768)|(cube[...,5]!=1)
G,R,NIR,SW1,SW2=[cube[...,i]/1e4 for i in range(5)]
# SENSITIVITY (25 Oct 2026): TM/ETM+ scenes transformed to OLI with Roy et al. (2016) ETM+->OLI OLS coefficients
_SL=[0.8483,0.9047,0.8462,0.8937,0.9071]; _IC=[0.0088,0.0061,0.0412,0.0254,0.0172]
_old=np.array([m['sen'] in ('L5','L7') for m in meta])[:,None,None]
G,R,NIR,SW1,SW2=[np.where(_old,_IC[i]+_SL[i]*B,B) for i,B in enumerate([G,R,NIR,SW1,SW2])]
with np.errstate(divide='ignore',invalid='ignore'):
    mndwi=(G-SW1)/(G+SW1); ndvi=(NIR-R)/(NIR+R)
water=(mndwi>0)&~nod; sand=(ndvi<0.25)&~water&~nod; veg=(ndvi>=0.30)&~water&~nod
ny,nr,nc=water.shape
NB8=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]; NB4=[(-1,0),(1,0),(0,-1),(0,1)]
def label(mask,nb=NB8):
    lab=np.zeros(mask.shape,int); n=0
    for (i,j) in np.argwhere(mask):
        if lab[i,j]: continue
        n+=1; st=[(i,j)]; lab[i,j]=n
        while st:
            a,b=st.pop()
            for da,db in nb:
                x,y=a+da,b+db
                if 0<=x<mask.shape[0] and 0<=y<mask.shape[1] and mask[x,y] and not lab[x,y]:
                    lab[x,y]=n; st.append((x,y))
    return lab,n
def dilate(m,r):
    out=m.copy(); rr=int(np.ceil(r))
    for da in range(-rr,rr+1):
        for db in range(-rr,rr+1):
            if da*da+db*db<=r*r:
                out|=np.roll(np.roll(m,da,0),db,1)
    return out
import os
# (v2/v3 notes superseded by v4 below) river = 4-connected components of low-flow water in >= 15% of seasons that lie within 300 m of an
# inventory record of the site (seeds); the largest component is used only if no component is near a record.
# Floodplain beels, ponds and flooded boro paddies are separate or infrequent and drop out. Buffer 100 m.
# Override: sites/lowflow/SITE_keep.txt (component ids to add) / SITE_drop.txt (ids to remove).
import os
# haze test: red reflectance over dense vegetation (NDVI > 0.45); fog and haze raise it or remove dense-vegetation pixels
vegred=[]
for t in range(ny):
    v=(ndvi[t]>0.45)&~nod[t]; vegred.append(float(np.median(R[t][v])) if v.sum()>=50 else np.nan)
hazy=[not (vr<=0.085) for vr in vegred]
okq=[t for t in range(ny) if not hazy[t] and (~nod[t]).mean()>0.8] or list(range(ny))
sfreq=sand[okq].mean(0); wfreq=water[okq].mean(0)
bright=np.nanmedian(np.where(nod[okq],np.nan,(R[okq]+G[okq]+cube[okq][...,0]/1e4)/3),0)
seas=g['seasonality'].astype(float)
# AOI v3 corridor: JRC water (occurrence >= 5 % or >= 1 month in the reference year) or a persistently bare, bright bed
# AOI v6: channel pixels are water or bare (NDVI < 0.2) in >= 40% of usable Januarys ('active'; boro paddies
# alternate flooded/green and mostly fail) and either (a) water in >= 15% of Januarys, (b) a bright sand bed
# (bare in >= 50%, median visible brightness >= 0.10) or (c) a wet mixed pixel (median MNDWI >= -0.30, median NDVI < 0.30).
# Components within 300 m of the site's records, + 100 m. Channels much narrower than 30 m are not resolved.
active=((water|(ndvi<0.2))&~nod)[okq].sum(0)/np.maximum((~nod[okq]).sum(0),1)
sandbed=(sfreq>=0.5)&(bright>=0.10)
mmed=np.nanmedian(np.where(nod[okq],np.nan,mndwi[okq]),0); nmed=np.nanmedian(np.where(nod[okq],np.nan,ndvi[okq]),0)
core=(active>=0.4)&((wfreq>=0.15)|sandbed|((mmed>=-0.30)&(nmed<0.30)))
lab,n=label(core,NB4); sz=np.bincount(lab.ravel()); sz[0]=0
W_,S_,E_,N_=man['region']
site=[r for r in (list(csv.DictReader(open('sites/sites_v1.csv')))+list(csv.DictReader(open('sites/sites_extra.csv')))) if r['site_id']==sid]
inv={r['rid']:r for r in csv.DictReader(open('inventory_411_sectors.csv'))}
seeds=np.zeros_like(core)
if site:
    for rid in [x for x in site[0]['rids'].split(';') if x]:
        lon,lat=float(inv[rid]['lon']),float(inv[rid]['lat'])
        j=int((lon-W_)/(E_-W_)*nc); i=int((N_-lat)/(N_-S_)*nr)
        if 0<=i<nr and 0<=j<nc: seeds[i,j]=True
near=dilate(seeds,300/30)
ids=[k for k in np.unique(lab[near&(lab>0)]) if sz[k]>=10]
keep=np.isin(lab,ids) if ids else lab==sz.argmax()
if os.path.exists(base+'_keep.txt'):
    for k in open(base+'_keep.txt').read().split(): keep|=lab==int(k)
if os.path.exists(base+'_drop.txt'):
    for k in open(base+'_drop.txt').read().split(): keep&=lab!=int(k)
np.save(base+'_components.npy',lab)
aoi=dilate(keep,100/30)
# pit-field mode (sites/lowflow/SITE_mode.txt = 'pitfield'): floodplain pit fields lie outside the channel, so the AOI is
# the whole window and the baseline 'sand' class becomes any baseline land (sand or vegetation): 'sand_to_water' then
# counts baseline land that is water in season t (new ponds/pits).
mode=open(src+'_mode.txt').read().strip() if os.path.exists(src+'_mode.txt') else 'river'
if mode=='pitfield': aoi=np.ones_like(keep)
px_ha=0.09
# baseline: first 8 seasons
nbase=8
okb=[t for t in range(nbase) if not hazy[t]] or list(range(nbase))
bsand=(((sand[okb]|veg[okb]) if mode=='pitfield' else sand[okb]).sum(0)>=len(okb)/2)&aoi; bwater=(water[okb].sum(0)>=len(okb)/2)&aoi
rows=[]; isol_maps=[]
for t in range(ny):
    w=water[t]&aoi; lb,nn=label(w); sz=np.bincount(lb.ravel()); sz[0]=0
    mainw=lb==sz.argmax() if nn else np.zeros_like(w)
    iso=w&~mainw; li,ni=label(iso); isz=np.bincount(li.ravel())[1:] if ni else np.array([])
    isol_maps.append(iso)
    valid=aoi&~nod[t]; vf=valid.sum()/aoi.sum(); sc_=aoi.sum()/max(valid.sum(),1)
    blue=meta[t].get('blue',0) or 0
    flag='haze' if hazy[t] else ('partial' if vf<0.8 else '')
    rows.append(dict(season=int(years[t]),date=meta[t]['date'],sensor=meta[t]['sen'],clear_aoi=round(valid.sum()/aoi.sum(),3),
        blue=blue,veg_red=round(vegred[t],4) if vegred[t]==vegred[t] else '',flag=flag,aoi_ha=round(aoi.sum()*px_ha,1),water_ha=round(w.sum()*px_ha*sc_,1),main_channel_ha=round(mainw.sum()*px_ha*sc_,1),
        sand_ha=round((sand[t]&aoi).sum()*px_ha*sc_,1),veg_ha=round((veg[t]&aoi).sum()*px_ha*sc_,1),
        isolated_water_ha=round(iso.sum()*px_ha,1),isolated_patches=int(ni),isolated_patches_ge3px=int((isz>=3).sum()) if ni else 0,
        sand_to_water_ha=round((bsand&w).sum()*px_ha*sc_,1),water_to_sand_ha=round((bwater&sand[t]).sum()*px_ha*sc_,1)))
with open(base+'_series.csv','w',newline='') as f:
    wr=csv.DictWriter(f,fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
# first season of persistent conversion: sand in baseline, water in t and t+1
first=np.zeros((nr,nc)); 
for t in range(nbase,ny-1):
    hit=bsand&water[t]&water[t+1]&(first==0); first[hit]=years[t]
np.savez_compressed(base+'_lowflow.npz',water=water,sand=sand,veg=veg,nod=nod,aoi=aoi,years=years,first=first,mndwi=mndwi.astype(np.float32),ndvi=ndvi.astype(np.float32),
    rgb=np.stack([SW1,NIR,R],-1).astype(np.float32),true=np.stack([R,G,cube[...,0]/1e4],-1).astype(np.float32),region=np.array(man['region']))
print('AOI ha',round(aoi.sum()*px_ha,1),'baseline sand ha',round(bsand.sum()*px_ha,1))
for r in rows: print(r['season'],r['date'],r['sensor'],r['clear_aoi'],'W',r['water_ha'],'S',r['sand_ha'],'V',r['veg_ha'],'iso',r['isolated_water_ha'],r['isolated_patches_ge3px'],'s2w',r['sand_to_water_ha'],'w2s',r['water_to_sand_ha'])
