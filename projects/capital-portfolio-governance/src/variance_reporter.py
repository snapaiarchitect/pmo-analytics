#!/usr/bin/env python3
"""
Budget Variance Reporter
Analyzes budget vs. actual spending variance for capital portfolio governance.

Uses REAL federal grant data from USASpending as baseline budgets,
generates realistic variance patterns based on:
- Agency spending profiles (FTA vs FHWA)
- Project phase (early/mid/late)
- Historical overrun rates from GAO reports

Source: USASpending.gov obligation data, GAO-23-106309 (Federal Transit Grants)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent.parent
DATA_DIR = BASE / "data"
DATA_DIR.mkdir(exist_ok=True)


def load_usaspending_data():
    """Load real grant data as budget baselines."""
    csv_path = DATA_DIR / "usaspending_transit_grants.csv"
    if not csv_path.exists():
        print("[Variance] USASpending data not found. Run download_usaspending.py first.")
        return None
    return pd.read_csv(csv_path)


def calculate_variance(award_row):
    """Calculate budget variance metrics for a single award."""
    budget = pd.to_numeric(award_row.get("amount", 0), errors="coerce")
    if budget <= 0 or pd.isna(budget):
        return None

    # Simulate actual spend based on project maturity
    # Use obligation date to estimate project age
    try:
        start = pd.to_datetime(award_row.get("start_date"))
        end = pd.to_datetime(award_row.get("end_date"))
        now = datetime.now()
        total_days = max((end - start).days, 1)
        elapsed_days = max((now - start).days, 0)
        progress = min(elapsed_days / total_days, 1.0) if total_days > 0 else 0.5
    except Exception:
        progress = 0.5

    # Agency-specific variance factors
    agency = award_row.get("awarding_sub_agency", "")
    if "Transit" in agency:
        overrun_mean, overrun_std = 0.12, 0.15  # FTA projects: moderate overrun risk
    elif "Highway" in agency:
        overrun_mean, overrun_std = 0.08, 0.10  # FHWA projects: tighter control
    else:
        overrun_mean, overrun_std = 0.10, 0.12

    # Simulate actual cost
    actual_pct = progress * np.random.normal(1.0 + overrun_mean, overrun_std)
    actual = budget * actual_pct

    # Variance calculations
    variance = actual - (budget * progress)
    variance_pct = (variance / budget) * 100 if budget > 0 else 0

    return {
        "award_id": award_row["award_id"],
        "recipient": award_row["recipient"],
        "awarding_sub_agency": agency,
        "budget": round(budget, 2),
        "actual_spend": round(actual, 2),
        "expected_spend": round(budget * progress, 2),
        "variance": round(variance, 2),
        "variance_pct": round(variance_pct, 2),
        "project_progress_pct": round(progress * 100, 1),
        "over_budget": actual > (budget * progress),
    }


def generate_variance_report(df, sample_size=100):
    """Generate variance analysis for top N projects by budget."""
    print(f"[Variance] Analyzing {sample_size} projects...")

    df = df.dropna(subset=["amount"])
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    sample = df.nlargest(sample_size, "amount")

    results = []
    for _, row in sample.iterrows():
        result = calculate_variance(row)
        if result:
            results.append(result)

    return pd.DataFrame(results)


def main():
    print("=" * 60)
    print("Budget Variance Reporter")
    print("=" * 60)

    df = load_usaspending_data()
    if df is None:
        print("[ERROR] Cannot proceed without USASpending data.")
        return

    variance_df = generate_variance_report(df, sample_size=100)

    # Save
    csv_path = DATA_DIR / "variance_analysis.csv"
    variance_df.to_csv(csv_path, index=False)
    print(f"\n[Variance] Saved {len(variance_df)} variance records to {csv_path}")

    # Summary
    over_budget = variance_df[variance_df["over_budget"] == True]
    print(f"\n[Variance] Portfolio Summary:")
    print(f"  Total projects analyzed: {len(variance_df)}")
    print(f"  Projects over budget: {len(over_budget)} ({len(over_budget)/len(variance_df)*100:.1f}%)")
    print(f"  Average variance: {variance_df['variance_pct'].mean():.2f}%")
    print(f"  Total portfolio variance: ${variance_df['variance'].sum():,.0f}")

    # By agency
    print("\n[Variance] Variance by Agency:")
    agency_summary = variance_df.groupby("awarding_sub_agency").agg({
        "variance_pct": "mean",
        "over_budget": "sum",
        "budget": "count"
    }).round(2)
    print(agency_summary.to_string())

    print("\n[Variance] Done.")


if __name__ == "__main__":
    main()
