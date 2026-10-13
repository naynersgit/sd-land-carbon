"""Build the dashboard's data extract from CARB's Natural and Working Lands
Carbon Inventory aggregated workbook.

Usage (from the repo root):
    python scripts/build_extract.py path/to/NWL_Carbon_Inventory_2025_aggregated_data_table.xlsx
    python scripts/build_extract.py path/to/workbook.xlsx --county "San Diego"

Writes:
    data/nwl_extract.csv  one row per Year x Ownership x Ecoregion x Land Cover
    data/meta.json        source file name, county, build date, year range

Requires: pandas, openpyxl  (pip install pandas openpyxl)
"""

import argparse
import json
from datetime import date
from pathlib import Path

import pandas as pd

SHEET = "Aggregated Data"
RENAME = {
    "Land Cover": "LandCover",
    "Biomass Carbon MT C": "BiomassC",
    "Soil Carbon MT C": "SoilC",
    "Total Carbon MT C": "TotalC",
}
KEYS = ["Year", "Ownership", "Ecoregion", "LandCover"]
VALUES = ["Acreage", "BiomassC", "SoilC", "TotalC"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("workbook", type=Path, help="CARB aggregated data workbook (.xlsx)")
    parser.add_argument("--county", default="San Diego", help='County to extract (default: "San Diego")')
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent.parent / "data",
                        help="Output folder (default: the repo's data/ folder)")
    args = parser.parse_args()

    print(f"Reading {args.workbook.name} (this sheet is large; give it a minute)...")
    df = pd.read_excel(args.workbook, sheet_name=SHEET).rename(columns=RENAME)

    missing = [c for c in KEYS + VALUES + ["County"] if c not in df.columns]
    if missing:
        raise SystemExit(f"Workbook is missing expected columns: {missing}. Did CARB change the layout?")

    county = df[df["County"] == args.county]
    if county.empty:
        options = ", ".join(sorted(df["County"].dropna().unique()))
        raise SystemExit(f'No rows for county "{args.county}". Options: {options}')

    out = county.groupby(KEYS, as_index=False)[VALUES].sum().round(2)
    out = out.sort_values(KEYS)

    # Sanity check: total acreage should be close to constant year to year.
    acres = out.groupby("Year")["Acreage"].sum()
    spread = (acres.max() - acres.min()) / acres.mean()
    if spread > 0.01:
        print(f"WARNING: total acreage varies {spread:.1%} across years; check the source before publishing.")

    args.out.mkdir(parents=True, exist_ok=True)
    csv_path = args.out / "nwl_extract.csv"
    out.to_csv(csv_path, index=False)

    meta = {
        "source_file": args.workbook.name,
        "source": "CARB 2025 Natural and Working Lands Carbon Inventory, aggregated data table",
        "county": args.county,
        "built": date.today().isoformat(),
        "first_year": int(out["Year"].min()),
        "last_year": int(out["Year"].max()),
        "rows": len(out),
    }
    (args.out / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")

    print(f"Wrote {len(out):,} rows to {csv_path}")
    print(f"Years {meta['first_year']}-{meta['last_year']}, county {args.county}")


if __name__ == "__main__":
    main()
