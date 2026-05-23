#!/usr/bin/env python3
"""
FTA National Transit Database (NTD) Capital Data Downloader
Fetches REAL capital expenditure data from FTA NTD.

Primary source: data.transportation.gov (Socrata platform)
  - 2022-2024 Capital Expenses: https://data.transportation.gov/Public-Transit/2022-2024-NTD-Annual-Data-Capital-Expenses-by-Capi/fphd-jyyj
  - 2024 Capital Use: https://www.transit.dot.gov/ntd/data-product/2024-annual-database-capital-use

Fallback: Direct CSV download from FTA NTD website
  - Annual Database Capital Use Excel/CSV files
  - URL pattern: https://www.transit.dot.gov/ntd/data-product/{year}-annual-database-capital-use

Data captured:
  agency_name, mode, type_of_service, capital_use_type,
  function, expense_amount, year, ntd_id

Citation: Federal Transit Administration National Transit Database
"""

import requests
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent.parent
DATA_DIR = BASE / "data"
DATA_DIR.mkdir(exist_ok=True)

# Socrata API endpoint for 2022-2024 Capital Expenses
NTD_SOCRATA_ID = "fphd-jyyj"
NTD_API = f"https://data.transportation.gov/resource/{NTD_SOCRATA_ID}.csv"

# FTA NTD product page (for documentation + manual download)
NTD_PRODUCT_URL = "https://www.transit.dot.gov/ntd/data-product/2024-annual-database-capital-use"


def fetch_ntd_socrata(limit=50000):
    """Fetch NTD capital expenses from Socrata API (no key required)."""
    print(f"[NTD] Fetching from Socrata API...")
    print(f"[NTD] URL: {NTD_API}")

    params = {"$limit": limit}
    resp = requests.get(NTD_API, params=params, timeout=120)

    if resp.status_code != 200:
        print(f"[WARN] Socrata API returned {resp.status_code}")
        print(f"[WARN] Response: {resp.text[:200]}")
        return None

    from io import StringIO

    df = pd.read_csv(StringIO(resp.text))
    print(f"  -> Retrieved {len(df)} records")
    return df


def fetch_ntd_sample():
    """Fetch a small sample to verify the API works."""
    params = {"$limit": 10}
    resp = requests.get(NTD_API, params=params, timeout=30)
    if resp.status_code == 200:
        from io import StringIO

        df = pd.read_csv(StringIO(resp.text))
        return df
    return None


def build_documentation_file():
    """Create a documentation file with manual download instructions."""
    doc = """# FTA NTD Data — Manual Download Guide

If the Socrata API is unavailable, use these direct download links:

## 2024 Annual Database Capital Use
- Web page: https://www.transit.dot.gov/ntd/data-product/2024-annual-database-capital-use
- Data file: Download Excel/CSV from the FTA NTD Data Products page

## 2022-2024 Capital Expenses (by Capital Use Type)
- Socrata dataset: https://data.transportation.gov/Public-Transit/2022-2024-NTD-Annual-Data-Capital-Expenses-by-Capi/fphd-jyyj
- Direct CSV: https://data.transportation.gov/api/views/fphd-jyyj/rows.csv?accessType=DOWNLOAD

## Historical Time Series
- TS3.1 Capital Expenditures: https://www.transit.dot.gov/ntd/data-product/ts31-capital-expenditures-time-series-2

## Data Dictionary
- NTD Glossary: https://www.transit.dot.gov/ntd/ntd-glossary
- Capital Use fields: agency, mode, TOS, capital_use_type, function, expense

## Citation
Federal Transit Administration, National Transit Database.
https://www.transit.dot.gov/ntd
"""
    doc_path = DATA_DIR / "NTD_DOWNLOAD_GUIDE.md"
    doc_path.write_text(doc)
    print(f"[NTD] Saved download guide to {doc_path}")


def main():
    print("=" * 60)
    print("FTA National Transit Database Capital Data Downloader")
    print("=" * 60)
    print(f"Source: {NTD_API}")
    print(f"Product page: {NTD_PRODUCT_URL}")
    print()

    # Try API
    df = None
    try:
        df = fetch_ntd_socrata(limit=50000)
    except Exception as e:
        print(f"[WARN] Socrata fetch failed: {e}")

    if df is not None and not df.empty:
        # Save raw data
        csv_path = DATA_DIR / "ntd_capital_expenses.csv"
        df.to_csv(csv_path, index=False)
        print(f"\n[NTD] Saved {len(df)} records to {csv_path}")

        # Summary
        print("\n[NTD] Sample columns:", list(df.columns[:8]))
        if "expense" in df.columns or any("expense" in c.lower() for c in df.columns):
            expense_col = next(c for c in df.columns if "expense" in c.lower())
            print(f"[NTD] Total capital expenses: ${df[expense_col].sum():,.0f}")

        # Metadata
        meta = {
            "source": "FTA National Transit Database",
            "api_url": NTD_API,
            "product_page": NTD_PRODUCT_URL,
            "record_count": len(df),
            "columns": list(df.columns),
            "fetched_at": datetime.now().isoformat(),
            "citation": "Federal Transit Administration, National Transit Database",
        }
        with open(DATA_DIR / "ntd_metadata.json", "w") as f:
            json.dump(meta, f, indent=2)
    else:
        print("\n[NTD] API unavailable. Saving documentation for manual download.")

    build_documentation_file()
    print("\n[NTD] Done.")


if __name__ == "__main__":
    main()
