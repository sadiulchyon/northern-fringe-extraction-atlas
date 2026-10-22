"""print __runSites list for sites: python3 scripts/windows.py HALF_KM SITE..."""
import csv,math,json,sys
h=float(sys.argv[1]); r={x['site_id']:x for x in list(csv.DictReader(open('sites/sites_v1.csv')))+list(csv.DictReader(open('sites/sites_extra.csv')))}
o=[]
for s in sys.argv[2:]:
    x=r[s]; lo=float(x['lon']);la=float(x['lat']); hh=max(h,float(x['window_m'])/2000)
    dl=hh/111.32; dn=hh/(111.32*math.cos(math.radians(la)))
    o.append([s,round(lo-dn,5),round(la-dl,5),round(lo+dn,5),round(la+dl,5)])
print(json.dumps(o))
