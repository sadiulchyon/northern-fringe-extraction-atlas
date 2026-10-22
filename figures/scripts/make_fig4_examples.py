# Chapter 4: two example site histories from the low-flow method (true colour, classes, series). Run from chapter-4/.
import csv, numpy as np, matplotlib, os; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
H=os.path.dirname(os.path.abspath(__file__)); WK=os.path.join(H,'..','..'); OUT=os.path.join(H,'..')
plt.rcParams.update({"font.family":"Liberation Sans","font.size":7,"axes.linewidth":0.5,"axes.edgecolor":"#777777"})
INK="#222222"
cmap=ListedColormap(['#2b6cb0','#e8d59a','#6aa84f','#d9d4cc','#ffffff'])
SITES=[('E060','Dolura border river (S5)',[1995,2010,2016,2024]),('N04','Dhalai at Bholaganj (S6)',[1995,2005,2010,2024])]
fig=plt.figure(figsize=(6.7,3.3),dpi=300)
gs=fig.add_gridspec(len(SITES),6,width_ratios=[1,1,1,1,0.45,2.0],wspace=0.06,hspace=0.35)
for i,(sid,name,yrs) in enumerate(SITES):
    d=np.load(f'{WK}/sites/lowflow/{sid}_lowflow.npz'); years=list(d['years']); W,S,E,N=d['region']; aoi=d['aoi']
    tc=np.where(d['nod'][...,None],np.nan,d['true']); lo=np.nanpercentile(tc,2,axis=(0,1,2)); hi=np.nanpercentile(tc,98,axis=(0,1,2)); tc=np.clip((tc-lo)/(hi-lo),0,1)
    cls=np.full(d['water'].shape,3); cls[d['veg']]=2; cls[d['sand']]=1; cls[d['water']]=0; cls[d['nod']]=4
    ii,jj=np.where(aoi); r0,r1,c0,c1=ii.min(),ii.max()+1,jj.min(),jj.max()+1
    # square-ish crop around the AOI
    rr=(r1-r0); cc=(c1-c0); side=max(rr,cc); rm=(r0+r1)//2; cm=(c0+c1)//2
    r0=max(0,rm-side//2); r1=min(aoi.shape[0],r0+side); c0=max(0,cm-side//2); c1=min(aoi.shape[1],c0+side)
    for k,y in enumerate(yrs):
        t=years.index(y); ax=fig.add_subplot(gs[i,k])
        img=tc[t][r0:r1,c0:c1].copy(); m=~aoi[r0:r1,c0:c1]; img[m]=img[m]*0.45+0.45
        ax.imshow(img,interpolation='nearest'); ax.contour(aoi[r0:r1,c0:c1].astype(float),levels=[0.5],colors='#b2182b',linewidths=0.5)
        # class inset: water pixels inside AOI overlaid in blue
        w=np.where(aoi[r0:r1,c0:c1]&d['water'][t][r0:r1,c0:c1],1.0,np.nan)
        ax.imshow(w,cmap=ListedColormap(['#2b6cb0']),alpha=0.75,interpolation='nearest')
        ax.set_xticks([]); ax.set_yticks([]); ax.set_title(f'Jan {y}',fontsize=7,pad=2)
        if k==0: ax.text(-0.02,0.5,f'({"ab"[i]}) {name}',transform=ax.transAxes,rotation=90,ha='right',va='center',fontsize=7,color=INK)
    # series
    rows=[r for r in csv.DictReader(open(f'{WK}/sites/lowflow/{sid}_series.csv')) if r['flag']=='']
    yy=[int(r['season']) for r in rows]; ax=fig.add_subplot(gs[i,5])
    ax.plot(yy,[float(r['sand_ha']) for r in rows],'-',color='#c9a227',lw=1,marker='s',ms=2,label='sand/bare')
    ax.plot(yy,[float(r['water_ha']) for r in rows],'-',color='#2b6cb0',lw=1,marker='o',ms=2,label='water')
    ax.plot(yy,[float(r['sand_to_water_ha']) for r in rows],'-',color='#b2182b',lw=1,marker='^',ms=2,label='baseline sand, now water')
    ax.set_ylabel('Area in outline (ha)',fontsize=6.5); ax.spines[['top','right']].set_visible(False); ax.set_xlim(1987,2026)
    if i==0: ax.legend(fontsize=5.5,frameon=False,loc='upper left')
    if i==len(SITES)-1: ax.set_xlabel('Dry season (January scene)')
fig.savefig(f'{OUT}/fig4_site_examples.png',bbox_inches='tight'); print('ok')
