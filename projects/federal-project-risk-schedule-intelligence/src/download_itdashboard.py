#!/usr/bin/env python3
"""
ITDashboard.gov Federal IT Project Data Fetcher
Fetches real federal IT project performance data from ITDashboard.gov API.
Includes cost variance, schedule variance, project health, and risk data.
"""

import requests
import json
import pandas as pd
from datetime import datetime
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

ITDASHBOARD_API = "https://itdashboard.gov/api/v1/ITDB2/"

def fetch_investments(year=2024):
    """Fetch major IT investments across all agencies."""
    url = f"{ITDASHBOARD_API}investments?budgetYear={year}"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        investments = []
        if isinstance(data, dict) and 'result' in data:
            items = data['result']
        elif isinstance(data, list):
            items = data
        else:
            items = data.get('investments', data.get('results', []))
        
        for inv in items:
            if not isinstance(inv, dict):
                continue
            investments.append({
                'uii': inv.get('uii') or inv.get('uniqueInvestmentIdentifier'),
                'agency_code': inv.get('agencyCode') or inv.get('agency_code'),
                'agency_name': inv.get('agencyName') or inv.get('agency_name'),
                'title': inv.get('investmentTitle') or inv.get('title'),
                'total_lifecycle_cost': inv.get('totalLifeCycleCost') or inv.get('total_lifecycle_cost'),
                'cio_evaluation': inv.get('cioEvaluation') or inv.get('cio_evaluation'),
                'year': year
            })
        return investments
    except Exception as e:
        print(f"Error fetching investments: {e}")
        return []

def fetch_projects(year=2024):
    """Fetch individual IT projects with variance data."""
    url = f"{ITDASHBOARD_API}projects?budgetYear={year}"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        projects = []
        if isinstance(data, dict) and 'result' in data:
            items = data['result']
        elif isinstance(data, list):
            items = data
        else:
            items = data.get('projects', data.get('results', []))
        
        for p in items:
            if not isinstance(p, dict):
                continue
            # Extract schedule/cost variance data
            projects.append({
                'project_id': p.get('projectId') or p.get('project_id'),
                'investment_uii': p.get('uniqueInvestmentIdentifier') or p.get('uii'),
                'agency_code': p.get('agencyCode') or p.get('agency_code'),
                'project_name': p.get('projectName') or p.get('project_name'),
                'project_health': p.get('projectHealth') or p.get('project_health'),
                'cost_variance': p.get('costVariance') or p.get('cost_variance'),
                'schedule_variance_days': p.get('scheduleVarianceDayAmount') or p.get('schedule_variance_days'),
                'planned_start': p.get('plannedStartDate') or p.get('planned_start'),
                'planned_end': p.get('plannedEndDate') or p.get('planned_end'),
                'projected_end': p.get('projectedEndDate') or p.get('projected_end'),
                'actual_end': p.get('actualEndDate') or p.get('actual_end'),
                'planned_cost': p.get('plannedTotalCost') or p.get('planned_cost'),
                'projected_cost': p.get('projectedTotalCost') or p.get('projected_cost'),
                'actual_cost': p.get('actualTotalCost') or p.get('actual_cost'),
                'status': p.get('projectStatus') or p.get('status'),
                'year': year
            })
        return projects
    except Exception as e:
        print(f"Error fetching projects: {e}")
        return []

def fetch_risks(year=2024):
    """Fetch risk register data for IT projects."""
    url = f"{ITDASHBOARD_API}risks?budgetYear={year}"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        risks = []
        if isinstance(data, dict) and 'result' in data:
            items = data['result']
        elif isinstance(data, list):
            items = data
        else:
            items = data.get('risks', data.get('results', []))
        
        for r in items:
            if not isinstance(r, dict):
                continue
            risks.append({
                'risk_id': r.get('riskId') or r.get('risk_id'),
                'uii': r.get('uniqueInvestmentIdentifier') or r.get('uii'),
                'agency_code': r.get('agencyCode') or r.get('agency_code'),
                'risk_area': r.get('riskArea') or r.get('risk_area'),
                'risk_probability': r.get('riskProbability') or r.get('risk_probability'),
                'risk_impact': r.get('riskImpact') or r.get('risk_impact'),
                'risk_score': r.get('riskScore') or r.get('risk_score'),
                'mitigation_strategy': r.get('mitigationStrategy') or r.get('mitigation_strategy'),
                'year': year
            })
        return risks
    except Exception as e:
        print(f"Error fetching risks: {e}")
        return []

def fetch_agencies():
    """Fetch agency list from IT Dashboard."""
    url = f"{ITDASHBOARD_API}agencies"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict) and 'result' in data:
            return data['result']
        elif isinstance(data, list):
            return data
        else:
            return data.get('agencies', [])
    except Exception as e:
        print(f"Error fetching agencies: {e}")
        return []

def main():
    print("=" * 60)
    print("ITDashboard.gov Federal IT Project Data Fetcher")
    print("=" * 60)
    
    # Fetch agencies first
    print("\n1. Fetching agency list...")
    agencies = fetch_agencies()
    agency_count = len(agencies) if agencies else 0
    print(f"   Found {agency_count} agencies")
    if agencies:
        with open(os.path.join(DATA_DIR, 'itdashboard_agencies.json'), 'w') as f:
            json.dump(agencies, f, indent=2)
    
    # Fetch investments
    print("\n2. Fetching IT investments (FY2024)...")
    investments = fetch_investments(year=2024)
    print(f"   Retrieved {len(investments)} investments")
    if investments:
        df_inv = pd.DataFrame(investments)
        df_inv.to_csv(os.path.join(DATA_DIR, 'itdashboard_investments.csv'), index=False)
        df_inv.to_json(os.path.join(DATA_DIR, 'itdashboard_investments.json'), orient='records', indent=2)
        # Agency summary
        agency_summary = df_inv.groupby('agency_name').agg({
            'uii': 'count',
            'total_lifecycle_cost': 'sum'
        }).rename(columns={'uii': 'investment_count'})
        agency_summary.to_csv(os.path.join(DATA_DIR, 'itdashboard_agency_summary.csv'))
        print(f"   Saved to itdashboard_investments.csv ({len(df_inv)} records)")
    
    # Fetch projects
    print("\n3. Fetching IT projects with variance data...")
    projects = fetch_projects(year=2024)
    print(f"   Retrieved {len(projects)} projects")
    if projects:
        df_proj = pd.DataFrame(projects)
        # Compute derived fields
        df_proj['has_delay'] = df_proj['schedule_variance_days'].apply(
            lambda x: x > 0 if pd.notna(x) else False
        )
        df_proj['cost_overrun'] = df_proj.apply(
            lambda row: (row['projected_cost'] or 0) > (row['planned_cost'] or 0) if pd.notna(row.get('projected_cost')) else False,
            axis=1
        )
        df_proj.to_csv(os.path.join(DATA_DIR, 'itdashboard_projects.csv'), index=False)
        df_proj.to_json(os.path.join(DATA_DIR, 'itdashboard_projects.json'), orient='records', indent=2)
        
        # Health summary
        health_summary = df_proj['project_health'].value_counts()
        print(f"\n   Project Health Summary:")
        for health, count in health_summary.items():
            print(f"      {health}: {count} projects")
        
        print(f"   Saved to itdashboard_projects.csv ({len(df_proj)} records)")
    
    # Fetch risks
    print("\n4. Fetching risk register data...")
    risks = fetch_risks(year=2024)
    print(f"   Retrieved {len(risks)} risk entries")
    if risks:
        df_risk = pd.DataFrame(risks)
        df_risk.to_csv(os.path.join(DATA_DIR, 'itdashboard_risks.csv'), index=False)
        df_risk.to_json(os.path.join(DATA_DIR, 'itdashboard_risks.json'), orient='records', indent=2)
        print(f"   Saved to itdashboard_risks.csv ({len(df_risk)} records)")
    
    # Master summary
    print("\n" + "=" * 60)
    print("FETCH SUMMARY")
    print("=" * 60)
    print(f"Agencies:        {agency_count}")
    print(f"Investments:     {len(investments)}")
    print(f"Projects:        {len(projects)}")
    print(f"Risk entries:    {len(risks)}")
    print(f"\nData saved to: {DATA_DIR}")
    
    # Combined dataset for downstream analysis
    if investments and projects:
        combined = {
            'fetched_at': datetime.now().isoformat(),
            'agency_count': agency_count,
            'investment_count': len(investments),
            'project_count': len(projects),
            'risk_count': len(risks),
            'sources': ['ITDashboard.gov API']
        }
        with open(os.path.join(DATA_DIR, 'fetch_summary.json'), 'w') as f:
            json.dump(combined, f, indent=2)
    
    return len(projects) + len(investments)

if __name__ == '__main__':
    total = main()
    print(f"\nTotal records fetched: {total}")
