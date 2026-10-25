# Chapter 4 figures from the low-flow site atlas: site map by result class, and onset/spread.
# Inputs: chapter-4/working/maps/dash/{sites.csv,site_results.csv,inventory.csv,atlas_source/{countries,rivers}.json}
import csv, json, re, statistics as st
from collections import Counter, defaultdict
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
import os
W=os.path.join(os.path.dirname(__file__),'..','..','working','maps','dash'); OUT=os.path.join(os.path.dirname(__file__),'..')
plt.rcParams.update({"font.family":"Liberation Sans","font.size":7,"axes.linewidth":0.5,"axes.edgecolor":"#777777","xtick.color":"#444444","ytick.color":"#444444"})
INK="#222222"; MUTED="#666666"
CLS=[('Pit extraction','#b2182b','o'),('Floodplain pits','#e08214','s'),('Possible dredging','#2166ac','D'),('Bar loss','#762a83','^'),('Bar vegetation','#4d9221','v'),('Depot / stockpile','#a6761d','P'),('Land filling','#d6438f','X'),('No signal','#ffffff','o')]
EXT=('Pit extraction','Floodplain pits','Possible dredging','Bar loss'); SUP=('Depot / stockpile','Land filling')
COL={c:k for c,k,_ in CLS}; MK={c:m for c,_,m in CLS}
res={r['site']:r for r in csv.DictReader(open(f'{W}/site_results.csv'))}
sites={r['site_id']:r for r in csv.DictReader(open(f'{W}/sites.csv')) if r['site_id'] in res}
inv=list(csv.DictReader(open(f'{W}/inventory.csv')))
countries=json.load(open(f'{W}/atlas_source/countries.json')); rivers=json.load(open(f'{W}/atlas_source/rivers.json'))
def xy(s): return zip(*[tuple(map(float,p.split(','))) for p in s.split(';')])
# ---------- Figure A: map ----------
fig,ax=plt.subplots(figsize=(6.7,3.6),dpi=300)
for c in countries:
    for ring in c['rings'].split('|'):
        x,y=xy(ring); ax.fill(x,y,color='#f0f0f0' if c['country']=='BGD' else '#fafafa',lw=0)
        ax.plot(x,y,color='#888888',lw=0.5)
for r in rivers:
    x,y=xy(r['coords']); ax.plot(x,y,color='#9ecae1',lw={1:0.4,2:0.8,3:1.6}[r['class']],solid_capstyle='round')
ax.scatter([float(p['lon']) for p in inv],[float(p['lat']) for p in inv],s=1.2,c='#aaaaaa',lw=0,zorder=3)
for cls,col,mk in CLS:
    ids=[s for s in sites if res[s]['type']==cls]
    ax.scatter([float(sites[s]['lon']) for s in ids],[float(sites[s]['lat']) for s in ids],s=16 if cls!='No signal' else 11,c=col,marker=mk,edgecolors=INK if cls!='No signal' else '#888888',linewidths=0.4,zorder=5,label=f'{cls} ({len(ids)})')
# sector extents from site longitudes
sec=defaultdict(list)
for s,r in sites.items(): sec[r['sector']].append(float(r['lon']))
BANDS={'S1':(88.30,89.30),'S2':(89.30,89.92),'S3':(89.92,90.30),'S4':(90.30,90.95),'S5':(90.95,91.60),'S6':(91.60,92.40)}
for k,(lo,hi) in BANDS.items():
    ax.add_patch(Rectangle((lo+0.01,24.44),hi-lo-0.02,0.07,color='#555555',lw=0)); ax.text((lo+hi)/2,24.525,k,ha='center',va='bottom',fontsize=6.5,color=INK)
for nm,x,y in [('Teesta',89.22,25.92),('Brahmaputra',90.25,26.18),('Old Brahmaputra',90.35,25.0),('Surma',91.62,25.03),('Kushiyara',91.72,24.66),('Mahananda',88.32,25.85)]:
    ax.text(x,y,nm,fontsize=5.5,color='#4a7fa5',style='italic',ha='center')
ax.text(89.6,26.62,'INDIA',fontsize=7,color=MUTED); ax.text(91.5,25.62,'INDIA (Meghalaya)',fontsize=7,color=MUTED); ax.text(89.9,25.3,'BANGLADESH',fontsize=7,color=MUTED)
ax.set_xlim(88.2,92.5); ax.set_ylim(24.10,26.98); ax.set_aspect(1/0.9)
ax.set_xlabel('Longitude (°E)'); ax.set_ylabel('Latitude (°N)')
ax.legend(loc='lower left',bbox_to_anchor=(0.005,0.12),fontsize=6,frameon=True,framealpha=0.95,edgecolor='#cccccc',handletextpad=0.3,borderpad=0.4,title=f'Result at the {len(sites)} analysed sites',title_fontsize=6)
fig.tight_layout(); fig.savefig(f'{OUT}/fig4_sites_map.png'); plt.close(fig)
# ---------- Figure B: onset and spread ----------
rows=[]
for s,r in res.items():
    m=re.search(r'(19|20)\d\d',r['visual_onset'])
    if m: rows.append((float(sites[s]['lon']),int(m.group(0)),r['type'],sites[s]['sector'],s))
fig,(a1,a2)=plt.subplots(1,2,figsize=(6.7,3.3),dpi=300,gridspec_kw={'width_ratios':[2,1.15]})
for k,(lo,hi) in BANDS.items():
    a1.axvspan(lo,hi,color='#f3f3f3' if k in('S1','S3','S5') else '#e6e6e6',lw=0,zorder=0); a1.text((lo+hi)/2,2026.0,k,ha='center',fontsize=6.5,color=INK)
for y,lab in [(2010,'2010 Act'),(2014,'2014 Sylhet ban'),(2020,'2020 lease ban')]:
    a1.axhline(y,color='#bbbbbb',lw=0.5,ls=(0,(3,2)),zorder=1); a1.text(88.25,y+0.3,lab,ha='left',fontsize=5.2,color=MUTED)
for cls,col,mk in CLS:
    if cls=='No signal': continue
    pts=[(x,y) for x,y,c,_,_ in rows if c==cls]
    a1.scatter([p[0] for p in pts],[p[1] for p in pts],s=15,c=col,marker=mk,edgecolors=INK,linewidths=0.35,zorder=5,label=cls)
# sector medians for extraction-type classes (excluding bar vegetation)
for k in sorted(sec):
    ys=[y for x,y,c,sc,_ in rows if sc==k and c in EXT]
    if ys:
        lo,hi=BANDS[k]; lo+=0.04; hi-=0.06; med=st.median(ys)
        a1.plot([lo-0.02,hi+0.02],[med,med],color=INK,lw=1.1,zorder=6); a1.text(hi+0.03,med,f'{med:.0f}'.replace('.0',''),fontsize=5.5,va='center',color=INK)
a1.set_xlim(88.2,92.5); a1.set_ylim(1993,2027); a1.set_xlabel('Longitude (°E), west to east along the border'); a1.set_ylabel('First year of change (visual onset)')
a1.legend(fontsize=5.4,loc='upper center',bbox_to_anchor=(0.5,-0.17),frameon=False,handletextpad=0.2,columnspacing=0.8,ncol=4)
a1.text(0.01,0.985,'(a)',transform=a1.transAxes,fontsize=8,fontweight='bold',va='top')
# panel b: cumulative number of sites with a detected change (extraction-type classes), by sector
secs=['S1','S2','S3','S4','S5','S6']; yrs_ax=list(range(1994,2026))
styles={'S1':('#222222','-'),'S2':('#888888','--'),'S3':('#888888',':'),'S4':('#e08214','-'),'S5':('#b2182b','-'),'S6':('#2166ac','-')}
for k in secs:
    ys=[y for x,y,c,sc,_ in rows if sc==k and c in EXT]
    cum=[sum(1 for y in ys if y<=t) for t in yrs_ax]
    col,ls=styles[k]; a2.plot(yrs_ax,cum,color=col,ls=ls,lw=1.1,label=f'{k} (n = {len(ys)})')
ys=[y for x,y,c,sc,_ in rows if c in SUP]; a2.plot(yrs_ax,[sum(1 for y in ys if y<=t) for t in yrs_ax],color='#d6438f',ls=(0,(4,1.5)),lw=1.1,label=f'Depots and fill, all (n = {len(ys)})')
for y in (2010,2014,2020): a2.axvline(y,color='#bbbbbb',lw=0.5,ls=(0,(3,2)),zorder=0)
a2.set_xlim(1994,2025); a2.set_ylabel('Sites with detected change (cumulative)'); a2.set_xlabel('Dry season')
a2.spines[['top','right']].set_visible(False); a2.legend(fontsize=5.2,frameon=False,loc='upper left',bbox_to_anchor=(0.0,0.93)); a2.yaxis.get_major_locator().set_params(integer=True)
a2.text(0.02,0.985,'(b)',transform=a2.transAxes,fontsize=8,fontweight='bold',va='top')
fig.tight_layout(); fig.savefig(f'{OUT}/fig4_onset_spread.png'); plt.close(fig)
# ---------- numbers for the text ----------
print('classes',Counter(r['type'] for r in res.values()))
for k in secs:
    ys=sorted(y for x,y,c,sc,_ in rows if sc==k and c in EXT); print(k,len(ys),ys and st.median(ys),ys)
