# Chapter 4: development of extraction across the belt, west to east: ten sites x six Januaries (true colour, water overlay).
import csv, textwrap, numpy as np, matplotlib, os; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
H=os.path.dirname(os.path.abspath(__file__)); WK=os.path.join(H,'..','..','working'); OUT=os.path.join(H,'..')
plt.rcParams.update({"font.family":"Liberation Sans","font.size":6.5})
SITES=[('E013','Patgram floodplain (S1)','floodplain pits 2005'),
       ('E008','Mahananda, Tetulia (S1)','Pits 1999'),
       ('E046','Old Brahmaputra (S3)','Dredging 2019'),
       ('N05','Someshwari, Durgapur (S4)','Pits 2021'),
       ('N01','Jadukata fan (S5)','Pits 2007 / 2021'),
       ('E060','Dolura border river (S5)','Pits 2015'),
       ('N11','Chela (S6)','Pits 2007'),
       ('N04','Dhalai, Bholaganj (S6)','Pits 2005'),
       ('E076','Piyain, Jaflong (S6)','Pits 2012'),
       ('E083','Lubha (S6)','Pits 2013')]
YRS=[1990,2000,2006,2012,2018,2024]
fig,axes_all=plt.subplots(len(SITES),len(YRS)+1,figsize=(6.7,10.6),dpi=300,gridspec_kw={'wspace':0.04,'hspace':0.06,'width_ratios':[0.78]+[1]*len(YRS)})
axes=axes_all[:,1:]
for a in axes_all[:,0]: a.axis('off')
for i,(sid,name,lab) in enumerate(SITES):
    d=np.load(f'{WK}/sites/lowflow/{sid}_lowflow.npz'); years=list(d['years']); aoi=d['aoi']
    flags={int(r['season']):r['flag'] for r in csv.DictReader(open(f'{WK}/sites/lowflow/{sid}_series.csv'))}
    tc=np.where(d['nod'][...,None],np.nan,d['true']); lo=np.nanpercentile(tc,2,axis=(0,1,2)); hi=np.nanpercentile(tc,98,axis=(0,1,2)); tc=np.clip((tc-lo)/(hi-lo),0,1)
    ii,jj=np.where(aoi); r0,r1,c0,c1=ii.min(),ii.max()+1,jj.min(),jj.max()+1
    side=max(r1-r0,c1-c0); rm=(r0+r1)//2; cm=(c0+c1)//2
    r0=max(0,rm-side//2); r1=min(aoi.shape[0],r0+side); c0=max(0,cm-side//2); c1=min(aoi.shape[1],c0+side)
    for k,y in enumerate(YRS):
        ax=axes[i,k]
        usable=[yy for yy in years if flags.get(int(yy),)=='' and abs(int(yy)-y)<=2]
        if not usable: usable=[yy for yy in years if flags.get(int(yy),'')=='']
        t=years.index(min(usable,key=lambda yy:(abs(int(yy)-y)>0, d['nod'][years.index(yy)][r0:r1,c0:c1].mean(), abs(int(yy)-y))))
        img=tc[t][r0:r1,c0:c1].copy(); m=~aoi[r0:r1,c0:c1]; img[m]=img[m]*0.45+0.45
        ax.imshow(img,interpolation='nearest')
        ax.contour(aoi[r0:r1,c0:c1].astype(float),levels=[0.5],colors='#b2182b',linewidths=0.4)
        w=np.where(aoi[r0:r1,c0:c1]&d['water'][t][r0:r1,c0:c1],1.0,np.nan)
        ax.imshow(w,cmap=ListedColormap(['#2b6cb0']),alpha=0.75,interpolation='nearest')
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values(): s.set_linewidth(0.3); s.set_edgecolor('#999999')
        if i==0: ax.set_title(f'Jan {y}',fontsize=7,pad=2)
        if int(years[t])!=y: ax.text(0.03,0.03,str(years[t]),transform=ax.transAxes,fontsize=5,color='#ffffff',bbox=dict(fc='#000000',alpha=0.5,lw=0,pad=1))
        if k==0: axes_all[i,0].text(0.0,0.5,textwrap.fill(name,15)+'\n'+textwrap.fill(lab,15),transform=axes_all[i,0].transAxes,ha='left',va='center',fontsize=5.6,linespacing=1.25)
    # scale bar on last column: window is ~3.5 km; crop side*30 m
    axes[i,-1].plot([0.62,0.62+1000/(side*30)],[0.06,0.06],transform=axes[i,-1].transAxes,color='k',lw=1)
    axes[i,-1].text(0.62,0.09,'1 km',transform=axes[i,-1].transAxes,fontsize=4.5)
fig.savefig(f'{OUT}/fig4_belt_panels.png',bbox_inches='tight'); print('ok')
