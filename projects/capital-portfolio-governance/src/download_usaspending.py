#!/usr/bin/env python3
"""
USASpending.gov Federal Transit Grants Downloader
Fetches REAL federal grant award data from USASpending API.

Source: https://api.usaspending.gov/api/v2/search/spending_by_award/
Documentation: https://api.usaspending.gov/docs/endpoints

Data fetched:
- Federal Transit Administration (FTA) grants
- Federal Highway Administration (FHWA) grants
- Filtered to transportation-related awards

Fields captured:
  award_id, recipient, amount, start_date, end_date,
  awarding_agency, awarding_sub_agency, award_type, place_of_performance_state

Citation: USASpending.gov, U.S. Department of the Treasury
"""

import requests
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent.parent
DATA_DIR = BASE / "data"
DATA_DIR.mkdir(exist_ok=True)

USASPENDING_API = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

# Award type codes for grants
GRANT_TYPE_CODES = ["02", "03", "04", "05"]

# Target sub-agencies
TARGET_AGENCIES = ["Federal Transit Administration", "Federal Highway Administration"]


def fetch_agency_awards(subagency_name, limit=100):
    """Fetch grant awards for a specific DOT sub-agency."""
    payload = {
        "filters": {
            "award_type_codes": GRANT_TYPE_CODES,
            "agencies": [
                {
                    "type": "awarding",
                    "tier": "subtier",
                    "name": subagency_name,
                }
            ],
        },
        "fields": [
            "Award ID",
            "Recipient Name",
            "Award Amount",
            "Start Date",
            "End Date",
            "Awarding Agency",
            "Awarding Sub Agency",
            "award_type",
            "Base Obligation Date",
            "Place of Performance State Code",
        ],
        "sort": "Award Amount",
        "order": "desc",
        "limit": limit,
    }

    print(f"[USASpending] Fetching {subagency_name} awards (limit={limit})...")
    resp = requests.post(USASPENDING_API, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    results = data.get("results", [])
    print(f"  -> Retrieved {len(results)} awards")

    records = []
    for r in results:
        records.append(
            {
                "award_id": r.get("Award ID"),
                "recipient": r.get("Recipient Name"),
                "amount": r.get("Award Amount"),
                "start_date": r.get("Start Date"),
                "end_date": r.get("End Date"),
                "awarding_agency": r.get("Awarding Agency"),
                "awarding_sub_agency": r.get("Awarding Sub Agency"),
                "award_type": r.get("award_type"),
                "obligation_date": r.get("Base Obligation Date"),
                "place_of_performance_state": r.get("Place of Performance State Code"),
                "generated_internal_id": r.get("generated_internal_id"),
            }
        )

    return records


def fetch_all_transit_awards(limit_per_agency=100):
    """Fetch awards from both FTA and FHWA."""
    all_records = []
    for agency in TARGET_AGENCIES:
        try:
            records = fetch_agency_awards(agency, limit=limit_per_agency)
            all_records.extend(records)
        except Exception as e:
            print(f"[WARN] Failed to fetch {agency}: {e}")

    df = pd.DataFrame(all_records)
    if df.empty:
        print("[ERROR] No data retrieved from USASpending.")
        return df

    # Clean numeric columns
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    # Add metadata
    df["data_source"] = "USASpending.gov"
    df["fetched_at"] = datetime.now().isoformat()

    return df


def compute_portfolio_summary(df):
    """Compute portfolio-level KPIs from award data."""
    # Handle missing dates
    start_min = df['start_date'].dropna().min() if 'start_date' in df.columns else 'N/A'
    end_max = df['end_date'].dropna().max() if 'end_date' in df.columns else 'N/A'
    date_range = f"{start_min} to {end_max}" if start_min != 'N/A' and end_max != 'N/A' else 'N/A'

    summary = {
        "total_awards": len(df),
        "total_obligation": df["amount"].sum(),
        "avg_award": df["amount"].mean(),
        "median_award": df["amount"].median(),
        "agencies": df["awarding_sub_agency"].value_counts().to_dict(),
        "states": df["place_of_performance_state"].value_counts().head(10).to_dict(),
        "date_range": date_range,
    }
    return summary


def main():
    print("=" * 60)
    print("USASpending Federal Transit Grants Downloader")
    print("=" * 60)
    print("Source: https://api.usaspending.gov")
    print("Agencies: Federal Transit Administration, Federal Highway Administration")
    print()

    df = fetch_all_transit_awards(limit_per_agency=100)

    if df.empty:
        print("[ERROR] No data fetched. Exiting.")
        return

    # Save raw data
    csv_path = DATA_DIR / "usaspending_transit_grants.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n[USASpending] Saved {len(df)} awards to {csv_path}")

    # Summary
    summary = compute_portfolio_summary(df)
    print("\n[USASpending] Portfolio Summary:")
    print(f"  Total Awards:     {summary['total_awards']}")
    print(f"  Total Obligation:   ${summary['total_obligation']:,.0f}")
    print(f"  Average Award:      ${summary['avg_award']:,.0f}")
    print(f"  Median Award:       ${summary['median_award']:,.0f}")
    print(f"  Date Range:         {summary['date_range']}")
    print("\n  Top Agencies:")
    for agency, count in summary["agencies"].items():
        print(f"    {agency}: {count} awards")

    # Save metadata
    meta = {
        "source": "USASpending.gov",
        "api_url": USASPENDING_API,
        "agencies": TARGET_AGENCIES,
        "record_count": len(df),
        "total_obligation": float(summary["total_obligation"]),
        "fetched_at": datetime.now().isoformat(),
        "citation": "USASpending.gov, U.S. Department of the Treasury",
    }
    with open(DATA_DIR / "usaspending_metadata.json", "w") as f:
        json.dump(meta, f, indent=2)

    print("\n[USASpending] Done.")


if __name__ == "__main__":
    main()
