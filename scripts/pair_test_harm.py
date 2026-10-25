"""Same as pair_test.py but L7 bands transformed to OLI with Roy et al. (2016, RSE 185:57-70) ETM+->OLI OLS coefficients.
Prints per-site median NDVI difference (L8 - L7) and sand/veg ratios before and after, excluding pairs where one scene is hazy
(|NDVI diff| > 0.15 or L7 veg = 0)."""
import sys, io, json, os, numpy as np
DL=os.environ.get('DOWNLOADS', os.path.expanduser('~/mnt/Downloads'))
SL=[0.8483,0.9047,0.8462,0.8937,0.9071]; IC=[0.0088,0.0061,0.0412,0.0254,0.0172]  # GREEN RED NIR SWIR1 SWIR2
def load(sid):
    raw=open(f'{DL}/{sid}_pair.bin','rb').read(); nl=raw.index(b'\n'); man=json.loads(raw[:nl]); d=raw[nl+1:]; arrs=[]; o=0
    for L in man['lens']: arrs.append(np.load(io.BytesIO(d[o:o+L]))); o+=L
    return man,arrs
def idx(a,man,harm=False):
    c=np.stack([a[b] for b in man['bands']],-1).astype(float); nod=(c[...,0]==-32768)|(c[...,5]!=1)
    B=[c[...,i]/1e4 for i in range(5)]
    if harm: B=[IC[i]+SL[i]*B[i] for i in range(5)]
    G,R,N,S1,_=B
    with np.errstate(divide='ignore',invalid='ignore'): return nod,(G-S1)/(G+S1),(N-R)/(N+R)
tot={}
for sid in sys.argv[1:]:
    man,arrs=load(sid); aoi=np.load(f'sites/lowflow/{sid}_lowflow.npz')['aoi']; res=[]
    for i in range(0,len(arrs),2):
        n8,m8,d8=idx(arrs[i],man); n7,m7,d7=idx(arrs[i+1],man); _,m7h,d7h=idx(arrs[i+1],man,True)
        ok=aoi&~n8&~n7; s=ok&~(m8>0)&~(m7>0)
        diff=np.median(d8[s]-d7[s]); difh=np.median(d8[s]-d7h[s])
        sd=lambda m,d:((d<0.25)&~(m>0)&ok).sum(); vg=lambda m,d:((d>=0.30)&~(m>0)&ok).sum()
        if abs(diff)>0.15 or vg(m7,d7)==0: continue
        res.append((diff,difh,sd(m8,d8)/max(sd(m7,d7),1),sd(m8,d8)/max(sd(m7h,d7h),1),vg(m8,d8)/max(vg(m7,d7),1),vg(m8,d8)/max(vg(m7h,d7h),1)))
    r=np.array(res); tot[sid]=r
    print(sid,len(r),'pairs | NDVI L8-L7 %.3f -> %.3f | sand L8/L7 %.2f -> %.2f | veg L8/L7 %.2f -> %.2f'%tuple(np.median(r,0)))
a=np.vstack(list(tot.values()))
print('ALL',len(a),'pairs | NDVI L8-L7 %.3f -> %.3f | sand L8/L7 %.2f -> %.2f | veg L8/L7 %.2f -> %.2f'%tuple(np.median(a,0)))
