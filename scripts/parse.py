import re,html,json,sys
import geopandas as gpd, pandas as pd, numpy as np
from shapely.geometry import Point
def parse(k):
    s=open(k,encoding='utf-8').read()
    rows=[]
    for i,p in enumerate(re.findall(r'<Placemark>.*?</Placemark>',s,re.S)):
        n=html.unescape(re.sub(r'\s+',' ',(re.search(r'<name>(.*?)</name>',p,re.S) or [0,''])[1]).strip())
        m=re.search(r'<description>(.*?)</description>',p,re.S); d=html.unescape(m.group(1)).strip() if m else ''
        c=re.search(r'<Point>.*?<coordinates>(.*?)</coordinates>',p,re.S).group(1).strip().split(',')
        w=re.search(r'<when>(.*?)</when>',p); w=w.group(1) if w else ''
        rows.append(dict(rid=i+1,name=n,desc=d,lon=float(c[0]),lat=float(c[1]),ge_view=w))
    return pd.DataFrame(rows)
df=parse('in/Sand Mining Locations(V1)/doc.kml')
# observed month/year in description
def md(d):
    m=re.findall(r'(\d{1,2})/(\d{2,4})',d)
    out=[]
    for a,b in m:
        y=int(b); y=y+2000 if y<100 else y
        if 1990<y<2030: out.append((y,int(a)))
    return out
df['desc_dates']=df.desc.apply(lambda d:';'.join(f'{y}-{m:02d}' for y,m in md(d)))
df['desc_year_max']=df.desc.apply(lambda d:max([y for y,_ in md(d)],default=np.nan))
def inten(t):
    t=t.lower()
    if 'extens' in t or 'extesn' in t: return 'Extensive' if 'moderate/' not in t else 'Moderate/Extensive'
    if 'moder' in t or 'modedr' in t: return 'Moderate'
    if 'minor' in t: return 'Minor'
    return ''
df['intensity']=df.desc.apply(inten)
def setting(t):
    t=t.lower(); r='river' in t or 'riverbed' in t; f='floodplain' in t
    return 'river+floodplain' if r and f else 'river' if r else 'floodplain' if f else ''
df['setting']=df.desc.apply(setting)
def grp(n):
    l=n.lower()
    if '?' in l: return 'Uncertain label'
    if l=='sand mining': return 'Sand Mining'
    if any(k in l for k in ['mining','pumping','miing','quarry']): return 'Other extraction'
    if any(k in l for k in ['ship','boat','vessel']): return 'Vessels'
    if any(k in l for k in ['deposit','depot']): return 'Deposit/depot'
    if any(k in l for k in ['river','khal','floodplain','nodi']): return 'River/floodplain'
    return 'Named feature'
df['label_group']=df.name.apply(grp)
g=gpd.GeoDataFrame(df,geometry=[Point(x,y) for x,y in zip(df.lon,df.lat)],crs=4326)
g.to_file('out/inventory_411.gpkg',driver='GPKG')
df.to_csv('out/inventory_411.csv',index=False)
print(df.label_group.value_counts()); print(df.intensity.value_counts()); print(df.desc_year_max.value_counts().sort_index())
