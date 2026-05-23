import pandas as pd
import numpy as np
from datetime import datetime
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')

def load_contract_data():
    """Load federal contract data."""
    path = os.path.join(DATA_DIR, 'federal_contracts_all.csv')
    if not os.path.exists(path):
        path = os.path.join(DATA_DIR, 'federal_it_contracts.csv')
    if not os.path.exists(path):
        print(f"ERROR: No contract data found. Run download_federal_contracts.py first.")
        return None
    return pd.read_csv(path)

def analyze_schedule_variance(df):
    """Analyze contract duration and schedule patterns."""
    print("=" * 60)
    print("Contract Schedule Variance Analysis")
    print("=" * 60)
    
    # Clean data
    df['duration_days'] = pd.to_numeric(df['duration_days'], errors='coerce')
    df['award_amount'] = pd.to_numeric(df['award_amount'], errors='coerce').fillna(0)
    
    valid_df = df[df['duration_days'].notna()].copy()
    
    print(f"\nTotal Contracts: {len(df)}")
    print(f"Contracts with valid dates: {len(valid_df)}")
    
    # Duration stats
    print(f"\nDuration Statistics:")
    print(f"  Mean: {valid_df['duration_days'].mean():.0f} days ({valid_df['duration_days'].mean()/365:.1f} years)")
    print(f"  Median: {valid_df['duration_days'].median():.0f} days")
    print(f"  Std: {valid_df['duration_days'].std():.0f} days")
    print(f"  Min: {valid_df['duration_days'].min():.0f} days")
    print(f"  Max: {valid_df['duration_days'].max():.0f} days")
    
    # Categorize by duration
    valid_df['duration_category'] = pd.cut(
        valid_df['duration_days'],
        bins=[0, 180, 365, 730, 1095, 9999],
        labels=['<6mo', '6-12mo', '1-2yr', '2-3yr', '>3yr']
    )
    
    print(f"\nDuration Distribution:")
    for cat, count in valid_df['duration_category'].value_counts().sort_index().items():
        print(f"  {cat}: {count} contracts ({count/len(valid_df):.1%})")
    
    # Agency-level analysis
    print(f"\nSchedule by Agency (Top 8 by avg duration):")
    agency_stats = valid_df.groupby('agency').agg({
        'duration_days': ['mean', 'median', 'std', 'count'],
        'award_amount': 'mean'
    }).round(0)
    agency_stats.columns = ['avg_duration', 'median_duration', 'duration_std', 'contract_count', 'avg_value']
    agency_stats = agency_stats.sort_values('avg_duration', ascending=False)
    
    for agency, row in agency_stats.head(8).iterrows():
        print(f"  {agency[:40]:<40} | {row['avg_duration']:>5.0f}d avg | {row['contract_count']:>3.0f} contracts | ${row['avg_value']:>12,.0f} avg")
    
    # Value-duration correlation
    corr = valid_df[['duration_days', 'award_amount']].corr().iloc[0, 1]
    print(f"\nValue-Duration Correlation: {corr:.3f}")
    
    # Risk factors
    valid_df['high_value'] = (valid_df['award_amount'] > valid_df['award_amount'].quantile(0.75)).astype(int)
    valid_df['long_duration'] = (valid_df['duration_days'] > 1095).astype(int)
    
    # Save results
    valid_df.to_csv(os.path.join(DATA_DIR, 'contracts_with_schedule_analysis.csv'), index=False)
    agency_stats.to_csv(os.path.join(DATA_DIR, 'agency_schedule_stats.csv'))
    
    return valid_df, agency_stats

def compute_schedule_performance_index(df):
    """Compute SPI-like metric from contract duration vs industry norms."""
    # Group by NAICS to get industry baseline
    naics_baseline = df.groupby('naics_code')['duration_days'].median().to_dict()
    
    # SPI estimate = baseline / actual (higher = better/on-track)
    df['naics_baseline'] = df['naics_code'].map(naics_baseline).fillna(df['duration_days'].median())
    df['spi_estimate'] = np.where(
        df['duration_days'] > 0,
        df['naics_baseline'] / df['duration_days'],
        1.0
    )
    df['spi_estimate'] = df['spi_estimate'].clip(lower=0.3, upper=1.5)
    
    print(f"\nEstimated SPI Summary:")
    print(f"  Mean SPI: {df['spi_estimate'].mean():.3f}")
    print(f"  SPI < 0.8 (at risk): {(df['spi_estimate'] < 0.8).sum()} contracts")
    print(f"  SPI < 0.6 (critical): {(df['spi_estimate'] < 0.6).sum()} contracts")
    
    return df

def main():
    df = load_contract_data()
    if df is None:
        return
    
    df, agency_stats = analyze_schedule_variance(df)
    df = compute_schedule_performance_index(df)
    
    # Save enhanced dataset for hybrid model
    df.to_csv(os.path.join(DATA_DIR, 'contracts_schedule_enhanced.csv'), index=False)
    
    print(f"\nSchedule analysis complete. Enhanced data saved.")
    return df

if __name__ == '__main__':
    main()
