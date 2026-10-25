"""L7 ETM+ vs L8 OLI same-season check (25 Oct 2026).
Reads ~/Downloads/SITE_pair.bin (from window.__pair in the GEE tab: L8 and L7 scenes 1-16 days apart, 2014-2021 seasons)
and the site AOI from sites/lowflow/SITE_lowflow.npz. Classifies both scenes with the site_lowflow.py rules
(water MNDWI>0; sand NDVI<0.25; vegetation NDVI>=0.30) on pixels valid in both, inside the AOI.
Usage: python3 scripts/pair_test.py SITE [...]  -> appends rows to sites/lowflow/pair_test.csv"""
import sys, io, json, csv, os, numpy as np
DL=os.environ.get('DOWNLOADS', os.path.expanduser('~/mnt/Downloads'))
out='sites/lowflow/pair_test.csv'; new=not os.path.exists(out)
f=open(out,'a',newline=''); w=csv.writer(f)
if new: w.writerow(['site','season','l8_date','l7_date','valid_ha','water_l8','water_l7','sand_l8','sand_l7','veg_l8','veg_l7','ndvi_med_l8','ndvi_med_l7','ndvi_diff_med'])
for sid in sys.argv[1:]:
    raw=open(f'{DL}/{sid}_pair.bin','rb').read(); nl=raw.index(b'\n'); man=json.loads(raw[:nl]); d=raw[nl+1:]
    arrs=[]; o=0
    for L in man['lens']: arrs.append(np.load(io.BytesIO(d[o:o+L]))); o+=L
    aoi=np.load(f'sites/lowflow/{sid}_lowflow.npz')['aoi']
    px=0.09
    def cls(a):
        c=np.stack([a[b] for b in man['bands']],-1).astype(float); nod=(c[...,0]==-32768)|(c[...,5]!=1)
        G,R,N,S1=[c[...,i]/1e4 for i in range(4)]
        with np.errstate(divide='ignore',invalid='ignore'): mn=(G-S1)/(G+S1); nd=(N-R)/(N+R)
        return nod,mn,nd
    sc=man['scenes']
    for i in range(0,len(sc),2):
        a8,a7=arrs[i],arrs[i+1]; m8,m7=sc[i],sc[i+1]
        n8,mn8,nd8=cls(a8); n7,mn7,nd7=cls(a7)
        if n8.shape!=aoi.shape: print(sid,'shape mismatch',n8.shape,aoi.shape); break
        ok=aoi&~n8&~n7
        def areas(mn,nd):
            wt=(mn>0)&ok; sd=(nd<0.25)&~(mn>0)&ok; vg=(nd>=0.30)&~(mn>0)&ok
            return wt.sum()*px, sd.sum()*px, vg.sum()*px
        A8=areas(mn8,nd8); A7=areas(mn7,nd7); s=ok&~(mn8>0)&~(mn7>0)
        w.writerow([sid,m8['season'],m8['date'],m7['date'],round(ok.sum()*px,1),round(A8[0],1),round(A7[0],1),round(A8[1],1),round(A7[1],1),round(A8[2],1),round(A7[2],1),
                    round(float(np.median(nd8[s])),3),round(float(np.median(nd7[s])),3),round(float(np.median(nd8[s]-nd7[s])),3)])
    print(sid,'done',len(sc)//2,'pairs')
f.close()
