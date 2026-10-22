# Chapter 4: what the classification sees. Five sites, one per result class: true colour and water/sand/vegetation classes, before and after the change.
import csv, textwrap, numpy as np, matplotlib, os; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
H=os.path.dirname(os.path.abspath(__file__)); WK=os.path.join(H,'..','..','working'); OUT=os.path.join(H,'..')
plt.rcParams.update({"font.family":"Liberation Sans","font.size":6.5})
SITES=[('E060','Dolura border river (S5)','Pit extraction',2010,2024),
       ('E013','Patgram floodplain (S1)','Floodplain pits',1996,2010),
       ('N05','Someshwari, Durgapur (S4)','Pit extraction',2015,2024),
       ('N17','Teesta entry, Dimla (S1)','Bar vegetation',2005,2021),
       ('N28','Jamalpur Economic Zone (S3)','Land filling',2016,2019)]
CM=ListedColormap(['#d9d9d9','#2b6cb0','#e8c170','#4d9221'])  # other, water, sand, veg
fig,axes_all=plt.subplots(len(SITES),5,figsize=(6.7,7.4),dpi=300,gridspec_kw={'wspace':0.04,'hspace':0.08,'width_ratios':[0.85,1,1,1,1]})
for a in axes_all[:,0]: a.axis('off')
def pick(years,flags,nod,y,r0,r1,c0,c1):
    us=[yy for yy in years if flags.get(int(yy),'')=='' and abs(int(yy)-y)<=2] or [yy for yy in years if flags.get(int(yy),'')=='']
    return years.index(min(us,key=lambda yy:(abs(int(yy)-y)>0, nod[years.index(yy)][r0:r1,c0:c1].mean(), abs(int(yy)-y))))
for i,(sid,name,cls,y0,y1) in enumerate(SITES):
    d=np.load(f'{WK}/sites/lowflow/{sid}_lowflow.npz'); years=list(d['years']); aoi=d['aoi']
    flags={int(r['season']):r['flag'] for r in csv.DictReader(open(f'{WK}/sites/lowflow/{sid}_series.csv'))}
    tc=np.where(d['nod'][...,None],np.nan,d['true']); lo=np.nanpercentile(tc,2,axis=(0,1,2)); hi=np.nanpercentile(tc,98,axis=(0,1,2)); tc=np.clip((tc-lo)/(hi-lo),0,1)
    full=aoi.all()
    ii,jj=np.where(aoi); r0,r1,c0,c1=ii.min(),ii.max()+1,jj.min(),jj.max()+1
    side=max(r1-r0,c1-c0); rm=(r0+r1)//2; cm=(c0+c1)//2
    r0=max(0,rm-side//2); r1=min(aoi.shape[0],r0+side); c0=max(0,cm-side//2); c1=min(aoi.shape[1],c0+side)
    for k,y in enumerate((y0,y1)):
        t=pick(years,flags,d['nod'],y,r0,r1,c0,c1)
        a=axes_all[i,1+2*k]; b=axes_all[i,2+2*k]
        img=tc[t][r0:r1,c0:c1].copy()
        a.imshow(img,interpolation='nearest')
        if not full: a.contour(aoi[r0:r1,c0:c1].astype(float),levels=[0.5],colors='#b2182b',linewidths=0.4)
        c=np.zeros(aoi.shape,int); c[d['veg'][t]]=3; c[d['sand'][t]]=2; c[d['water'][t]]=1
        cc=c[r0:r1,c0:c1].astype(float); cc[~aoi[r0:r1,c0:c1]]=np.nan
        b.imshow(np.ones(cc.shape),cmap=ListedColormap(['#ffffff']),vmin=0,vmax=1); b.imshow(cc,cmap=CM,vmin=0,vmax=3,interpolation='nearest')
        for ax in (a,b):
            ax.set_xticks([]); ax.set_yticks([])
            for s in ax.spines.values(): s.set_linewidth(0.3); s.set_edgecolor('#999999')
        a.text(0.03,0.04,str(int(years[t])),transform=a.transAxes,fontsize=5.5,color='#ffffff',bbox=dict(fc='#000000',alpha=0.55,lw=0,pad=1))
    axes_all[i,0].text(0,0.5,textwrap.fill(name,16)+'\n'+cls,transform=axes_all[i,0].transAxes,ha='left',va='center',fontsize=5.8,linespacing=1.3)
    axes_all[i,-1].plot([0.55,0.55+1000/(side*30)],[0.06,0.06],transform=axes_all[i,-1].transAxes,color='k',lw=1)
    axes_all[i,-1].text(0.55,0.09,'1 km',transform=axes_all[i,-1].transAxes,fontsize=4.5)
for k,t in enumerate(['Before: true colour','Before: classes','After: true colour','After: classes']): axes_all[0,1+k].set_title(t,fontsize=6.5,pad=2)
fig.legend(handles=[Patch(color='#2b6cb0',label='Water (MNDWI > 0)'),Patch(color='#e8c170',label='Sand or bare (NDVI < 0.25)'),Patch(color='#4d9221',label='Vegetation (NDVI ≥ 0.30)'),Patch(color='#d9d9d9',label='Other')],
           loc='lower center',ncol=4,fontsize=6,frameon=False,bbox_to_anchor=(0.55,0.065))
fig.savefig(f'{OUT}/fig4_class_examples.png',bbox_inches='tight'); print('ok')
