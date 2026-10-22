"""Convert a per-site cube downloaded from the Earth Engine editor (manifest line + concatenated NPY chunks)
to a compressed npz: cube[year, row, col, band] int16, years, bands, region [W,S,E,N].  Usage: python3 cube_bin_to_npz.py FILE.bin"""
import sys, json, io, numpy as np
fn=sys.argv[1]; raw=open(fn,'rb').read()
nl=raw.index(b'\n'); man=json.loads(raw[:nl]); data=raw[nl+1:]
o=0; arrs=[]
for L in man['lens']:
    arrs.append(np.load(io.BytesIO(data[o:o+L]))); o+=L
cube=np.stack([np.stack([a[b] for b in man['bands']],axis=-1) for a in arrs])
out=fn.replace('.bin','.npz')
np.savez_compressed(out, cube=cube, years=np.array(man['years']), bands=np.array(man['bands']), region=np.array(man['region']))
print(out, cube.shape, 'NOBS median by year:', [int(np.median(cube[i,...,7])) for i in range(cube.shape[0])])
