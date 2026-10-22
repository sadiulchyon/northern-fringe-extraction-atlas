import csv, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

rows = list(csv.DictReader(open('results/inventory_sites_c3_v1.csv')))
years = [y for y in range(1988, 2026) if y != 2007]
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8.5, 'axes.spines.top': False,
                     'axes.spines.right': False, 'axes.edgecolor': '#52514e',
                     'xtick.color': '#52514e', 'ytick.color': '#52514e'})
fig = plt.figure(figsize=(7.4, 6.4))
a = fig.add_axes([0.09, 0.70, 0.86, 0.23])
secs = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']
tot = [sum(r['sector'] == s for r in rows) for s in secs]
det = [sum(r['sector'] == s and int(r['seasons_detected']) > 0 for r in rows) for s in secs]
x = np.arange(6)
a.bar(x, tot, 0.6, color='#cfd8e3', label='known extraction records')
a.bar(x, det, 0.6, color='#2a78d6', label='detected in at least 1 season')
for i in range(6):
    a.text(i, tot[i] + 1, f'{det[i]} / {tot[i]}', ha='center', fontsize=8, color='#0b0b0b')
a.set_xticks(x, ['S1 (west)', 'S2', 'S3', 'S4', 'S5', 'S6 (northeast)'])
a.set_ylim(0, 52); a.set_ylabel('records')
a.legend(frameon=False, loc='upper center', bbox_to_anchor=(0.62, 1.0), fontsize=8)
a.set_title('(a) Inventory extraction records (2021-22) with mapped excavated ground within 500 m, 1988-2025',
            loc='left', fontsize=9)
b = fig.add_axes([0.13, 0.08, 0.76, 0.52])
d = [r for r in rows if r['sector'] == 'S6' and int(r['seasons_detected']) > 0]
d.sort(key=lambda r: float(r['lon']))
M = np.array([[float(r[f'ha_{y}']) for y in years] for r in d])
cmap = LinearSegmentedColormap.from_list('b', ['#dbe8f8', '#9ec5f4', '#3987e5', '#1c5cab', '#0d366b'])
im = b.imshow(np.ma.masked_equal(M, 0), aspect='auto', cmap=cmap, vmin=0, vmax=6, interpolation='nearest')
b.set_facecolor('#f4f4f2')
b.set_yticks(range(len(d)), [f"#{r['rid']}  {float(r['lon']):.2f} E, {float(r['lat']):.2f} N" for r in d], fontsize=7)
xt = [i for i, y in enumerate(years) if y % 5 == 0]
b.set_xticks(xt, [years[i] for i in xt])
b.set_title('(b) S6 records with detections: mapped excavated ground within 500 m (ha), west (top) to east',
            loc='left', fontsize=9)
cax = fig.add_axes([0.905, 0.08, 0.015, 0.52])
fig.colorbar(im, cax=cax).set_label('ha (blank = none)')
fig.text(0.01, 0.005, 'v1 classification + rules R1-R3 (patch at least 5 cells); 2007 missing. Before error adjustment.',
         fontsize=7, color='#52514e')
fig.savefig('figs/ch4_fig_known_sites_detection_v1.png', dpi=300)
