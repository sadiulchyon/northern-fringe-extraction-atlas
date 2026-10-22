# Figure: annual mapped excavated ground by sector (v1b), from results/c3_area_by_sector_v1b.csv
import csv, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
rows = list(csv.DictReader(open('results/c3_area_by_sector_v1b.csv')))
yr = [int(r['season']) for r in rows]
fig, (a, b) = plt.subplots(2, 1, figsize=(7.2, 5.2), sharex=True, gridspec_kw={'height_ratios': [2.2, 1]})
a.plot(yr, [float(r['S6_km2']) for r in rows], color='#2a78d6', lw=2, marker='o', ms=4)
a.set_ylabel('Mapped excavated ground (km2)'); a.set_title('(a) Sector 6', loc='left')
for i, c in zip(range(1, 6), ['#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#6250d6']):
    b.plot(yr, [float(r[f'S{i}_km2']) for r in rows], color=c, lw=1.6, label=f'S{i}')
b.set_ylabel('km2'); b.legend(ncol=5, frameon=False); b.set_title('(b) Sectors 1 to 5', loc='left')
fig.tight_layout(); fig.savefig('figures/ch4_fig_c3_area_series_v1b.png', dpi=300)
