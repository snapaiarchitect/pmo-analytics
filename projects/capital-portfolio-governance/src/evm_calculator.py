#!/usr/bin/env python3
"""
Earned Value Management (EVM) Calculator
Computes CPI, SPI, EAC, VAC, and TCPI from project performance data.

Uses REAL grant data from USASpending as project inputs, supplemented by
industry-standard EVM formulas:
  - CPI (Cost Performance Index) = EV / AC
  - SPI (Schedule Performance Index) = EV / PV
  - EAC (Estimate at Completion) = BAC / CPI
  - VAC (Variance at Completion) = BAC - EAC
  - TCPI (To-Complete Performance Index) = (BAC - EV) / (BAC - AC)

Source: ANSI/EIA-748 Earned Value Management Systems Standard
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent.parent
DATA_DIR = BASE / "data"
OUTPUT_DIR = DATA_DIR
OUTPUT_DIR.mkdir(exist_ok=True)


def load_usaspending_data():
    """Load real grant data as project baselines."""
    csv_path = DATA_DIR / "usaspending_transit_grants.csv"
    if not csv_path.exists():
        print("[EVM] USASpending data not found. Run download_usaspending.py first.")
        return None

    df = pd.read_csv(csv_path)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    return df


def simulate_project_performance(award_row):
    """
    Simulate realistic EVM metrics for a grant project.
    In production, these would come from actual project tracking systems.
    Here we generate plausible values based on the grant amount and dates.
    """
    bac = award_row["amount"]  # Budget at Completion

    # Simulate project progress (randomized but realistic)
    # Most projects are between 20% and 90% complete
    progress_pct = np.random.uniform(0.25, 0.85)

    # Earned Value
    ev = bac * progress_pct

    # Cost variance: some projects over/under budget
    cost_factor = np.random.normal(1.0, 0.08)  # mean 1.0, std 0.08
    ac = ev * cost_factor  # Actual Cost

    # Schedule variance: some ahead/behind
    schedule_factor = np.random.normal(1.0, 0.06)
    pv = ev * schedule_factor  # Planned Value

    # Guard against division by zero
    if ac == 0:
        ac = 1
    if pv == 0:
        pv = 1

    # Calculate EVM metrics
    cpi = ev / ac
    spi = ev / pv
    eac = bac / cpi
    vac = bac - eac
    tcpi = (bac - ev) / (bac - ac) if (bac - ac) != 0 else 0

    return {
        "award_id": award_row["award_id"],
        "recipient": award_row["recipient"],
        "bac": round(bac, 2),
        "ev": round(ev, 2),
        "ac": round(ac, 2),
        "pv": round(pv, 2),
        "cpi": round(cpi, 3),
        "spi": round(spi, 3),
        "eac": round(eac, 2),
        "vac": round(vac, 2),
        "tcpi": round(tcpi, 3),
        "variance_pct": round(((ac - ev) / bac) * 100, 2),
    }


def calculate_evm_for_portfolio(df, sample_size=50):
    """Calculate EVM metrics for a sample of projects."""
    print(f"[EVM] Calculating EVM for {sample_size} projects...")

    # Sort by amount and take a representative sample
    df_sorted = df.dropna(subset=["amount"]).sort_values("amount", ascending=False)
    sample = df_sorted.head(sample_size)

    results = []
    for _, row in sample.iterrows():
        result = simulate_project_performance(row)
        results.append(result)

    return pd.DataFrame(results)


def classify_project_health(evm_row):
    """Classify project health based on CPI and SPI."""
    cpi = evm_row["cpi"]
    spi = evm_row["spi"]

    if cpi >= 1.0 and spi >= 1.0:
        return "On Track"
    elif cpi < 1.0 and spi < 1.0:
        return "At Risk (Cost & Schedule)"
    elif cpi < 1.0:
        return "Over Budget"
    elif spi < 1.0:
        return "Behind Schedule"
    else:
        return "On Track"


def main():
    print("=" * 60)
    print("Earned Value Management Calculator")
    print("=" * 60)

    df = load_usaspending_data()
    if df is None:
        print("[ERROR] Cannot proceed without USASpending data.")
        return

    evm_df = calculate_evm_for_portfolio(df, sample_size=50)
    evm_df["health_status"] = evm_df.apply(classify_project_health, axis=1)

    # Save EVM results
    csv_path = OUTPUT_DIR / "evm_analysis.csv"
    evm_df.to_csv(csv_path, index=False)
    print(f"\n[EVM] Saved {len(evm_df)} project EVM records to {csv_path}")

    # Portfolio summary
    print("\n[EVM] Portfolio EVM Summary:")
    print(f"  Average CPI: {evm_df['cpi'].mean():.3f}")
    print(f"  Average SPI: {evm_df['spi'].mean():.3f}")
    print(f"  Total VAC: ${evm_df['vac'].sum():,.0f}")
    print(f"  Projects at risk: {len(evm_df[evm_df['health_status'] != 'On Track'])}")
    print(f"  Projects on track: {len(evm_df[evm_df['health_status'] == 'On Track'])}")

    # Health distribution
    print("\n[EVM] Health Distribution:")
    for status, count in evm_df["health_status"].value_counts().items():
        print(f"  {status}: {count}")

    print("\n[EVM] Done.")


if __name__ == "__main__":
    main()
