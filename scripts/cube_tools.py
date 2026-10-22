"""Chapter 4 site cubes: load, convert and render.
Cube file (from the Earth Engine editor): one JSON manifest line, then 38 concatenated NPY arrays
(structured, one field per band). Values are reflectance and indices x 10,000 as stored in ch4/ls_dry;
masked pixels (outside the corridor mask or no observation) are -32768.
"""
import json, io, csv, math, numpy as np
NODATA = -32768

def load_bin(fn):
    raw = open(fn, 'rb').read()
    nl = raw.index(b'\n'); man = json.loads(raw[:nl]); data = raw[nl + 1:]
    o = 0; arrs = []
    for L in man['lens']:
        arrs.append(np.load(io.BytesIO(data[o:o + L]))); o += L
    cube = np.stack([np.stack([a[b] for b in man['bands']], axis=-1) for a in arrs])
    return cube, np.array(man['years']), list(man['bands']), man['region'], man

def to_npz(fn, out):
    cube, years, bands, region, man = load_bin(fn)
    np.savez_compressed(out, cube=cube, years=years, bands=np.array(bands), region=np.array(region))
    return cube, years, bands, region

def load_npz(fn):
    d = np.load(fn)
    return d['cube'], d['years'], list(d['bands']), list(d['region'])

def false_colour(cube, bands, combo=('SWIR1', 'NIR', 'RED'), pct=(2, 98)):
    """Fixed stretch over all years so panels are comparable. Returns img[y,r,c,3] in 0-1 and nodata mask."""
    nod = cube[..., bands.index('NDVI')] == NODATA
    rgb = np.stack([cube[..., bands.index(b)] for b in combo], axis=-1).astype(float) / 1e4
    rgb[nod] = np.nan
    lo = np.nanpercentile(rgb, pct[0], axis=(0, 1, 2)); hi = np.nanpercentile(rgb, pct[1], axis=(0, 1, 2))
    img = np.clip((rgb - lo) / (hi - lo), 0, 1); img[nod] = 0.5
    return img, nod

def chip_strip(cube, years, bands, region, title, out, points=(), cols=7, panel_in=2.6, combo=('SWIR1', 'NIR', 'RED')):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    W, S, E, N = region
    img, nod = false_colour(cube, bands, combo)
    nobs = cube[..., bands.index('NOBS')]
    ny, nr, nc = img.shape[:3]; rows = math.ceil(ny / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(cols * panel_in, rows * panel_in * nr / nc + 0.6))
    for ax in axes.flat: ax.axis('off')
    for i, ax in enumerate(axes.flat[:ny]):
        ax.imshow(img[i], extent=[W, E, S, N], interpolation='nearest')
        for lon, lat in points: ax.plot(lon, lat, 'o', mfc='none', mec='yellow', ms=7, mew=1.2)
        n = int(np.median(nobs[i][~nod[i]])) if (~nod[i]).any() else 0
        ax.set_title(f'{int(years[i])}  (n={n})', fontsize=10, pad=2); ax.set_xlim(W, E); ax.set_ylim(S, N)
    fig.suptitle(title, fontsize=11)
    plt.tight_layout(rect=[0, 0, 1, 0.97]); plt.savefig(out, dpi=100); plt.close(fig)
    return out

def site_points(inventory_csv, rids):
    rids = set(rids)
    return [(float(r['lon']), float(r['lat'])) for r in csv.DictReader(open(inventory_csv)) if r['rid'] in rids]
