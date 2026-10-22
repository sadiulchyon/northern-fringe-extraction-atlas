import geopandas as gpd, pandas as pd, numpy as np
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree
g=gpd.read_file('out/inventory_411.gpkg')
ne=gpd.read_file('ne/ne_10m_admin_0_countries.shp')
adm1=gpd.read_file('ne/ne_10m_admin_1_states_provinces.shp')
bgd=ne[ne.ADM0_A3=='BGD'].to_crs(32646); ind=ne[ne.ADM0_A3=='IND'].to_crs(32646)
gp=g.to_crs(32646)
border=bgd.geometry.iloc[0].boundary.intersection(ind.geometry.iloc[0].buffer(50))
gp['in_bgd_ne']=gp.within(bgd.geometry.iloc[0])
d=gp.distance(border)/1000
gp['dist_border_km']=np.where(gp.in_bgd_ne,d,-d)
a1=adm1[adm1.adm0_a3.isin(['BGD','IND'])][['name','adm0_a3','geometry']].rename(columns={'name':'a1name'})
j=gpd.sjoin(g,a1,how='left',predicate='within')
gp['admin1']=j['a1name'].values; gp['admin0']=j['adm0_a3'].values
print(gp.admin1.value_counts(dropna=False))
print(gp.dist_border_km.describe()); print(np.percentile(gp.dist_border_km,[5,25,50,75,90,95,99]))
xy=np.c_[gp.geometry.x,gp.geometry.y]; t=cKDTree(xy)
for r in [1000,2000,3000,5000,10000]:
    m=t.sparse_distance_matrix(t,r); n,lab=connected_components(m>0 if False else (m!=0)+0,directed=False) if False else connected_components(t.sparse_distance_matrix(t,r).tocsr(),directed=False)
    print(r,'m ->',n,'groups; singletons',(np.bincount(lab)==1).sum())
n,lab=connected_components(t.sparse_distance_matrix(t,5000).tocsr(),directed=False)
gp['cl5']=lab
rows=[]
for c,s in gp.groupby('cl5'):
    named=[x for x in s.name if s.label_group[s.name==x].iloc[0] in ('River/floodplain','Named feature')]
    rows.append(dict(cl=c,n=len(s),lon=round(s.geometry.to_crs(4326).x.mean(),3),lat=round(s.geometry.to_crs(4326).y.mean(),3),
        admin1=s.admin1.mode().iloc[0] if s.admin1.notna().any() else '',
        sm=(s.label_group=='Sand Mining').sum(),ves=(s.label_group=='Vessels').sum(),dep=(s.label_group=='Deposit/depot').sum(),
        dmed=round(s.dist_border_km.median(),1),names='; '.join(sorted(set(named)))[:120],
        yrs=f"{int(np.nanmin(s.desc_year_max)) if s.desc_year_max.notna().any() else ''}-{int(np.nanmax(s.desc_year_max)) if s.desc_year_max.notna().any() else ''}"))
cl=pd.DataFrame(rows).sort_values('lon')
pd.set_option('display.width',250); pd.set_option('display.max_colwidth',120); pd.set_option('display.max_rows',200)
print(cl.to_string(index=False))
gp.to_crs(4326).to_file('out/inventory_411_spatial.gpkg',driver='GPKG')
