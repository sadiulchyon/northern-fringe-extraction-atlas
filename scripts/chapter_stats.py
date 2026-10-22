import csv,re,statistics as st,collections as C
sec={}
for f in ['sites/sites_v1.csv','sites/sites_extra.csv']:
    for r in csv.DictReader(open(f)): sec[r['site_id']]=(r['sector'],float(r['lon']),r['admin0'])
rows=list(csv.DictReader(open('maps/dash/site_results.csv')))
classes=['Pit extraction','Floodplain pits','Possible dredging','Bar loss','Bar vegetation','Depot / stockpile','Land filling','No signal']
ext=classes[:4]
tab=C.defaultdict(C.Counter)
for r in rows: tab[sec[r['site']][0]][r['type']]+=1
print('n sites',len(rows), 'IND',sum(sec[r['site']][2]=='IND' for r in rows))
print('sector|'+'|'.join(classes)+'|Total')
for s in sorted(tab): print(s,'|'.join(str(tab[s][c]) for c in classes),sum(tab[s].values()),sep='|')
tot=C.Counter(r['type'] for r in rows); print('All',*[tot[c] for c in classes],len(rows),sep='|')
def y(v):
    m=re.search(r'(19|20)\d\d',v or ''); return int(m.group()) if m else None
d=[(r['site'],sec[r['site']][0],r['type'],y(r['visual_onset'])) for r in rows if r['type'] in ext and y(r['visual_onset'])]
print('dated ext',len(d))
dec=C.Counter('<2000' if a<2000 else '2000s' if a<2010 else '2010s' if a<2020 else '2020+' for *_,a in d); print(dec)
for s in sorted(set(x[1] for x in d)):
    v=[x[3] for x in d if x[1]==s]; print(s,'n',len(v),'median',st.median(v))
for c in ['Depot / stockpile','Land filling']:
    print(c,[(r['site'],y(r['visual_onset'])) for r in rows if r['type']==c])
print('undated ext',[r['site'] for r in rows if r['type'] in ext and not y(r['visual_onset'])])
