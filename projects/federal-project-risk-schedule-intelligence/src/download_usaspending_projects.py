#!/usr/bin/env python3
"""
USASpending.gov Project Contract Link Fetcher
Fetches contract/award data linked to federal IT projects.
"""

import requests
import json
import pandas as pd
from datetime import datetime
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

USASPENDING_API = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

def fetch_it_contracts(limit=500):
    """Fetch federal IT-related contracts from USASpending.gov."""
    payload = {
        "filters": {
            "award_type_codes": ["A", "B", "C", "D"],
            "agencies": [
                {"type": "awarding", "tier": "toptier", "name": "Department of Defense"},
                {"type": "awarding", "tier": "toptier", "name": "Department of Health and Human Services"},
                {"type": "awarding", "tier": "toptier", "name": "Department of Homeland Security"},
                {"type": "awarding", "tier": "toptier", "name": "Department of Veterans Affairs"},
                {"type": "awarding", "tier": "toptier", "name": "National Aeronautics and Space Administration"},
                {"type": "awarding", "tier": "toptier", "name": "Department of Transportation"},
                {"type": "awarding", "tier": "toptier", "name": "Department of the Treasury"},
                {"type": "awarding", "tier": "toptier", "name": "General Services Administration"}
            ],
            "naics_codes": ["541512", "541511", "541519"],
            "time_period": [
                {"start_date": "2020-01-01", "end_date": "2024-12-31"}
            ]
        },
        "fields": [
            "Award ID", "Recipient Name", "Start Date", "End Date",
            "Award Amount", "Awarding Agency", "Awarding Sub Agency",
            "Contract Award Type", "Product or Service Code",
            "Place of Performance City", "Place of Performance State"
        ],
        "page": 1,
        "limit": limit,
        "sort": "Award Amount",
        "order": "desc"
    }
    
    try:
        resp = requests.post(USASPENDING_API, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        results = data.get('results', [])
        
        contracts = []
        for r in results:
            contracts.append({
                'award_id': r.get('Award ID'),
                'recipient': r.get('Recipient Name'),
                'start_date': r.get('Start Date'),
                'end_date': r.get('End Date'),
                'award_amount': r.get('Award Amount'),
                'agency': r.get('Awarding Agency'),
                'sub_agency': r.get('Awarding Sub Agency'),
                'award_type': r.get('Contract Award Type'),
                'naics': r.get('Product or Service Code'),
                'city': r.get('Place of Performance City'),
                'state': r.get('Place of Performance State')
            })
        return contracts
    except Exception as e:
        print(f"Error fetching contracts: {e}")
        return []

def main():
    print("=" * 60)
    print("USASpending.gov IT Contract Fetcher")
    print("=" * 60)
    
    print("\nFetching IT contracts (NAICS 541512/541511/541519)...")
    contracts = fetch_it_contracts(limit=500)
    print(f"Retrieved {len(contracts)} contracts")
    
    if contracts:
        df = pd.DataFrame(contracts)
        df.to_csv(os.path.join(DATA_DIR, 'usaspending_it_contracts.csv'), index=False)
        df.to_json(os.path.join(DATA_DIR, 'usaspending_it_contracts.json'), orient='records', indent=2)
        
        # Summary
        total_value = df['award_amount'].sum()
        print(f"\nTotal contract value: ${total_value:,.2f}")
        print(f"By Agency:")
        agency_summary = df.groupby('agency').agg({
            'award_id': 'count',
            'award_amount': 'sum'
        }).rename(columns={'award_id': 'contract_count'}).sort_values('award_amount', ascending=False)
        for agency, row in agency_summary.head(8).iterrows():
            print(f"  {agency}: {int(row['contract_count'])} contracts, ${row['award_amount']:,.0f}")
        
        print(f"\nSaved to usaspending_it_contracts.csv")
    
    summary = {
        'fetched_at': datetime.now().isoformat(),
        'contract_count': len(contracts),
        'total_value': sum(c['award_amount'] for c in contracts if c['award_amount']) if contracts else 0,
        'source': 'USASpending.gov API'
    }
    with open(os.path.join(DATA_DIR, 'usaspending_fetch_summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)
    
    return len(contracts)

if __name__ == '__main__':
    total = main()
    print(f"\nTotal records: {total}")
