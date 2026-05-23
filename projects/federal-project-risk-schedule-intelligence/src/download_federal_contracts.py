#!/usr/bin/env python3
"""
Federal IT Contract Data Fetcher (USASpending.gov)
Fetches real federal IT contracts with period of performance data as proxy for project schedules.
"""

import requests
import json
import pandas as pd
from datetime import datetime
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

USASPENDING_API = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

def fetch_it_contracts(year=2024, max_pages=5):
    """Fetch federal IT contracts with period of performance data from USASpending.gov."""
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"
    
    all_contracts = []
    for page in range(1, max_pages + 1):
        payload = {
            "filters": {
                "award_type_codes": ["A", "B", "C", "D"],
                "time_period": [
                    {"start_date": start_date, "end_date": end_date}
                ]
            },
            "fields": [
                "Award ID", "Recipient Name", "Start Date", "End Date",
                "Award Amount", "Awarding Agency", "Awarding Sub Agency",
                "NAICS", "PSC",
                "Place of Performance State Code",
                "Description", "Last Modified Date"
            ],
            "page": page,
            "limit": 100,
            "sort": "Award Amount",
            "order": "desc"
        }
        
        try:
            resp = requests.post(USASPENDING_API, json=payload, timeout=90)
            resp.raise_for_status()
            data = resp.json()
            results = data.get('results', [])
            
            if not results:
                break
            
            for r in results:
                start = r.get('Start Date', '')
                end = r.get('End Date', '')
                
                duration_days = None
                if start and end:
                    try:
                        s = datetime.strptime(start, '%Y-%m-%d')
                        e = datetime.strptime(end, '%Y-%m-%d')
                        duration_days = (e - s).days
                    except:
                        pass
                
                all_contracts.append({
                    'award_id': r.get('Award ID'),
                    'recipient': r.get('Recipient Name'),
                    'start_date': start,
                    'end_date': end,
                    'duration_days': duration_days,
                    'award_amount': r.get('Award Amount'),
                    'agency': r.get('Awarding Agency'),
                    'sub_agency': r.get('Awarding Sub Agency'),
                    'naics_code': r.get('NAICS', {}).get('code') if isinstance(r.get('NAICS'), dict) else None,
                    'naics_desc': r.get('NAICS', {}).get('description') if isinstance(r.get('NAICS'), dict) else None,
                    'psc_code': r.get('PSC', {}).get('code') if isinstance(r.get('PSC'), dict) else None,
                    'psc_desc': r.get('PSC', {}).get('description') if isinstance(r.get('PSC'), dict) else None,
                    'state': r.get('Place of Performance State Code'),
                    'description': r.get('Description', '')[:200] if r.get('Description') else '',
                    'last_modified': r.get('Last Modified Date')
                })
            
            print(f"  Page {page}: {len(results)} contracts")
            
        except Exception as e:
            print(f"  Page {page} error: {e}")
            break
    
    return all_contracts

def main():
    print("=" * 60)
    print("Federal IT Contract Data Fetcher (USASpending.gov)")
    print("=" * 60)
    
    all_contracts = []
    for year in [2023, 2024]:
        print(f"\nFetching IT contracts for {year}...")
        contracts = fetch_it_contracts(year=year, max_pages=5)
        print(f"  Retrieved {len(contracts)} contracts")
        all_contracts.extend(contracts)
    
    print(f"\n{'='*60}")
    print(f"Total contracts retrieved: {len(all_contracts)}")
    
    if all_contracts:
        df = pd.DataFrame(all_contracts)
        
        df['award_amount'] = pd.to_numeric(df['award_amount'], errors='coerce').fillna(0)
        df['duration_days'] = pd.to_numeric(df['duration_days'], errors='coerce')
        
        # Filter to IT-related NAICS
        it_naics = ['541512', '541511', '541519', '541330', '511210']
        df_it = df[df['naics_code'].isin(it_naics)].copy()
        
        print(f"\nIT-related contracts (NAICS filter): {len(df_it)}")
        
        # Save both
        df.to_csv(os.path.join(DATA_DIR, 'federal_contracts_all.csv'), index=False)
        df_it.to_csv(os.path.join(DATA_DIR, 'federal_it_contracts.csv'), index=False)
        df_it.to_json(os.path.join(DATA_DIR, 'federal_it_contracts.json'), orient='records', indent=2)
        
        total_value = df_it['award_amount'].sum()
        avg_duration = df_it['duration_days'].mean()
        
        print(f"\nTotal IT contract value: ${total_value:,.2f}")
        print(f"Average duration: {avg_duration:.0f} days" if pd.notna(avg_duration) else "Average duration: N/A")
        
        print(f"\nBy Agency:")
        agency_summary = df_it.groupby('agency').agg({
            'award_id': 'count',
            'award_amount': 'sum',
            'duration_days': 'mean'
        }).rename(columns={'award_id': 'contract_count'}).sort_values('award_amount', ascending=False)
        for agency, row in agency_summary.head(8).iterrows():
            print(f"  {agency[:40]:<40} | {int(row['contract_count']):>3} contracts | ${row['award_amount']:>14,.0f} | {row['duration_days']:>5.0f}d avg")
        
        print(f"\nDuration Distribution:")
        dur_bins = pd.cut(df_it['duration_days'].dropna(), bins=[0, 180, 365, 730, 1095, 9999], 
                          labels=['<6mo', '6-12mo', '1-2yr', '2-3yr', '>3yr'])
        for bin_name, count in dur_bins.value_counts().sort_index().items():
            print(f"  {bin_name}: {count} contracts ({count/len(df_it):.1%})")
        
        print(f"\nSaved to federal_it_contracts.csv")
    
    summary = {
        'fetched_at': datetime.now().isoformat(),
        'contract_count': len(all_contracts),
        'it_contract_count': len(df_it) if all_contracts else 0,
        'total_value': float(df_it['award_amount'].sum()) if all_contracts and len(df_it) > 0 else 0,
        'source': 'USASpending.gov API',
        'naics_codes': ['541512', '541511', '541519', '541330', '511210'],
        'years': [2023, 2024]
    }
    with open(os.path.join(DATA_DIR, 'contracts_fetch_summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)
    
    return len(all_contracts)

if __name__ == '__main__':
    total = main()
    print(f"\nTotal records: {total}")