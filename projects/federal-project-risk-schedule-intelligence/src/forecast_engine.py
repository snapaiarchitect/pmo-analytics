import pandas as pd
import numpy as np
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def generate_confidence_intervals():
    """Generate confidence interval summary for executive reporting."""
    print("=" * 60)
    print("Forecast Confidence Intervals")
    print("=" * 60)
    
    path = os.path.join(DATA_DIR, 'hybrid_forecast_results.csv')
    if not os.path.exists(path):
        print(f"ERROR: {path} not found. Run hybrid_model.py first.")
        return
    
    df = pd.read_csv(path)
    
    # Overall confidence metrics
    print(f"\nPortfolio-Level Risk Scores:")
    print(f"  P50 (Median): {df['p50'].mean():.1f}/100")
    print(f"  P80 (Likely): {df['p80'].mean():.1f}/100")
    print(f"  P95 (Worst Case): {df['p95'].mean():.1f}/100")
    
    # By agency
    print(f"\nConfidence by Agency (Top 8 by P80 score):")
    agency_ci = df.groupby('agency').agg({
        'p50': 'mean',
        'p80': 'mean',
        'p95': 'mean',
        'award_id': 'count'
    }).rename(columns={'award_id': 'contract_count'}).sort_values('p80', ascending=False)
    
    for agency, row in agency_ci.head(8).iterrows():
        print(f"  {agency}: P50={row['p50']:.1f}, P80={row['p80']:.1f}, P95={row['p95']:.1f} ({int(row['contract_count'])} contracts)")
    
    # Early warning contracts (P80 > 80)
    early_warning = df[df['p80'] > 80]
    print(f"\nEarly Warning Contracts (P80 > 80): {len(early_warning)}")
    print(f"  These contracts have >80% probability of high schedule risk")
    
    # Save CI report
    ci_report = {
        'portfolio': {
            'p50_mean': float(df['p50'].mean()),
            'p80_mean': float(df['p80'].mean()),
            'p95_mean': float(df['p95'].mean()),
            'total_contracts': len(df)
        },
        'by_agency': agency_ci.reset_index().to_dict('records'),
        'early_warning_count': len(early_warning),
        'early_warning_contracts': early_warning[['award_id', 'recipient', 'agency', 'p80', 'risk_level']].head(20).to_dict('records')
    }
    
    with open(os.path.join(DATA_DIR, 'confidence_intervals.json'), 'w') as f:
        json.dump(ci_report, f, indent=2)
    
    print(f"\nConfidence interval report saved.")
    return ci_report

def main():
    generate_confidence_intervals()

if __name__ == '__main__':
    main()
