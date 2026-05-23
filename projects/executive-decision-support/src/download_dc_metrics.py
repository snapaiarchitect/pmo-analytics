#!/usr/bin/env python3
"""
DC Open Data API Client
Fetches agency performance metrics from the DC Open Data Portal (CKAN API).

Primary endpoint: https://opendata.dc.gov/api/3/action/package_search
Fallback: https://opendata.dc.gov/datasets/DCGIS::agency-performance-metrics/explore
"""

import requests
import pandas as pd
import json
from pathlib import Path

BASE = Path(__file__).parent.parent
DATA_DIR = BASE / "data"
DATA_DIR.mkdir(exist_ok=True)

CKAN_API = "https://opendata.dc.gov/api/3/action"
AGENCY_PERFORMANCE_PACKAGE = "agency-performance-metrics"

def search_packages(query="agency performance"):
    """Search CKAN packages for agency performance datasets."""
    url = f"{CKAN_API}/package_search?q={requests.utils.quote(query)}&rows=20"
    print(f"[DC Open Data] Searching: {url}")
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("success"):
        print(f"[DC Open Data] Search failed: {data}")
        return []
    return data["result"]["results"]

def fetch_package_detail(package_id):
    """Fetch detailed package info including resources."""
    url = f"{CKAN_API}/package_show?id={package_id}"
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data["result"] if data.get("success") else None

def fetch_resource_csv(resource_url):
    """Download a CSV resource and parse to DataFrame."""
    print(f"[DC Open Data] Downloading CSV: {resource_url[:80]}...")
    resp = requests.get(resource_url, timeout=120)
    resp.raise_for_status()
    df = pd.read_csv(pd.io.common.StringIO(resp.text))
    print(f" -> {len(df)} records, {len(df.columns)} columns")
    return df

def fetch_agency_performance_fallback():
    """
    Fallback: Use the ArcGIS Open Data REST endpoint for Agency Performance Metrics.
    The CKAN package 'agency-performance-metrics' exposes an ArcGIS feature service.
    """
    # Try the ArcGIS REST API query endpoint directly
    # The dataset ID for DCGIS Agency Performance Metrics
    arcgis_url = "https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Administration_Other/MapServer/16/query"
    params = {
        "where": "1=1",
        "outFields": "*",
        "outSR": "4326",
        "f": "json",
        "resultRecordCount": 2000,
    }
    print(f"[DC Open Data] Trying ArcGIS REST fallback...")
    try:
        resp = requests.get(arcgis_url, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        features = data.get("features", [])
        if not features:
            print("[DC Open Data] No features returned from ArcGIS.")
            return pd.DataFrame()
        rows = [f["attributes"] for f in features]
        df = pd.DataFrame(rows)
        print(f"[DC Open Data] Fallback: {len(df)} records from ArcGIS")
        return df
    except Exception as e:
        print(f"[DC Open Data] ArcGIS fallback failed: {e}")
        return pd.DataFrame()

def main():
    print("=" * 60)
    print("DC Open Data — Agency Performance Metrics Downloader")
    print("=" * 60)

    df = None

    # Try 1: CKAN package search
    try:
        packages = search_packages("agency performance")
        target = None
        for pkg in packages:
            if AGENCY_PERFORMANCE_PACKAGE in pkg.get("name", "") or \
               "performance" in pkg.get("name", "").lower():
                target = pkg
                break

        if target:
            print(f"[DC Open Data] Found package: {target['name']}")
            detail = fetch_package_detail(target["id"])
            if detail and detail.get("resources"):
                for res in detail["resources"]:
                    fmt = res.get("format", "").upper()
                    if fmt in ("CSV", "GEOJSON", "JSON"):
                        df = fetch_resource_csv(res["url"])
                        break
        else:
            print("[DC Open Data] No matching package found via CKAN search.")
    except Exception as e:
        print(f"[DC Open Data] CKAN search failed: {e}")

    # Try 2: ArcGIS REST fallback
    if df is None or df.empty:
        df = fetch_agency_performance_fallback()

    # Try 3: Minimal synthetic but clearly labeled fallback
    if df is None or df.empty:
        print("[DC Open Data] All live sources failed. Generating labeled sample for structure.")
        agencies = [
            "Department of Health", "Metropolitan Police Department",
            "Department of Transportation", "Department of Energy & Environment",
            "Office of the Chief Technology Officer", "Department of Human Services",
            "Department of Parks and Recreation", "DC Public Schools",
            "Department of Employment Services", "Department of Consumer and Regulatory Affairs",
        ]
        df = pd.DataFrame({
            "agency_name": agencies,
            "metric_name": ["Composite Performance Index"] * len(agencies),
            "value": [68, 72, 58, 80, 85, 60, 75, 70, 55, 68],
            "reporting_period": ["2024-Q1"] * len(agencies),
        })
        df["_source"] = "labeled_sample_fallback"
        print(f"[DC Open Data] Generated {len(df)} labeled sample records")
    else:
        # Normalize columns
        col_map = {}
        for c in df.columns:
            cl = c.lower().strip()
            if "agency" in cl:
                col_map[c] = "agency_name"
            elif "metric" in cl and "name" in cl:
                col_map[c] = "metric_name"
            elif cl in ("value", "actual", "result"):
                col_map[c] = "value"
            elif "period" in cl or "quarter" in cl or "date" in cl:
                col_map[c] = "reporting_period"
        if col_map:
            df = df.rename(columns=col_map)
        # Ensure required columns exist
        for req in ["agency_name", "metric_name", "value", "reporting_period"]:
            if req not in df.columns:
                df[req] = "N/A"

    # Save
    out_json = DATA_DIR / "dc_agency_metrics.json"
    out_csv = DATA_DIR / "dc_agency_metrics.csv"
    df.to_json(out_json, orient="records", indent=2)
    df.to_csv(out_csv, index=False)
    print(f"\n[DC Open Data] Saved {len(df)} records to {out_json}")
    print(f"[DC Open Data] Saved CSV to {out_csv}")

    # Metadata
    meta = {
        "source": "DC Open Data Portal",
        "api_url": "https://opendata.dc.gov/api/3/action/package_search",
        "fallback_used": "ArcGIS REST" if "_source" not in df.columns else "labeled_sample",
        "record_count": len(df),
        "columns": list(df.columns),
        "date_fetched": pd.Timestamp.now().isoformat(),
    }
    with open(DATA_DIR / "dc_metadata.json", "w") as f:
        json.dump(meta, f, indent=2)

    print("\n[DC Open Data] Done.")

if __name__ == "__main__":
    main()
