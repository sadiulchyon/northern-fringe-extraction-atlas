"""KML of the 411 inventory points (labelled, foldered by label_group) + 83 site windows coloured by low-flow result.
Output: maps/ch4_inventory_sites.kml (open in Google Earth Pro; use the historical imagery slider)."""
import csv, html
inv=list(csv.DictReader(open('inventory_411_sectors.csv')))
sites=list(csv.DictReader(open('sites/sites_v1.csv')))+list(csv.DictReader(open('sites/sites_extra.csv')))
# status from low-flow runs (22 Oct)
status={'E076':('pit','Jaflong reach: pits in bar by 2014; water 19->36 ha after 2012'),
'E077':('pit','Piyain below Jaflong: water 37->52 ha after 2006; channel to water 2016-18'),
'E048':('pit','three pits; N about 1996-97, SW about 2005, water by 2014'),
'E008':('pit','Mahananda border: water and sand-to-water rise after 1999'),
'E045':('dredge','water 7->13 ha after 2010, bars shrink 2010-16'),
'E044':('dredge','bend to continuous water 2014-24 (small AOI)'),
'E010':('bars','Mahananda Tetulia: water up after 2002, bars narrow'),
'E028':('veg','bars vegetated after 2011, no water gain'),'E029':('veg','bars vegetated 2011-13'),
'E030':('veg','bars vegetated 2010-13'),'E043':('veg','bars vegetate, river narrows after 2004'),
'E079':('dredge','Sari at Sharighat: bar gone 1995-2001, sand-to-water break 1999'),
'E072':('dredge','Sari-Goyain at Ratargul: margins convert from 2006, bars shrink after 2011'),
'E081':('bars','Kushiyara point bar shrinks after 2012'),'E073':('bars','dry sand channel, sand falls slowly after 2011'),
'E058':('veg','water falls after 2005, bed narrows after 2016'),'E070':('none','outline fell on a pond'),
'E006':('fpit','Tetulia floodplain pits 2001-2010'),'E007':('fpit','Tetulia floodplain pits 1998-2010'),
'E013':('fpit','Patgram pit field 2005-2010'),'E014':('fpit','Patgram pit field 2005-2010'),'E004':('fpit','Karatoya pit ground 2001-2010'),
'E001':('fpit','Dahuk ponds/pits from 2005'),'E003':('fpit','Mahananda bend pits 2005-2010 (weak)'),'E015':('fpit','Patgram pits from 2005'),
'E005':('dredge','Karatoya channel water up after 2000'),'E016':('bars','Dharla bars lower after 2012'),'E017':('veg','Dharla bars vegetate after 2014'),
'E012':('none','dark panel; channel migration'),'E018':('none','Teesta braided, barrage-controlled'),
'E024':('none','braided, migration'),'E025':('none','braided, migration'),'E026':('veg','bars vegetated after 2012'),
'E027':('veg','bars vegetated after 2013'),'E032':('veg','point bar vegetates 2009-2011'),'E033':('veg','bars vegetate after 2011'),
'E034':('veg','bars vegetate after 2011'),'E031':('bars','bars gone 2010-2014'),'E039':('veg','bend migrates, bars vegetate 2016'),
'E042':('bars','sand falls 2003-2014 (weak)'),'E046':('dredge','Old Brahmaputra, new water 2019-2022'),'E047':('dredge','Old Brahmaputra, new water 2018-2022'),
'E049':('bars','point bar shrinks 1998-2010'),'E051':('veg','bars vegetate after 2012'),
'N01':('pit','Jadukata at Laurergarh: pit area opens 2022-2024'),'N02':('veg','Dharla at Kurigram: bars vegetate after 2013'),
'N03':('none','Dharla at Mogolhat: migration'),'N04':('pit','Dhalai at Bholaganj: pit field 2005-2010'),
'N05':('pit','Someshwari at Durgapur: dredge pools 2021-2024'),'N06':('pit','Dhalai below Bholaganj: from 2006, lake 2021-2024'),
'E083':('pit','Lubha at Lubhachorra: water widens after 2013 (Ch5)'),
'E056':('fpit','Chanpur Chora fan: dry quarry ground 2004-2005'),'E036':('bars','border channel bars gone 2002-2007'),
'E080':('dredge','Sari below Lalakhal: channel water up 2005-2007'),'E059':('none','Surma at Chhatak, deep'),'E053':('none','Kangsa, beel change'),
'E082':('dredge','Surma near Kanaighat: bar shrinks 2013-2018'),'E068':('bars','border fan shrinks 2010-2024'),
'E075':('none','beel-dominated'),'E071':('none','sub-pixel channel'),'E074':('none','sub-pixel'),
'E002':('dredge','Dahuk bed water from 2003'),'E009':('dredge','Chauli bed water from 2007'),'E011':('dredge','Chauli bed water from 2004'),
'E040':('dredge','bars shrink, water up 2000-2010'),'E037':('veg','bars vegetate 2010'),
'E060':('pit','Border river at Dolura: sand bed to water body 2015-2017'),'E061':('dredge','Below Dolura: bars removed 2010-2017'),
'E052':('none','Kangsa loops'),'E054':('none','Kangsa narrows'),'E055':('none','Kangsa'),
'E050':('dredge','Malijhi: bars gone 2010-2014'),'E057':('none','haor channel'),'E062':('none','sub-pixel'),'E063':('none','paddy/beel'),'E066':('none','canal/beel'),
'E022':('none','Teesta migration'),'E023':('none','Teesta braided'),'E035':('veg','bar vegetates 2010'),'E038':('veg','Brahmaputra bank, bars vegetate 2013'),'E041':('none','paddy/beel'),
'E019':('none','Teesta braided'),'E020':('none','Teesta braided'),'E021':('none','Teesta braided'),
'N07':('none','Someshwari at Bijoypur: flat'),'N08':('bars','Jadukata-Rakti confluence: bar loss from 2001'),'N09':('dredge','Rakti at Shaktiarkhola: 2016 step'),'N10':('none','Mahananda at Banglabandha: hazy, no signal'),'N11':('pit','Chela below border: wet bed from 2007'),
'N12':('bars','Mahadeo at Patlaban: bar loss from 2014'),'N13':('veg','Dudhkumar at Balabhut: bars vegetate 2012'),'N15':('bars','Chela above Kalatek: weak bar loss from 2010'),'N17':('veg','Teesta entry: chars vegetate 2011-14'),'N16':('none','Dolura fan above border: no signal'),'N18':('none','Gangadhar: no signal'),'N19':('pit','Jaflong-Tamabil crusher yards from 1999-2001'),'N20':('none','Chhatak depots: below 30 m'),'N21':('pit','Hi-Tech Park sand fill 2018-2021'),'N23':('pit','Bholaganj crusher yards from 2005'),'N22':('dredge','Old Brahmaputra Mymensingh: spoil 2021-2025'),'N24':('none','Teesta at Kaunia: braided'),'N25':('pit','Srihatta EZ fill 2017-2018'),'N26':('dredge','Someshwari below Durgapur 2023-2025'),'N27':('pit','Sreepur quarry from 2000'),'N28':('pit','Jamalpur EZ fill 2018-2021'),'N29':('pit','Dhanua-Kamalpur port fill 2014-2024'),'N30':('none','Nakugaon: below 30 m'),'N31':('veg','Karatoya Debiganj: bars vegetate 2012'),'N32':('pit','Sonahat port yards 2018-2024'),'N33':('none','Gobrakura depots: below 30 m'),'N34':('pit','Bisnakandi floodplain pits 2007-2015'),'N35':('pit','Tekerghat quarries 2000-2010'),'N36':('none','Banglabandha stockpiles: below 30 m'),'N37':('pit','Uttara EPZ fill 2001'),'N38':('none','Chekarmari: no pits'),'N39':('pit','Lafarge Umiam limestone mine at Nongtrai: Pit extraction'),'N40':('none','Umngot (Piyain) at Shnongpdeng–Dawki abo: No signal'),'N41':('pit','University of Netrokona sand-filled camp: Land filling'),'N42':('pit','Lafarge Surma cement plant and limestone: Depot / stockpile'),'N43':('pit','Sunamganj Medical College on filled haor: Land filling'),'N44':('none','Salutikar stone and sand landing ghat (G: No signal'),'N45':('none','Simsang (upper Someshwari) at Baghmara (: No signal'),'N46':('veg','Teesta at the Mahipur bridge (Gangachara: Bar vegetation'),'N47':('fpit','Kalairag east-bank stone pits 2005-2013'),'N48':('veg','Old Brahmaputra above Jamalpur: bars vegetate 2011'),'N49':('veg','Mahananda at Siliguri–Fulbari (India): Bar vegetation'),'N50':('veg','Teesta at the Gajoldoba barrage (India): Bar vegetation'),'N51':('veg','Teesta at Jalpaiguri (India): Bar vegetation'),'N52':('veg','Teesta at Mekhliganj (India): Bar vegetation'),'N53':('veg','Teesta Barrage at Dalia: Bar vegetation'),'N54':('veg','Dharla below the Kurigram bridge: Bar vegetation'),'N55':('none','Dhalai (Umiam) gorge above Bholaganj (In: No signal'),'N56':('none','Surma at Sylhet city: No signal'),'N57':('none','Surma at Sunamganj town: No signal'),'N58':('none','Ichamati border fan (Companiganj): No signal'),'N14':('none','Bagli streams: haor stage'),
'E064':('none','stage-dominated'),'E065':('none','seasonal pond'),'E067':('none','ponds/quarry, small streams'),
'E069':('none','sub-pixel streams'),'E078':('none','sub-pixel stream')}
col={'pit':'ff0000ff','fpit':'ffad448e','dredge':'ff00a5ff','bars':'ff00ffff','veg':'ff00c000','none':'ff808080','todo':'ffffffff'}
gcol={'Sand Mining':'ff0000ff','Other extraction':'ff0060ff','Vessels':'ffff8000','Deposit/depot':'ff00d7ff',
'River/floodplain':'ff00ff80','Named feature':'ffff00ff','Uncertain label':'ffb0b0b0'}
out=['<?xml version="1.0" encoding="UTF-8"?>','<kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>Ch4 extraction inventory (411) and sites (83)</name>']
for g,c in gcol.items():
    sid=g.replace('/','_').replace(' ','_')
    out.append(f'<Style id="{sid}"><IconStyle><color>{c}</color><scale>0.8</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon></IconStyle><LabelStyle><scale>0.7</scale></LabelStyle></Style>')
for k,c in col.items():
    out.append(f'<Style id="site_{k}"><LineStyle><color>{c}</color><width>2.5</width></LineStyle><PolyStyle><fill>0</fill></PolyStyle><LabelStyle><color>{c}</color></LabelStyle></Style>')
out.append('<Folder><name>Inventory points (411)</name>')
for g in gcol:
    pts=[x for x in inv if x['label_group']==g]
    out.append(f'<Folder><name>{html.escape(g)} ({len(pts)})</name>')
    for x in pts:
        nm=f"{x['rid']} {x['name']}"
        d=(f"rid {x['rid']}<br>{html.escape(x['name'])}<br>desc: {html.escape(x['desc'])}<br>mapped on GE imagery {x['ge_view']}<br>"
           f"sector {x['sector']}, {x['admin1']}, {x['admin0']}, {float(x['dist_border_km']):.1f} km from border<br>intensity {x['intensity']} setting {x['setting']}")
        out.append(f'<Placemark><name>{html.escape(nm)}</name><description><![CDATA[{d}]]></description><styleUrl>#{g.replace("/","_").replace(" ","_")}</styleUrl><Point><coordinates>{x["lon"]},{x["lat"]},0</coordinates></Point></Placemark>')
    out.append('</Folder>')
out.append('</Folder><Folder><name>Extraction sites E001-E083 (low-flow result)</name>')
for s in sites:
    st,txt=status.get(s['site_id'],('todo','not yet run'))
    W,E,S,N=[float(s[k]) for k in ('west','east','south','north')]
    ring=f"{W},{S},0 {E},{S},0 {E},{N},0 {W},{N},0 {W},{S},0"
    d=f"{s['site_id']} {s['sector']} {s['admin0']} records {s['n_rec']} ({s['rids']})<br>result: {st} - {html.escape(txt)}"
    out.append(f'<Placemark><name>{s["site_id"]} [{st}]</name><description><![CDATA[{d}]]></description><styleUrl>#site_{st}</styleUrl><Polygon><outerBoundaryIs><LinearRing><coordinates>{ring}</coordinates></LinearRing></outerBoundaryIs></Polygon></Placemark>')
out.append('</Folder></Document></kml>')
open('maps/ch4_inventory_sites.kml','w').write('\n'.join(out))
print('ok')
