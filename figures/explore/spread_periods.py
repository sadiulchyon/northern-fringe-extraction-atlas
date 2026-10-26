# Exploratory: spatio-temporal development of dated extraction-type sites (cumulative by period). Not a chapter figure.
import csv, json, os
from collections import defaultdict
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
B=os.path.join(os.path.dirname(__file__),'..','..','working')
res={r['site']:r for r in csv.DictReader(open(f'{B}/maps/dash/site_results.csv'))}
st={}
for fn in ['sites/sites_v1.csv','sites/sites_extra.csv']:
    for r in csv.DictReader(open(f'{B}/{fn}')): st[r['site_id']]=(float(r['lon']),float(r['lat']))
countries=json.load(open(f'{B}/maps/dash/atlas_source/countries.json')); rivers=json.load(open(f'{B}/maps/dash/atlas_source/rivers.json'))
def xy(s): return zip(*[tuple(map(float,p.split(','))) for p in s.split(';')])
EXT={'Pit extraction':('#b2182b','o'),'Floodplain pits':('#e08214','s'),'Possible dredging':('#2166ac','D'),'Bar loss':('#762a83','^')}
SUP={'Depot / stockpile':('#a6761d','P'),'Land filling':('#d6438f','X')}
P=[(1980,1999,'before 2000'),(2000,2004,'2000–2004'),(2005,2009,'2005–2009'),(2010,2014,'2010–2014'),(2015,2019,'2015–2019'),(2020,2025,'2020–2025')]
pts=[(s,st[s],r['type'],int(r['visual_onset'][:4])) for s,r in res.items() if r['visual_onset'][:4].isdigit() and s in st and (r['type'] in EXT or r['type'] in SUP)]
plt.rcParams.update({"font.family":"Liberation Sans","font.size":6.5})
fig,axs=plt.subplots(2,3,figsize=(9.6,5.0),dpi=220)
cnt=defaultdict(int)
for ax,(a,b,lab) in zip(axs.flat,P):
    for c in countries:
        for ring in c['rings'].split('|'):
            x,y=xy(ring); ax.fill(x,y,color='#f0f0f0' if c['country']=='BGD' else '#fafafa',lw=0); ax.plot(x,y,color='#999999',lw=0.4)
    for r in rivers:
        if r['class']>=2: x,y=xy(r['coords']); ax.plot(x,y,color='#9ecae1',lw={2:0.5,3:1.1}[r['class']])
    old=[p for p in pts if p[3]<a]; new=[p for p in pts if a<=p[3]<=b]
    ax.scatter([p[1][0] for p in old],[p[1][1] for p in old],s=7,c='#bbbbbb',lw=0,zorder=4)
    for t,(col,mk) in {**EXT,**SUP}.items():
        q=[p for p in new if p[2]==t]
        ax.scatter([p[1][0] for p in q],[p[1][1] for p in q],s=22,c=col,marker=mk,edgecolors='#222222',linewidths=0.4,zorder=5,label=t)
    ne=sum(1 for p in new if p[2] in EXT); ns=sum(1 for p in new if p[2] in SUP)
    ax.set_title(f'{lab}: {ne} extraction, {ns} depot/fill new ({len(old)+len(new)} total)',fontsize=7)
    ax.set_xlim(88.25,92.5); ax.set_ylim(23.6,26.95); ax.set_aspect(1/0.9); ax.set_xticks([]); ax.set_yticks([])
h,l=axs.flat[0].get_legend_handles_labels()
fig.legend(*[x for x in zip(*{k:v for v,k in zip(*axs.flat[1].get_legend_handles_labels())}.items())][::-1] if False else axs.flat[1].get_legend_handles_labels(),loc='lower center',ncol=6,fontsize=6.5,frameon=False)
fig.tight_layout(rect=(0,0.05,1,1)); fig.savefig(os.path.join(os.path.dirname(__file__),'spread_periods.png'))
# table by sector and period (extraction-type only)
sec=lambda x:'S1' if x<89.30 else 'S2' if x<89.92 else 'S3' if x<90.30 else 'S4' if x<90.95 else 'S5' if x<91.60 else 'S6'
print('sector '+' '.join(l for _,_,l in P))
for S in ['S1','S2','S3','S4','S5','S6']:
    print(S,' '.join(str(sum(1 for p in pts if p[2] in EXT and sec(p[1][0])==S and a<=p[3]<=b)) for a,b,_ in P))
print('fills/depots',' '.join(str(sum(1 for p in pts if p[2] in SUP and a<=p[3]<=b)) for a,b,_ in P))
