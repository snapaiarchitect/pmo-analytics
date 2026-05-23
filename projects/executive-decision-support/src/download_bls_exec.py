#!/usr/bin/env python3
"""
Bureau of Labor Statistics (BLS) Data Downloader (DC-Specific)
Fetches REAL DC-area employment and wage data from the BLS Public Data API.

Series IDs:
- LAUMD113100000000003 : DC Unemployment Rate (Local Area Unemployment)
- SMU11310000000000001 : DC Employment (State and Area Employment)

No API key required for single-series requests.
"""

import requests
import pandas as pd
import json
from pathlib import Path

BASE = Path(__file__).parent.parent
DATA_DIR = BASE / "data"
DATA_DIR.mkdir(exist_ok=True)

BLS_API = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

SERIES = {
    "LASST110000000000003": {
        "name": "dc_unemployment_rate",
        "description": "DC Unemployment Rate (LAUS, %)",
    },
    "SMU11000000000000001": {
        "name": "dc_employment_level",
        "description": "DC Total Nonfarm Employment (CES, thousands)",
    },
}

def fetch_bls_series(series_ids, start_year=2019, end_year=2024):
    """Fetch BLS time-series data via public API (no key needed)."""
    headers = {"Content-Type": "application/json"}
    payload = {
        "seriesid": series_ids,
        "startyear": str(start_year),
        "endyear": str(end_year),
    }
    print(f"[BLS] Fetching: {', '.join(series_ids)} ({start_year}-{end_year})")
    resp = requests.post(BLS_API, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    if data.get("status") != "REQUEST_SUCCEEDED":
        print(f"[BLS] API status: {data.get('status')}")
        print(f"[BLS] Message: {data.get('message', 'N/A')}")
        return None

    all_rows = []
    for series in data.get("Results", {}).get("series", []):
        sid = series["seriesID"]
        meta = SERIES.get(sid, {"name": sid, "description": ""})
        for item in series.get("data", []):
            val = item.get("value")
            if val and val != "-":
                all_rows.append({
                    "series_id": sid,
                    "metric": meta["name"],
                    "description": meta["description"],
                    "year": int(item["year"]),
                    "period": item["period"],
                    "period_name": item.get("periodName", ""),
                    "value": float(val),
                })
    df = pd.DataFrame(all_rows)
    print(f"[BLS] -> {len(df)} records")
    return df

def fetch_bls_bulk_fallback():
    """Fallback: Download LAUS bulk file and filter for DC."""
    print("[BLS] Falling back to bulk LAUS data...")
    url = "https://download.bls.gov/pub/time.series/la/la.data.0.CurrentU15-19"
    try:
        resp = requests.get(url, timeout=120)
        resp.raise_for_status()
        lines = resp.text.splitlines()
        header_idx = 0
        for i, line in enumerate(lines):
            if "series_id" in line:
                header_idx = i
                break
        df = pd.read_csv(pd.io.common.StringIO("\n".join(lines[header_idx:])), sep="\t")
        df["series_id"] = df["series_id"].astype(str).str.strip()
        # DC unemployment: LASST11...03
        mask = df["series_id"].str.startswith("LASST11") & df["series_id"].str.endswith("03")
        sub = df[mask].copy()
        if sub.empty:
            print("[BLS] No DC data in bulk file.")
            return pd.DataFrame()
        sub["value"] = pd.to_numeric(sub["value"], errors="coerce")
        sub = sub.dropna(subset=["value"])
        sub_rows = []
        for _, row in sub.iterrows():
            sub_rows.append({
                "series_id": str(row["series_id"]),
                "metric": "dc_unemployment_rate",
                "description": "DC Unemployment Rate (LAUS bulk)",
                "year": int(row["year"]),
                "period": str(row["period"]).strip(),
                "period_name": "",
                "value": float(row["value"]),
            })
        df = pd.DataFrame(sub_rows)
        print(f"[BLS] Bulk fallback: {len(df)} records")
        return df
    except Exception as e:
        print(f"[BLS] Bulk fallback failed: {e}")
        return pd.DataFrame()

def main():
    print("=" * 60)
    print("BLS — DC Employment & Wages Downloader")
    print("=" * 60)

    series_ids = list(SERIES.keys())
    df = None
    try:
        df = fetch_bls_series(series_ids)
    except Exception as e:
        print(f"[BLS] API fetch failed: {e}")

    if df is None or df.empty:
        df = fetch_bls_bulk_fallback()

    if df is None or df.empty:
        print("[BLS] All sources failed. Generating minimal labeled sample.")
        df = pd.DataFrame({
            "series_id": ["LAUMD113100000000003", "SMU11310000000000001"],
            "metric": ["dc_unemployment_rate", "dc_employment_level"],
            "description": ["DC Unemployment Rate (sample)", "DC Employment Level (sample)"],
            "year": [2024, 2024],
            "period": ["M12", "M12"],
            "period_name": ["December", "December"],
            "value": [5.2, 780000],
        })
        df["_source"] = "labeled_sample_fallback"
        print(f"[BLS] Generated {len(df)} labeled sample records")

    # Save
    out_json = DATA_DIR / "bls_dc.json"
    out_csv = DATA_DIR / "bls_dc.csv"
    df.to_json(out_json, orient="records", indent=2)
    df.to_csv(out_csv, index=False)
    print(f"\n[BLS] Saved to {out_json}")
    print(f"[BLS] Saved CSV to {out_csv}")

    # Wide format
    if "metric" in df.columns:
        pivot = df.pivot_table(
            index=["year", "period"],
            columns="metric",
            values="value",
            aggfunc="first"
        ).reset_index()
        pivot.to_csv(DATA_DIR / "bls_dc_wide.csv", index=False)
        print(f"[BLS] Saved wide-format pivot ({len(pivot)} rows)")

    # Metadata
    meta = {
        "source": "Bureau of Labor Statistics",
        "api_url": BLS_API,
        "series": {k: v["description"] for k, v in SERIES.items()},
        "record_count": len(df),
        "date_fetched": pd.Timestamp.now().isoformat(),
    }
    with open(DATA_DIR / "bls_metadata.json", "w") as f:
        json.dump(meta, f, indent=2)

    print("\n[BLS] Done.")

if __name__ == "__main__":
    main()
