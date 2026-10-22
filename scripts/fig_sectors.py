import geopandas as gpd, pandas as pd, numpy as np, matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
g=gpd.read_file('out/inventory_411_spatial.gpkg')
br=[88.3,89.3,89.92,90.3,90.95,91.6,92.5]
lab=['S1 Panchagarh–Thakurgaon','S2 Teesta–Brahmaputra','S3 Sherpur (Garo W)','S4 Mymensingh–Netrakona (Garo E)','S5 Sunamganj (Shillong W)','S6 Sylhet (Shillong E)']
g['sector']=pd.cut(g.lon,br,labels=[l.split()[0] for l in lab])
g['zone']=np.where(g.dist_border_km<=10,'0–10 km',np.where(g.dist_border_km<=20,'10–20 km','>20 km'))
g.to_file('out/inventory_411_sectors.gpkg',driver='GPKG'); g.drop(columns='geometry').to_csv('out/inventory_411_sectors.csv',index=False)
ne=gpd.read_file('ne/ne_10m_admin_0_countries.shp'); riv=gpd.read_file('ne/ne_10m_rivers_lake_centerlines.shp')
bb=(88.0,24.6,92.7,26.9)
cols={'Sand Mining':'#c0392b','Other extraction':'#e67e22','Deposit/depot':'#d4ac0d','Vessels':'#2471a3','River/floodplain':'#17a589','Named feature':'#7f8c8d','Uncertain label':'#bbbbbb'}
fig=plt.figure(figsize=(11,7.2))
ax=fig.add_axes([0.04,0.30,0.92,0.66])
ne.cx[bb[0]:bb[2],bb[1]:bb[3]].plot(ax=ax,color='#f2f0eb',edgecolor='#999',lw=0.6)
ne[ne.ADM0_A3=='BGD'].plot(ax=ax,color='#fbfaf7',edgecolor='#555',lw=0.9)
riv.cx[bb[0]:bb[2],bb[1]:bb[3]].plot(ax=ax,color='#8db4d6',lw=0.7)
for k,c in cols.items():
    s=g[g.label_group==k]; ax.scatter(s.lon,s.lat,s=12,c=c,edgecolor='white',lw=0.3,label=f'{k} ({len(s)})',zorder=3)
for i in range(6):
    ax.axvline(br[i+1],color='#444',ls=':',lw=0.6) if i<5 else None
    ax.text((br[i]+br[i+1])/2 if i else 88.75,26.8,lab[i].split()[0],ha='center',fontsize=10,weight='bold')
ax.text(90.2,24.7,'Bangladesh',color='#666',fontsize=9); ax.text(91.3,25.6,'Meghalaya (India)',color='#666',fontsize=9)
ax.set_xlim(bb[0],bb[2]); ax.set_ylim(bb[1],bb[3]); ax.set_aspect(1/np.cos(np.radians(25.7)))
ax.legend(loc='lower left',fontsize=8,frameon=True); ax.tick_params(labelsize=8)
ax.set_title('Reconnaissance inventory (411 records) by sector along the northern border — working figure',fontsize=10,loc='left')
ax2=fig.add_axes([0.07,0.05,0.55,0.19])
ct=pd.crosstab(g.sector,g.label_group)[list(cols)]
bottom=np.zeros(len(ct))
for k in cols: ax2.bar(ct.index.astype(str),ct[k],bottom=bottom,color=cols[k]); bottom+=ct[k].values
ax2.set_ylabel('Records',fontsize=8); ax2.tick_params(labelsize=8); ax2.spines[['top','right']].set_visible(False)
ax3=fig.add_axes([0.70,0.05,0.27,0.19])
ax3.hist(g.dist_border_km.clip(-5,40),bins=np.arange(-5,41,2.5),color='#555'); ax3.axvline(0,color='k',lw=0.6)
ax3.set_xlabel('Distance inside border (km; NE 1:10m)',fontsize=8); ax3.tick_params(labelsize=8); ax3.spines[['top','right']].set_visible(False)
fig.savefig('out/ch4_working_inventory_sectors.png',dpi=170)
print(ct.assign(total=ct.sum(1)).to_string())
print(pd.crosstab(g.sector,g.zone))
