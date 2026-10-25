"""Compare Pettitt breaks in sites/lowflow (original) and sites/lowflow_harm (TM/ETM+ harmonised to OLI). Writes sites/lowflow_harm/compare.csv."""
import csv, glob, numpy as np
cls={r['site']:r for r in csv.DictReader(open('maps/dash/site_results.csv'))}
def pet(d,k):
    R=[r for r in d if r['flag']=='']; y=np.array([int(r['season']) for r in R]); x=np.array([float(r[k]) for r in R]); n=len(x)
    U=np.array([np.sign(x[t:,None]-x[None,:t]).sum() for t in range(1,n)]); i=int(np.argmax(np.abs(U))); K=abs(U[i])
    p=min(1.0,2*np.exp(-6*K**2/(n**3+n**2))); return int(y[i]),round(x[y<=y[i]].mean()),round(x[y>y[i]].mean()),p
out=[]
for s in sorted(cls):
    try: a=list(csv.DictReader(open(f'sites/lowflow/{s}_series.csv'))); b=list(csv.DictReader(open(f'sites/lowflow_harm/{s}_series.csv')))
    except FileNotFoundError: continue
    r={'site':s,'type':cls[s]['type']}
    for k,kk in [('sand_ha','sand'),('veg_ha','veg_'),('water_ha','wate'),('sand_to_water_ha','s2w_')]:
        for tag,d in [('o',a),('h',b)]:
            y,bf,af,p=pet(d,k); r[f'{kk}_{tag}']=f'{bf}->{af}@{y}' ; r[f'{kk}_{tag}_p']=float('%.2g'%p)
    out.append(r)
w=csv.DictWriter(open('sites/lowflow_harm/compare.csv','w',newline=''),fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
import collections
def sig(r,k,t): return r[f'{k}_{t}_p']<0.05
for typ in sorted(set(r['type'] for r in out)):
    R=[r for r in out if r['type']==typ]
    def yr(r,k,t): return int(r[f'{k}_{t}'].split('@')[1])
    st=lambda k,t: sum(1 for r in R if sig(r,k,t) and yr(r,k,t) in (2012,2013))
    print(f"{typ:18s} n={len(R):3d} | sand sig o/h {sum(sig(r,'sand','o') for r in R)}/{sum(sig(r,'sand','h') for r in R)} break@2012-13 o/h {st('sand','o')}/{st('sand','h')} | veg_ sig o/h {sum(sig(r,'veg_','o') for r in R)}/{sum(sig(r,'veg_','h') for r in R)} @2012-13 {st('veg_','o')}/{st('veg_','h')} | water sig o/h {sum(sig(r,'wate','o') for r in R)}/{sum(sig(r,'wate','h') for r in R)} | s2w sig o/h {sum(sig(r,'s2w_','o') for r in R)}/{sum(sig(r,'s2w_','h') for r in R)}")
