"""
WMATA Open Data Fetcher
Queries available datasets from WMATA's Open Data Hub.

Data Source: https://www.wmata.com/initiatives/open-data-hub/
"""

import requests
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
WMATA_API_BASE = "https://api.wmata.com"

# WMATA doesn't have a single public API key-free endpoint for capital projects.
# We document what's available and fetch what we can without authentication.

WMATA_OPEN_DATA_URLS = {
    "gtfs": "https://developer.wmata.com/docs/services/gtfs/operations/6b8d88c7e8b7e7f0e8c8d8e7",
    "rail_stations": "https://api.wmata.com/Rail.svc/json/jStations",
    "bus_routes": "https://api.wmata.com/Bus.svc/json/jRoutes",
}


def fetch_wmata_stations() -> list[dict]:
    """Fetch WMATA rail station list (no API key required for basic endpoint)."""
    url = "https://api.wmata.com/Rail.svc/json/jStations"
    
    print(f"[WMATA] Fetching rail stations from {url}...")
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        stations = data.get("Stations", [])
        print(f"[WMATA] Got {len(stations)} stations")
        return stations
    except requests.exceptions.RequestException as e:
        print(f"[WMATA] Station fetch failed: {e}")
        return []


def fetch_wmata_lines() -> list[dict]:
    """Fetch WMATA rail line definitions."""
    url = "https://api.wmata.com/Rail.svc/json/jLines"
    
    print(f"[WMATA] Fetching rail lines...")
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        lines = data.get("Lines", [])
        print(f"[WMATA] Got {len(lines)} lines")
        return lines
    except requests.exceptions.RequestException as e:
        print(f"[WMATA] Line fetch failed: {e}")
        return []


def save_data(data: dict, filename: str) -> Path:
    """Save fetched data to JSON."""
    filepath = DATA_DIR / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"[WMATA] Saved to {filepath}")
    return filepath


def fetch_all_wmata() -> dict[str, Path]:
    """Fetch all available WMATA open data."""
    results = {}
    
    stations = fetch_wmata_stations()
    if stations:
        results["stations"] = save_data(
            {"Stations": stations, "source": "WMATA Rail API", "fetched": str(__import__("datetime").datetime.now())},
            "wmata_stations.json"
        )
    
    lines = fetch_wmata_lines()
    if lines:
        results["lines"] = save_data(
            {"Lines": lines, "source": "WMATA Rail API", "fetched": str(__import__("datetime").datetime.now())},
            "wmata_lines.json"
        )
    
    return results


if __name__ == "__main__":
    print("=" * 60)
    print("WMATA Open Data Hub — Data Fetcher")
    print("=" * 60)
    print(f"\nPortal: https://www.wmata.com/initiatives/open-data-hub/")
    print("Note: Capital project data requires WMATA developer API key.")
    print("This script fetches publicly available station and line data.\n")
    
    results = fetch_all_wmata()
    
    if results:
        for name, path in results.items():
            print(f"  {name}: {path}")
    else:
        print("  [No data fetched — WMATA API may require authentication]")
    
    print("\n[WMATA] Done.")
