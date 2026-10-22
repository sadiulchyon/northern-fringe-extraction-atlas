"""Onset summary across sites from SITE_series.csv (usable seasons only: no haze/partial flag).
Pettitt change point on low-flow water, sand and baseline-sand-now-water; direction and means before/after."""
import sys, csv, numpy as np
rows_out=[]
for sid in sys.argv[1:]:
    R=[r for r in csv.DictReader(open(f'sites/lowflow/{sid}_series.csv')) if r['flag']=='']
    y=np.array([int(r['season']) for r in R]); out={'site':sid,'n_seasons':len(R),'aoi_ha':R[0]['aoi_ha']}
    for k,lab in [('water_ha','water'),('sand_ha','sand'),('sand_to_water_ha','s2w')]:
        x=np.array([float(r[k]) for r in R]); n=len(x)
        U=np.array([np.sign(x[t:,None]-x[None,:t]).sum() for t in range(1,n)]); i=int(np.argmax(np.abs(U))); K=abs(U[i])
        p=min(1.0,2*np.exp(-6*K**2/(n**3+n**2)))
        out[f'{lab}_break']=int(y[i]); out[f'{lab}_before']=round(x[y<=y[i]].mean(),1); out[f'{lab}_after']=round(x[y>y[i]].mean(),1); out[f'{lab}_p']=float('%.2g'%p)
    rows_out.append(out)
w=csv.DictWriter(open('sites/lowflow/onset_summary.csv','w',newline=''),fieldnames=list(rows_out[0])); w.writeheader(); w.writerows(rows_out)
for o in rows_out:
    print(f"{o['site']} AOI {o['aoi_ha']} ha, n={o['n_seasons']}: water {o['water_before']}->{o['water_after']} after {o['water_break']} (p={o['water_p']}); "
          f"sand {o['sand_before']}->{o['sand_after']} after {o['sand_break']} (p={o['sand_p']}); s2w {o['s2w_before']}->{o['s2w_after']} after {o['s2w_break']} (p={o['s2w_p']})")
