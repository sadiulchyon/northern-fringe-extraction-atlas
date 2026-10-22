# Northern Fringe Extraction Atlas

Sand and gravel extraction along the northern border of Bangladesh, 1988 to 2025, reconstructed at 121 sites (river reaches, stone and sand depots, land ports and sand-filled land) from one January Landsat scene per dry season.

**Atlas:** https://sadiulchyon.github.io/northern-fringe-extraction-atlas/

This repository holds the data, code and interactive atlas behind Chapter 4 of the doctoral dissertation of Md Sadiul Alam Chyon (Department of Geography and Geographic Information Science, University of Illinois Urbana-Champaign; supervisor Jim Best). The results are provisional and unpublished.

## What the atlas shows

- **Map** of the 411 reconnaissance inventory points, the 83 site windows clustered from them and 16 added reaches, coloured by result. Click a site for its January image chips, classes and series.
- **Year slider:** sites light up from the first January in which their low-flow series shows an extraction-type change; a strip chart counts changed sites by sector.
- **Onset by position** along the border, with dated laws, bans and dredging works.
- **Spread:** first year of change against longitude, with sector medians.
- **Site detail:** water, sand and vegetation area inside each river outline, 1988 to 2025.
- **Tables** of all analysed sites and of the screening.

## Method in brief

1. **Sites.** The 132 extraction records of the inventory were clustered at 2 km into 83 windows of 3 to 4 km (E001 to E083, west to east). Reaches without records (N01 to N17) were added from press reports and from screening the border rivers on Google satellite imagery. Every window was screened before analysis.
2. **Scenes.** For each dry season, one Landsat Collection 2 Level 2 scene: at least 90% of the window clear between 15 December and 28 February, lowest median blue reflectance (least haze); fallbacks 80% clear, then November to April. Bands at 30 m in UTM zone 46N, with JRC Global Surface Water occurrence.
3. **Outline.** Pixels that are water or bare in at least 40% of usable Januaries, in components within 300 m of the site's records (largest component for added reaches), buffered by 100 m. Floodplain pit fields in S1 use the whole window ("pit-field mode").
4. **Classes.** Water MNDWI > 0; sand NDVI < 0.25 and not water; vegetation NDVI ≥ 0.30. Hazy, partial (< 80% clear) and one-season outlier scenes are flagged and excluded from statistics.
5. **Onset.** Pettitt change point on water, sand and baseline-sand-now-water areas, plus a visual onset read from the January panels and the first-conversion map.
6. **Result classes.** Pit extraction; floodplain pits; possible dredging (water rises as bars go, no pit pattern); bar loss; bar vegetation (char cropping, not extraction); depot or stockpile (bare yards); land filling (sand fill for development); no signal.

Limits: detection at 30 m lags the true start where pits are small (about four years on the Someshwari); a sand step between the 2013 and 2014 seasons at some S1 sites may come from the Landsat 7 to 8 change; most sites have no gauge, so stage is controlled only by the January date.

## Main results (22 October 2026)

| Class | Sites |
|---|---|
| Pit extraction | 14 |
| Floodplain pits | 9 |
| Possible dredging | 18 |
| Bar loss | 12 |
| Bar vegetation | 20 |
| Depot / stockpile | 3 |
| Land filling | 5 |
| No signal | 40 |

Sites N19 to N38 (added 22 October 2026) go beyond the inventory: stone crusher and stockpile yards, land ports, quarries and sand-filled land (economic zones, the Sylhet Hi-Tech Park), found from Google Maps listings and imagery and run in pit-field mode, where the rise in bare ground marks the yard or the fill.

Of 48 dated extraction-type sites, 5 change before 2000, 23 in 2000 to 2009, 18 in 2010 to 2019 and 2 after 2020. Extraction began at two gravel cores, the Patgram floodplain (1998 to 2005) and the Sylhet rivers (2005 to 2006), filled the Sylhet rivers by 2013, and shifted after 2014 to the sand rivers of Sunamganj and Netrokona (Dolura 2015 to 2017, Rakti 2016, Jadukata and Someshwari 2021).

## Repository layout

| Path | Contents |
|---|---|
| `docs/` | The atlas (GitHub Pages): `index.html`, `data/` (CSV and JSON it reads), `vendor/d3.min.js` |
| `gee/ch4_09_lowflow_runsites.js` | Earth Engine helpers that pick the January scenes and download each site as `SITE_scenes_v2.bin` |
| `gee/corridor_rf_superseded/` | Earlier corridor-wide random-forest pipeline (scripts 01 to 08), set aside because it recorded bare ground rather than extraction |
| `scripts/` | Python and shell pipeline (below) |
| `inventory_411_sectors.csv` | The 411 inventory points with sector and distance to the border |
| `sites/sites_v1.csv`, `.geojson` | The 83 site windows; `sites_extra.csv` the added reaches N01 to N18 |
| `sites/lowflow/` | Per-site January series (`SITE_series.csv`), panels (`SITE_panel.png`), pit-field flags (`SITE_mode.txt`) and the Pettitt table (`onset_summary.csv`) |
| `maps/dash/` | Source tables for the atlas; `site_results.csv` is the authoritative list of result classes and visual onsets |
| `maps/ch4_inventory_sites.kml` | Inventory points and site windows for Google Earth |
| `figures/` | Thesis figures (PNG) and the scripts that draw them |

Raw downloads (`*.bin`, about 6 MB per site) and intermediate arrays (`*.npz`, `*.npy`) are not included; they are regenerated by steps 2 and 3 below.

## Reproducing a site

Requirements: an Earth Engine account; Python 3.10 or later with numpy, matplotlib and Pillow.

1. Add the reach to `sites/sites_extra.csv` (window bounds in the last four columns), then print its list for Earth Engine:
   `python3 scripts/windows.py 1.75 SITE`
2. Open the Earth Engine Code Editor, paste `gee/ch4_09_lowflow_runsites.js` into the browser's developer console, and run `window.__runSites([[SITE, W, S, E, N]])`. One list at a time; each site takes 1 to 4 minutes and downloads `SITE_scenes_v2.bin`.
3. `DOWNLOADS=~/Downloads bash scripts/run_site.sh SITE` builds the outline, classes, series and panels in `sites/lowflow/`.
4. `python3 scripts/onset_table.py SITE` prints the Pettitt breaks.
5. Classify from the panel and add a row to `maps/dash/site_results.csv` (site, type, river, visual_onset, note).
6. `TAG=b01 bash scripts/dash_pack.sh SITE` rebuilds the onset table, series, KML and image chips in `maps/dash/`; `bash scripts/publish_site.sh` copies them into `docs/data/`.

To view the atlas locally: `python3 -m http.server --directory docs` and open http://localhost:8000.

## Data sources

Landsat Collection 2 Level 2 (U.S. Geological Survey); JRC Global Surface Water (Pekel et al., 2016, Nature 540, 418–422); HydroRIVERS v1.0 (Lehner and Grill, 2013); Natural Earth 1:10m boundaries; inventory points mapped on Google Earth historical imagery. Governance dates in `maps/dash/events.csv` carry their source links. d3 v7 (ISC licence) is bundled in `docs/vendor/`.

## Citation and reuse

Chyon, M. S. A. (2026). *Northern Fringe Extraction Atlas: sand and gravel extraction along the northern border of Bangladesh, 1988–2025* [Data and code]. https://github.com/sadiulchyon/northern-fringe-extraction-atlas

No licence is granted yet; please contact the author before reusing the data or results.

Contact: mchyon2@illinois.edu
