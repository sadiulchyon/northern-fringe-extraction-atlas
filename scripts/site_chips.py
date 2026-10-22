"""Image chips for the dashboard: per analysed site, 4 Januarys (baseline, before onset, after onset, latest),
pseudo-true colour (outside AOI faded) and classes inside the AOI, as base64 PNG rows -> maps/dash/chips.json"""
import csv, json, io, re, base64, numpy as np
from PIL import Image
res=list(csv.DictReader(open('maps/dash/site_results.csv')))
ons={r['site']:r for r in csv.DictReader(open('maps/dash/onset.csv'))}
PAL={0:(31,78,156),1:(242,210,122),2:(79,154,69),3:(200,195,184)}
def stretch(a):
    lo=np.nanpercentile(a,2,axis=(0,1,2)); hi=np.nanpercentile(a,98,axis=(0,1,2)); return np.clip((a-lo)/(hi-lo),0,1)
def b64j(arr):
    im=Image.fromarray(arr,'RGB'); buf=io.BytesIO(); im.save(buf,'JPEG',quality=82); return base64.b64encode(buf.getvalue()).decode()
def b64(arr,mode):
    im=Image.fromarray(arr,mode); buf=io.BytesIO(); im.save(buf,'PNG',optimize=True); return base64.b64encode(buf.getvalue()).decode()
out=[]; info=[]
for r in res:
    sid=r['site']; d=np.load(f'sites/lowflow/{sid}_lowflow.npz'); years=list(d['years']); aoi=d['aoi']
    ser={int(x['season']):x for x in csv.DictReader(open(f'sites/lowflow/{sid}_series.csv'))}
    ok=[y for y in years if not ser.get(int(y),{}).get('flag')]
    ys=re.findall(r'\d{4}',r['visual_onset'])
    if ys: a=int(ys[0]); b=int(ys[1]) if len(ys)>1 else (a+6 if 'onward' in r['visual_onset'] else a)
    else:
        wb=int(float(ons[sid]['water_break'])) if sid in ons else 2005; a,b=wb,wb+4
    near=lambda t,cond: min([y for y in ok if cond(y)] or [None],key=lambda y: abs(y-t) if y else 1e9)
    y0=ok[0]; y3=ok[-1]
    y1=near(a-1,lambda y: y0<y<y3 and y<=a)
    y2=near(b+2,lambda y: (y1 or y0)<y<y3 and y>=b)
    pick=[y for y in [y0,y1,y2,y3] if y is not None]
    pick=sorted(set(pick))
    while len(pick)<4:
        cand=[y for y in ok if y not in pick]
        gaps=[(pick[i+1]-pick[i],i) for i in range(len(pick)-1)]; g,i=max(gaps); mid=(pick[i]+pick[i+1])/2
        pick=sorted(pick+[min(cand,key=lambda y:abs(y-mid))])
    ii,jj=np.where(aoi); nr,nc=aoi.shape; pad=3
    r0,r1,c0,c1=max(ii.min()-pad,0),min(ii.max()+1+pad,nr),max(jj.min()-pad,0),min(jj.max()+1+pad,nc)
    tc=stretch(np.where(d['nod'][...,None],np.nan,d['true'])[:, r0:r1, c0:c1])
    cls=np.full(d['water'].shape,3); cls[d['veg']]=2; cls[d['sand']]=1; cls[d['water']]=0
    sub=aoi[r0:r1,c0:c1]
    for y in pick:
        t=years.index(y)
        img=np.nan_to_num(tc[t],nan=0.5).copy(); img[~sub]=img[~sub]*0.4+0.45
        rgb=(img*255).astype(np.uint8)
        c=cls[t][r0:r1,c0:c1]; ca=np.zeros(c.shape+(4,),np.uint8)
        for k,v in PAL.items(): ca[c==k,:3]=v
        ca[...,3]=np.where(sub,255,0); ca[d['nod'][t][r0:r1,c0:c1]&sub]=(255,255,255,255)
        s=ser.get(int(y),{})
        out.append({'site':sid,'season':int(y),'date':s.get('date',''),'sensor':s.get('sensor',''),'w':int(sub.shape[1]),'h':int(sub.shape[0]),
                    'water_ha':s.get('water_ha',''),'sand_ha':s.get('sand_ha',''),'img':b64j(rgb),'fmt':'jpeg','cls':b64(ca,'RGBA')})
    info.append((sid,pick,sub.shape))
json.dump(out,open('maps/dash/chips.json','w'),separators=(',',':'))
for x in info: print(x)
import os; print(os.path.getsize('maps/dash/chips.json'))
