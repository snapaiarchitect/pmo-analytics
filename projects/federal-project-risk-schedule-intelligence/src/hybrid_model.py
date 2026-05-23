import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

def load_enhanced_data():
    """Load schedule-enhanced contract data."""
    path = os.path.join(DATA_DIR, 'contracts_schedule_enhanced.csv')
    if not os.path.exists(path):
        print(f"ERROR: {path} not found. Run schedule_analyzer.py first.")
        return None
    return pd.read_csv(path)

def load_agency_risk():
    """Load agency risk scores."""
    path = os.path.join(DATA_DIR, 'agency_risk_scores.csv')
    if os.path.exists(path):
        return pd.read_csv(path, index_col=0)
    return None

def compute_schedule_risk_score(row, agency_risk_map):
    """
    Compute a 0-100 Schedule Risk Score for a contract.
    Combines agency risk, value risk, SPI deviation, and duration category.
    """
    score = 0
    
    # 1. Agency Risk (0-25 points)
    agency = row.get('agency', 'Unknown')
    agency_risk = agency_risk_map.get(agency, 0.3)
    score += min(agency_risk * 25, 25)
    
    # 2. Value Risk (0-25 points) - larger contracts = more complex
    amount = row.get('award_amount', 0)
    if amount > 1e10:  # > $10B
        score += 25
    elif amount > 1e9:  # > $1B
        score += 20
    elif amount > 1e8:  # > $100M
        score += 15
    elif amount > 1e7:  # > $10M
        score += 10
    else:
        score += 5
    
    # 3. SPI Risk (0-25 points) - SPI < 1 means behind schedule
    spi = row.get('spi_estimate', 1.0)
    if spi < 0.6:
        score += 25
    elif spi < 0.8:
        score += 20
    elif spi < 1.0:
        score += 10
    else:
        score += 0
    
    # 4. Duration Risk (0-25 points) - very long contracts = riskier
    duration = row.get('duration_days', 365)
    if duration > 3650:  # > 10 years
        score += 25
    elif duration > 2190:  # > 6 years
        score += 20
    elif duration > 1095:  # > 3 years
        score += 15
    elif duration > 730:  # > 2 years
        score += 10
    else:
        score += 5
    
    # Monte Carlo confidence intervals for the risk score
    np.random.seed(42)
    n_simulations = 1000
    
    # Add noise to simulate uncertainty
    noise = np.random.normal(0, 5, n_simulations)
    simulated_scores = np.clip(score + noise, 0, 100)
    
    return {
        'risk_score': round(float(score), 1),
        'p50': round(float(np.percentile(simulated_scores, 50)), 1),
        'p80': round(float(np.percentile(simulated_scores, 80)), 1),
        'p95': round(float(np.percentile(simulated_scores, 95)), 1),
        'base_duration': float(duration),
        'spi': float(spi),
        'award_amount': float(amount),
        'agency_risk': float(agency_risk)
    }

def build_hybrid_model():
    """Build risk-adjusted schedule forecast for all contracts."""
    print("=" * 60)
    print("Hybrid Risk-Adjusted Schedule Forecast Model")
    print("=" * 60)
    
    df = load_enhanced_data()
    if df is None:
        return
    
    agency_risk_df = load_agency_risk()
    agency_risk_map = {}
    if agency_risk_df is not None:
        agency_risk_map = agency_risk_df['is_long_duration'].to_dict()
    
    print(f"\nProcessing {len(df)} contracts...")
    
    # Compute risk score for each contract
    results = []
    for idx, row in df.iterrows():
        if idx % 100 == 0:
            print(f"  Processed {idx}/{len(df)} contracts...")
        
        result = compute_schedule_risk_score(row, agency_risk_map)
        result['award_id'] = row.get('award_id', f'award_{idx}')
        result['recipient'] = row.get('recipient', 'Unknown')
        result['agency'] = row.get('agency', 'Unknown')
        result['naics_code'] = row.get('naics_code', 'Unknown')
        result['sub_agency'] = row.get('sub_agency', 'Unknown')
        results.append(result)
    
    # Build results dataframe
    results_df = pd.DataFrame(results)
    
    # Classify risk levels based on P80 score
    results_df['risk_level'] = pd.cut(
        results_df['p80'],
        bins=[0, 40, 60, 80, 100],
        labels=['Low', 'Medium', 'High', 'Critical']
    )
    
    print(f"\n" + "=" * 60)
    print("FORECAST RESULTS")
    print("=" * 60)
    print(f"Contracts analyzed: {len(results_df)}")
    print(f"\nRisk Distribution:")
    risk_dist = results_df['risk_level'].value_counts()
    for level, count in risk_dist.items():
        print(f"  {level}: {count} contracts ({count/len(results_df):.1%})")
    
    print(f"\nRisk Score Statistics:")
    print(f"  Mean Risk Score: {results_df['risk_score'].mean():.1f}/100")
    print(f"  Mean P80 Score: {results_df['p80'].mean():.1f}/100")
    
    print(f"\nTop 10 At-Risk Contracts (by P80 score):")
    top_risk = results_df.nlargest(10, 'p80')[['award_id', 'recipient', 'agency', 'risk_score', 'p80', 'p95', 'risk_level']]
    for _, row in top_risk.iterrows():
        print(f"  {str(row['award_id'])[:20]:<20} | {str(row['recipient'])[:25]:<25} | {str(row['agency'])[:20]:<20} | Score: {row['p80']:>5.1f} | {row['risk_level']}")
    
    # Agency summary
    print(f"\nAgency Risk Summary:")
    agency_summary = results_df.groupby('agency').agg({
        'risk_score': 'mean',
        'p80': 'mean',
        'award_id': 'count'
    }).rename(columns={'award_id': 'contract_count'}).sort_values('p80', ascending=False)
    for agency, row in agency_summary.head(8).iterrows():
        print(f"  {agency[:40]:<40} | {row['p80']:>5.1f} avg | {int(row['contract_count']):>3} contracts")
    
    # Save results
    results_df.to_csv(os.path.join(DATA_DIR, 'hybrid_forecast_results.csv'), index=False)
    results_df.to_json(os.path.join(DATA_DIR, 'hybrid_forecast_results.json'), orient='records', indent=2)
    
    # Save summary
    summary = {
        'generated_at': datetime.now().isoformat(),
        'total_contracts': len(results_df),
        'risk_distribution': risk_dist.to_dict(),
        'mean_risk_score': float(results_df['risk_score'].mean()),
        'mean_p80_score': float(results_df['p80'].mean()),
        'critical_contracts': int((results_df['risk_level'] == 'Critical').sum()),
        'high_contracts': int((results_df['risk_level'] == 'High').sum())
    }
    with open(os.path.join(MODEL_DIR, 'hybrid_model_summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nResults saved to hybrid_forecast_results.csv")
    return results_df

def main():
    results = build_hybrid_model()
    if results is not None:
        print(f"\nHybrid model complete. {len(results)} contracts analyzed.")
    return results

if __name__ == '__main__':
    main()