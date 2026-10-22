# Chapter 4: the supply chain seen from Landsat: quarry, plant yard, crusher yards, port yard and sand-filled land, six Januaries each (true colour, bare ground overlay).
import csv, textwrap, numpy as np, matplotlib, os; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
H=os.path.dirname(os.path.abspath(__file__)); WK=os.path.join(H,'..','..','working'); OUT=os.path.join(H,'..')
plt.rcParams.update({"font.family":"Liberation Sans","font.size":6.5})
SITES=[('N39','Lafarge limestone mine, Nongtrai, India (S6)','Quarry 2004'),
       ('N42','Chhatak cement plant and limestone yard (S6)','Yard 2001'),
       ('N23','Bholaganj crusher yards (S6)','Yards 2005'),
       ('N32','Sonahat land port yards (S2)','Yards 2018'),
       ('N29','Dhanua-Kamalpur land port (S2)','Fill 2014'),
       ('N21','Sylhet Hi-Tech Park (S6)','Fill 2018'),
       ('N28','Jamalpur Economic Zone (S3)','Fill 2018')]
YRS=[1996,2002,2008,2014,2019,2024]
fig,axes_all=plt.subplots(len(SITES),len(YRS)+1,figsize=(6.7,7.6),dpi=300,gridspec_kw={'wspace':0.04,'hspace':0.06,'width_ratios':[0.85]+[1]*len(YRS)})
axes=axes_all[:,1:]
for a in axes_all[:,0]: a.axis('off')
for i,(sid,name,lab) in enumerate(SITES):
    d=np.load(f'{WK}/sites/lowflow/{sid}_lowflow.npz'); years=list(d['years'])
    flags={int(r['season']):r['flag'] for r in csv.DictReader(open(f'{WK}/sites/lowflow/{sid}_series.csv'))}
    tc=np.where(d['nod'][...,None],np.nan,d['true']); lo=np.nanpercentile(tc,2,axis=(0,1,2)); hi=np.nanpercentile(tc,98,axis=(0,1,2)); tc=np.clip((tc-lo)/(hi-lo),0,1)
    n0,n1=d['aoi'].shape; side=min(n0,n1); r0=(n0-side)//2; c0=(n1-side)//2; r1=r0+side; c1=c0+side
    for k,y in enumerate(YRS):
        ax=axes[i,k]
        usable=[yy for yy in years if flags.get(int(yy),)=='' and abs(int(yy)-y)<=2]
        if not usable: usable=[yy for yy in years if flags.get(int(yy),'')=='']
        t=years.index(min(usable,key=lambda yy:(abs(int(yy)-y)>0, d['nod'][years.index(yy)][r0:r1,c0:c1].mean(), abs(int(yy)-y))))
        ax.imshow(tc[t][r0:r1,c0:c1],interpolation='nearest')
        b=np.where(d['sand'][t][r0:r1,c0:c1]&~d['water'][t][r0:r1,c0:c1],1.0,np.nan)
        ax.imshow(b,cmap=ListedColormap(['#d6438f']),alpha=0.45,interpolation='nearest')
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values(): s.set_linewidth(0.3); s.set_edgecolor('#999999')
        if i==0: ax.set_title(f'Jan {y}',fontsize=7,pad=2)
        if int(years[t])!=y: ax.text(0.03,0.03,str(years[t]),transform=ax.transAxes,fontsize=5,color='#ffffff',bbox=dict(fc='#000000',alpha=0.5,lw=0,pad=1))
        if k==0: axes_all[i,0].text(0.0,0.5,textwrap.fill(name,15)+'\n'+textwrap.fill(lab,15),transform=axes_all[i,0].transAxes,ha='left',va='center',fontsize=5.6,linespacing=1.25)
    axes[i,-1].plot([0.55,0.55+1000/(side*30)],[0.06,0.06],transform=axes[i,-1].transAxes,color='k',lw=1)
    axes[i,-1].text(0.55,0.09,'1 km',transform=axes[i,-1].transAxes,fontsize=4.5)
fig.savefig(f'{OUT}/fig4_supply_panels.png',bbox_inches='tight'); print('ok')
