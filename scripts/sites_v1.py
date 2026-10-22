"""Chapter 4, site table v1 (22 Oct 2026).
Clusters the 132 extraction records of the 411-point inventory (Sand Mining + Other extraction)
at 2 km (single linkage, great-circle distance) into sites. Each site gets an adaptive square
window: cluster extent + 600 m margin on each side, clamped to 1.5-5 km, in metres (UTM 46N).
Outputs: sites/sites_v1.csv, sites/sites_v1.geojson (windows + points), sites/sites_v1.kml.
Run from chapter-4/working.  No GEE needed.
"""
import csv, math, json, collections
rows=list(csv.DictReader(open('inventory_411_sectors.csv')))
ext=[r for r in rows if r['label_group'] in ('Sand Mining','Other extraction')]
# UTM 46N (EPSG:32646) forward projection, enough precision for windows
def utm46(lon,lat):
    a=6378137.0; f=1/298.257223563; k0=0.9996; lon0=math.radians(93.0)
    e2=f*(2-f); ep2=e2/(1-e2)
    phi=math.radians(lat); lam=math.radians(lon)
    N=a/math.sqrt(1-e2*math.sin(phi)**2); T=math.tan(phi)**2; C=ep2*math.cos(phi)**2; A=math.cos(phi)*(lam-lon0)
    M=a*((1-e2/4-3*e2**2/64-5*e2**3/256)*phi-(3*e2/8+3*e2**2/32+45*e2**3/1024)*math.sin(2*phi)
         +(15*e2**2/256+45*e2**3/1024)*math.sin(4*phi)-(35*e2**3/3072)*math.sin(6*phi))
    x=k0*N*(A+(1-T+C)*A**3/6+(5-18*T+T**2+72*C-58*ep2)*A**5/120)+500000
    y=k0*(M+N*math.tan(phi)*(A**2/2+(5-T+9*C+4*C**2)*A**4/24+(61-58*T+T**2+600*C-330*ep2)*A**6/720))
    return x,y
def inv46(x,y):
    a=6378137.0; f=1/298.257223563; k0=0.9996; lon0=math.radians(93.0)
    e2=f*(2-f); ep2=e2/(1-e2); e1=(1-math.sqrt(1-e2))/(1+math.sqrt(1-e2))
    M=(y)/k0; mu=M/(a*(1-e2/4-3*e2**2/64-5*e2**3/256))
    phi1=mu+(3*e1/2-27*e1**3/32)*math.sin(2*mu)+(21*e1**2/16-55*e1**4/32)*math.sin(4*mu)+(151*e1**3/96)*math.sin(6*mu)
    N1=a/math.sqrt(1-e2*math.sin(phi1)**2); T1=math.tan(phi1)**2; C1=ep2*math.cos(phi1)**2
    R1=a*(1-e2)/(1-e2*math.sin(phi1)**2)**1.5; D=(x-500000)/(N1*k0)
    phi=phi1-(N1*math.tan(phi1)/R1)*(D**2/2-(5+3*T1+10*C1-4*C1**2-9*ep2)*D**4/24+(61+90*T1+298*C1+45*T1**2-252*ep2-3*C1**2)*D**6/720)
    lam=lon0+(D-(1+2*T1+C1)*D**3/6+(5-2*C1+28*T1-3*C1**2+8*ep2+24*T1**2)*D**5/120)/math.cos(phi1)
    return math.degrees(lam),math.degrees(phi)
for r in ext:
    r['x'],r['y']=utm46(float(r['lon']),float(r['lat']))
n=len(ext); lab=list(range(n))
def find(i):
    while lab[i]!=i: lab[i]=lab[lab[i]]; i=lab[i]
    return i
for i in range(n):
    for j in range(i+1,n):
        if math.hypot(ext[i]['x']-ext[j]['x'],ext[i]['y']-ext[j]['y'])<=2000: lab[find(i)]=find(j)
groups=collections.defaultdict(list)
for i in range(n): groups[find(i)].append(ext[i])
# order sites west to east
sites=sorted(groups.values(), key=lambda g: sum(float(r['lon']) for r in g)/len(g))
MARGIN=600; WMIN=1500; WMAX=5000
out=[]; feats=[]
def pick(vals):
    vals=[v for v in vals if v]
    return collections.Counter(vals).most_common(1)[0][0] if vals else ''
for k,g in enumerate(sites,1):
    sid=f'E{k:03d}'
    xs=[r['x'] for r in g]; ys=[r['y'] for r in g]
    cx=(min(xs)+max(xs))/2; cy=(min(ys)+max(ys))/2
    ext_m=max(max(xs)-min(xs),max(ys)-min(ys))
    w=min(WMAX,max(WMIN,ext_m+2*MARGIN))
    w=round(w/100)*100
    lon,lat=inv46(cx,cy)
    yrs=sorted({r['desc_year_max'][:4] for r in g if r['desc_year_max']})
    inten=[r['intensity'] for r in g if r['intensity']]
    rank={'Minor':1,'Moderate':2,'Moderate/Extensive':3,'Extensive':4}
    imax=max(inten,key=lambda v:rank.get(v,0)) if inten else ''
    rec=dict(site_id=sid,n_rec=len(g),lon=round(lon,5),lat=round(lat,5),window_m=int(w),extent_m=int(round(ext_m)),
             sector=pick([r['sector'] for r in g]),admin0=pick([r['admin0'] for r in g]),admin1=pick([r['admin1'] for r in g]),
             dist_border_km=round(sum(float(r['dist_border_km']) for r in g)/len(g),1),
             zone=pick([r['zone'] for r in g]),intensity_max=imax,setting=pick([r['setting'] for r in g]),
             desc_years=';'.join(yrs),rids=';'.join(r['rid'] for r in g),
             names=';'.join(sorted({r['name'] for r in g if r['name'].strip().lower() not in ('sand mining',)}))[:80],
             west=round(inv46(cx-w/2,cy)[0],5),east=round(inv46(cx+w/2,cy)[0],5),
             south=round(inv46(cx,cy-w/2)[1],5),north=round(inv46(cx,cy+w/2)[1],5))
    out.append(rec)
    ring=[inv46(cx-w/2,cy-w/2),inv46(cx+w/2,cy-w/2),inv46(cx+w/2,cy+w/2),inv46(cx-w/2,cy+w/2),inv46(cx-w/2,cy-w/2)]
    feats.append(dict(type='Feature',properties={k2:v for k2,v in rec.items() if k2 not in('west','east','south','north')},
                      geometry=dict(type='Polygon',coordinates=[[list(p) for p in ring]])))
    for r in g:
        feats.append(dict(type='Feature',properties=dict(site_id=sid,rid=r['rid'],name=r['name'],desc=r['desc'].replace('\n',' | ')),
                          geometry=dict(type='Point',coordinates=[float(r['lon']),float(r['lat'])])))
with open('sites/sites_v1.csv','w',newline='') as f:
    wr=csv.DictWriter(f,fieldnames=list(out[0].keys())); wr.writeheader(); wr.writerows(out)
json.dump(dict(type='FeatureCollection',features=feats),open('sites/sites_v1.geojson','w'))
# KML: windows + points, for Google Earth historical imagery
kml=['<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>Ch4 sites v1</name>',
     '<Style id="w"><LineStyle><color>ff00ffff</color><width>2</width></LineStyle><PolyStyle><fill>0</fill></PolyStyle></Style>',
     '<Style id="p"><IconStyle><scale>0.7</scale><color>ff0000ff</color></IconStyle></Style>']
for ft in feats:
    p=ft['properties']
    if ft['geometry']['type']=='Polygon':
        coords=' '.join(f'{x},{y},0' for x,y in ft['geometry']['coordinates'][0])
        kml.append(f'<Placemark><name>{p["site_id"]} ({p["sector"]}, {p["n_rec"]} rec, {p["window_m"]} m)</name><styleUrl>#w</styleUrl><Polygon><outerBoundaryIs><LinearRing><coordinates>{coords}</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>')
    else:
        x,y=ft['geometry']['coordinates']
        kml.append(f'<Placemark><name>{p["site_id"]} rid {p["rid"]}</name><description>{p["name"]}: {p["desc"]}</description><styleUrl>#p</styleUrl><Point><coordinates>{x},{y},0</coordinates></Point></Placemark>')
kml.append('</Document></kml>')
open('sites/sites_v1.kml','w').write('\n'.join(kml))
print(len(out),'sites written')
print('window sizes:',collections.Counter(r['window_m'] for r in out))
print('by sector:',collections.Counter(r['sector'] for r in out))
print('by country:',collections.Counter(r['admin0'] for r in out))
print('multi-record sites:',sum(1 for r in out if r['n_rec']>1))
