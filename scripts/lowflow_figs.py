"""Figures for the low-flow site analysis. Usage: python3 scripts/lowflow_figs.py SITE [check|strip|class]"""
import sys, csv, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
sid=sys.argv[1]; what=sys.argv[2]; base=f'sites/lowflow/{sid}'
d=np.load(base+'_lowflow.npz'); years=d['years']; W,S,E,N=d['region']; aoi=d['aoi']
recs=[]
site=[r for r in (list(csv.DictReader(open('sites/sites_v1.csv')))+list(csv.DictReader(open('sites/sites_extra.csv')))) if r['site_id']==sid][0]
inv={r['rid']:r for r in csv.DictReader(open('inventory_411_sectors.csv'))}
pts=[(float(inv[k]['lon']),float(inv[k]['lat'])) for k in site['rids'].split(';') if k]
def stretch(a,lo=None,hi=None):
    hi=np.nanpercentile(a,99.7,axis=(0,1,2)) if hi is None else hi
    a=a.copy(); a[~np.isfinite(a)]=np.nan
    lo=np.nanpercentile(a,2,axis=(0,1,2)) if lo is None else lo; hi=np.nanpercentile(a,98,axis=(0,1,2)) if hi is None else hi
    return np.clip((a-lo)/(hi-lo),0,1)
fc=stretch(np.where(d['nod'][...,None],np.nan,d['rgb']))
tc=stretch(np.where(d['nod'][...,None],np.nan,d['true']))
cls=np.full(d['water'].shape,3); cls[d['veg']]=2; cls[d['sand']]=1; cls[d['water']]=0; cls[d['nod']]=4
cmap=ListedColormap(['#1f4e9c','#f2d27a','#4f9a45','#c8c3b8','#ffffff'])
ext=[W,E,S,N]
def outline(ax):
    ax.contour(np.flipud(aoi.astype(float)) if False else aoi.astype(float),levels=[0.5],colors='magenta',linewidths=0.8,extent=[W,E,S,N],origin='upper')
    ax.set_xlim(W,E); ax.set_ylim(S,N)
    for x,y in pts: ax.plot(x,y,'o',mfc='none',mec='red',ms=6,mew=1.2)
if what=='check':
    sel=[0,8,16,24,30,37]
    fig,axes=plt.subplots(2,6,figsize=(18,6.4))
    for k,t in enumerate(sel):
        ax=axes[0,k]; ax.imshow(tc[t],extent=ext); outline(ax); ax.set_title(f'{years[t]} true colour'); ax.axis('off')
        ax=axes[1,k]; ax.imshow(cls[t],cmap=cmap,vmin=0,vmax=4,extent=ext,interpolation='nearest'); outline(ax); ax.set_title(f'{years[t]} classes'); ax.axis('off')
    fig.suptitle(f'{sid}: magenta = river AOI (low-flow water in >=2 seasons, connected, +100 m); red = inventory records; classes: blue water, yellow sand, green vegetation, grey other',fontsize=10)
    plt.tight_layout(); plt.savefig(base+'_check.png',dpi=90)
if what in ('strip','class'):
    ii,jj=np.where(aoi); r0,r1,c0,c1=ii.min(),ii.max()+1,jj.min(),jj.max()+1
    nr,nc=aoi.shape
    cW=W+c0/nc*(E-W); cE=W+c1/nc*(E-W); cN=N-r0/nr*(N-S); cS=N-r1/nr*(N-S)
    ny=len(years); cols=8; rows=int(np.ceil(ny/cols))
    h=(r1-r0)/(c1-c0)
    fig,axes=plt.subplots(rows,cols,figsize=(cols*2.4,rows*2.4*h+0.5))
    for ax in axes.flat: ax.axis('off')
    sel=np.load(base+'_lowflow.npz')
    import json
    for t,ax in enumerate(axes.flat[:ny]):
        if what=='strip':
            img=fc[t][r0:r1,c0:c1].copy(); m=~aoi[r0:r1,c0:c1]; img[m]=img[m]*0.35+0.4
        else:
            c=cls[t][r0:r1,c0:c1].copy().astype(float); c[~aoi[r0:r1,c0:c1]]=np.nan; img=c
        if what=='strip': ax.imshow(img,extent=[cW,cE,cS,cN],interpolation='nearest')
        else: ax.imshow(img,cmap=cmap,vmin=0,vmax=4,extent=[cW,cE,cS,cN],interpolation='nearest')
        for x,y in pts: ax.plot(x,y,'o',mfc='none',mec='red' if what=='strip' else 'k',ms=5,mew=1)
        ax.set_xlim(cW,cE); ax.set_ylim(cS,cN)
        ax.set_title(str(years[t]),fontsize=9,pad=1)
    lab={'strip':'SWIR1/NIR/red, one January scene per season, fixed stretch; outside AOI faded; red = records',
         'class':'classes inside AOI: blue water (MNDWI>0), yellow sand (NDVI<0.25), green vegetation (NDVI>=0.30), grey other'}[what]
    fig.suptitle(f'{sid}: {lab}',fontsize=10)
    plt.tight_layout(rect=[0,0,1,0.97]); plt.savefig(f'{base}_{what}.png',dpi=80)
if what=='series':
    rows=list(csv.DictReader(open(base+'_series.csv'))); y=[int(r['season']) for r in rows]
    f=lambda k:[float(r[k]) for r in rows]
    fig,ax=plt.subplots(3,1,figsize=(9,8),sharex=True)
    ax[0].plot(y,f('water_ha'),'o-',c='#1f4e9c',label='water'); ax[0].plot(y,f('sand_ha'),'s-',c='#c9a227',label='sand/bare'); ax[0].plot(y,f('main_channel_ha'),'--',c='#1f4e9c',alpha=.6,label='water in main channel')
    ax[0].legend(fontsize=8); ax[0].set_ylabel('ha in AOI')
    ax[1].plot(y,f('isolated_water_ha'),'o-',c='k',label='isolated water (not connected to main channel)'); ax2=ax[1].twinx(); ax2.bar(y,f('isolated_patches_ge3px'),alpha=.25,color='k'); ax2.set_ylabel('patches >= 3 px')
    ax[1].legend(fontsize=8); ax[1].set_ylabel('ha')
    ax[2].plot(y,f('sand_to_water_ha'),'o-',c='#b2182b',label='baseline sand now water'); ax[2].plot(y,f('water_to_sand_ha'),'s-',c='#2166ac',label='baseline water now sand'); ax[2].legend(fontsize=8); ax[2].set_ylabel('ha'); ax[2].set_xlabel('dry season (scene date in Jan of that year, mostly)')
    fig.suptitle(f'{sid}: low-flow classes inside the river AOI (baseline = 1988-1995)',fontsize=10)
    plt.tight_layout(); plt.savefig(f'{base}_series.png',dpi=90)
if what=='first':
    first=d['first'].astype(float); first[(first==0)|~aoi]=np.nan
    fig,ax=plt.subplots(1,2,figsize=(15,5.6))
    base_img=tc[0].copy(); 
    ax[0].imshow(base_img,extent=ext); outline(ax[0])
    im=ax[0].imshow(first,cmap='plasma',vmin=1996,vmax=2024,extent=ext,interpolation='nearest')
    plt.colorbar(im,ax=ax[0],shrink=0.8,label='first season sand -> water, persisting 2 seasons')
    ax[0].set_title(f'{sid}: first year of persistent sand-to-water conversion (baseline 1988-1995)')
    v=first[np.isfinite(first)]
    ax[1].hist(v,bins=np.arange(1995.5,2025.5,1),color='#6a3d9a'); ax[1].set_xlabel('season'); ax[1].set_ylabel('pixels (0.09 ha each)')
    ax[1].set_title('converted pixels by first season')
    plt.tight_layout(); plt.savefig(f'{base}_first.png',dpi=75)
if what=='zoom':
    # zoom box given as lon/lat in argv[3]: W,S,E,N ; seasons in argv[4] as a-b
    zW,zS,zE,zN=[float(x) for x in sys.argv[3].split(',')]; a,b=[int(x) for x in sys.argv[4].split('-')]
    nr,nc=aoi.shape
    zW,zE,zS,zN=max(zW,W),min(zE,E),max(zS,S),min(zN,N)
    c0=int((zW-W)/(E-W)*nc); c1=int((zE-W)/(E-W)*nc); r0=int((N-zN)/(N-S)*nr); r1=int((N-zS)/(N-S)*nr)
    ts=[t for t in range(len(years)) if a<=years[t]<=b]; cols=7; rows=int(np.ceil(len(ts)/cols))*2
    h=(r1-r0)/(c1-c0)
    fig,axes=plt.subplots(rows,cols,figsize=(cols*2.3,rows*2.3*h+0.4))
    for ax in axes.flat: ax.axis('off')
    for k,t in enumerate(ts):
        rr=(k//cols)*2; cc=k%cols
        ax=axes[rr,cc]; ax.imshow(tc[t][r0:r1,c0:c1],extent=[zW,zE,zS,zN],interpolation='nearest'); ax.set_title(f'{years[t]}',fontsize=8,pad=1)
        ax.contour(aoi[r0:r1,c0:c1].astype(float),levels=[.5],colors='magenta',linewidths=.6,extent=[zW,zE,zS,zN],origin='upper')
        for x,y in pts:
            if zW<x<zE and zS<y<zN: ax.plot(x,y,'o',mfc='none',mec='red',ms=5)
        ax.set_xlim(zW,zE); ax.set_ylim(zS,zN)
        ax=axes[rr+1,cc]; c=cls[t][r0:r1,c0:c1].astype(float); c[~aoi[r0:r1,c0:c1]]=np.nan
        ax.imshow(c,cmap=cmap,vmin=0,vmax=4,extent=[zW,zE,zS,zN],interpolation='nearest'); ax.set_xlim(zW,zE); ax.set_ylim(zS,zN)
    fig.suptitle(f'{sid} zoom {zW},{zS},{zE},{zN}: true colour (top) and classes inside AOI (bottom)',fontsize=9)
    plt.tight_layout(rect=[0,0,1,0.98]); plt.savefig(f'{base}_zoom_{a}_{b}.png',dpi=80)
if what=='panel':
    # one-page summary: 8 seasons true colour cropped to AOI bbox, first-conversion map, series
    rows_=list(csv.DictReader(open(base+'_series.csv'))); yy=np.array([int(r['season']) for r in rows_])
    g=lambda k:np.array([float(r[k]) for r in rows_])
    ii,jj=np.where(aoi); nr,nc=aoi.shape; pad=3
    r0,r1,c0,c1=max(ii.min()-pad,0),min(ii.max()+1+pad,nr),max(jj.min()-pad,0),min(jj.max()+1+pad,nc)
    cW=W+c0/nc*(E-W); cE=W+c1/nc*(E-W); cN=N-r0/nr*(N-S); cS=N-r1/nr*(N-S)
    want=[1989,1995,2001,2005,2010,2014,2018,2024]
    ts=[int(np.argmin(np.abs(years-w))) for w in want]
    fig=plt.figure(figsize=(16,10))
    gs=fig.add_gridspec(3,4,height_ratios=[1,1,1.1])
    for k,t in enumerate(ts):
        ax=fig.add_subplot(gs[k//4,k%4]); img=tc[t][r0:r1,c0:c1].copy(); m=~aoi[r0:r1,c0:c1]; img[m]=img[m]*0.45+0.35
        ax.imshow(img,extent=[cW,cE,cS,cN],interpolation='nearest')
        for x,y in pts: ax.plot(x,y,'o',mfc='none',mec='red',ms=6,mew=1.2)
        ax.set_xlim(cW,cE); ax.set_ylim(cS,cN); ax.set_title(f'{years[t]}',fontsize=10); ax.tick_params(labelsize=6)
    ax=fig.add_subplot(gs[2,:2]); first=d['first'].astype(float); first[(first==0)|~aoi]=np.nan
    ax.imshow(tc[0][r0:r1,c0:c1]*0.6+0.3,extent=[cW,cE,cS,cN])
    im=ax.imshow(first[r0:r1,c0:c1],cmap='plasma',vmin=1996,vmax=2024,extent=[cW,cE,cS,cN],interpolation='nearest')
    plt.colorbar(im,ax=ax,shrink=0.8,label='first season sand -> water (persists 2 seasons)'); ax.set_title('first year of persistent sand-to-water conversion',fontsize=10); ax.tick_params(labelsize=6)
    ax=fig.add_subplot(gs[2,2:])
    ok=np.array([r['flag']=='' for r in rows_])
    for k_,c_,m_,l_ in [('water_ha','#1f4e9c','o','water'),('sand_ha','#c9a227','s','sand/bare'),('sand_to_water_ha','#b2182b','^','baseline sand now water')]:
        ax.plot(yy[ok],g(k_)[ok],m_+'-',c=c_,label=l_); ax.plot(yy[~ok],g(k_)[~ok],'x',c=c_,ms=7)
    ax.set_xlabel('x = hazy or partial scene, excluded')
    ax.set_ylabel('ha in AOI'); ax.legend(fontsize=8); ax.set_title(f'AOI {aoi.sum()*0.09:.0f} ha (low-flow channel + 100 m)',fontsize=10)
    fig.suptitle(f'{sid} ({site["sector"]}, {site["admin0"]}, {site["n_rec"]} records): January low-flow Landsat, true colour, outside AOI faded; red = inventory records',fontsize=11)
    plt.tight_layout(rect=[0,0,1,0.97]); plt.savefig(f'{base}_panel.png',dpi=72)
    from PIL import Image; Image.open(f'{base}_panel.png').convert('RGB').save(f'/tmp/{sid}_panel.jpg',quality=75)
    print('panel',Image.open(f'{base}_panel.png').size)
