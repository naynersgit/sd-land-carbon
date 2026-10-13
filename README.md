# San Diego County land carbon dashboard

An interactive dashboard of acreage and carbon change on natural and working lands in San Diego County, 2001–2022. It's built from the California Air Resources Board's **2025 Natural and Working Lands (NWL) Carbon Inventory**, aggregated data table (released March 2026).

It contains four views, each filterable by ownership and ecoregion:

1. **Acreage change since 2001, by land cover.** The Cedar (2003) and Witch (2007) fire years are shaded, and the apparent 2011 reclassification is marked.
2. **Biomass and soil carbon over time**, in separate panels.
3. **Total carbon by land cover**, first year compared with last year (dumbbell chart).
4. **Carbon per acre by land cover** in the latest year.

## What's in this repo

```
index.html                 the dashboard (one self-contained page; loads d3 from cdnjs)
data/nwl_extract.csv       county extract: one row per Year x Ownership x Ecoregion x Land Cover
data/meta.json             source file, county, build date, year range (shown in the page footer)
scripts/build_extract.py   rebuilds the two data files from CARB's workbook
.nojekyll                  tells GitHub Pages to serve files as-is
```

## Viewing it locally

Browsers block a page opened straight from disk (`file://`) from loading its data. Start a small local server from the repo folder instead:

```bash
python -m http.server 8000
```

Then open http://localhost:8000.

## Updating the data

When CARB publishes a new inventory:

```bash
pip install pandas openpyxl                     # first time only
python scripts/build_extract.py ~/Downloads/NWL_Carbon_Inventory_<year>_aggregated_data_table.xlsx
git add data && git commit -m "Update to CARB <year> NWL inventory" && git push
```

The page reads the year range from the data, so its titles and axes update on their own. The script stops if the workbook's columns change. It also warns if total county acreage varies by more than 1% across years, which would point to a data problem.

**Another county:** add `--county "Riverside"` (or any county name in the workbook). The page title follows `data/meta.json`. The fire and reclassification markers in the charts are specific to San Diego and live in the `EVENTS` list near the top of the script in `index.html`.

## Caveats

- Carbon is in **metric tons of carbon (MT C)**, not CO2e. Multiply by 3.664 to convert.
- Soil carbon covers the top 30 cm only.
- The 2011 shrubland/grassland reversal and the 2014 shifts in cropland and developed land happen in a single year. They look like changes in classification or input data, not real land change.
- CARB notes that some developed-land and cropland biomass years were imputed.
- The data is aggregated by year, so it can't show which acres converted to which cover type.

## Source

California Air Resources Board, *Natural and Working Lands Ecosystem Carbon data for the 2025 Natural and Working Lands Carbon Inventory*: https://ww2.arb.ca.gov/nwl-inventory
