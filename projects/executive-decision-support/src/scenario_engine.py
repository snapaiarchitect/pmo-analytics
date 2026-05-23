#!/usr/bin/env python3
"""
Scenario Engine — What-if Budget Modeling for Municipal Planning

Input: Budget allocation percentages across DC agencies
Baseline: Historical performance metrics from downloaded data
Output: Projected outcomes using linear regression from historical correlation
Sensitivity: ±10% budget shift impact
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LinearRegression

BASE = Path(__file__).parent.parent
DATA_DIR = BASE / "data"

AGENCIES = [
    "Department of Health",
    "Metropolitan Police Department",
    "Department of Transportation",
    "Department of Energy & Environment",
    "Office of the Chief Technology Officer",
    "Department of Human Services",
    "Department of Parks and Recreation",
    "DC Public Schools",
    "Department of Employment Services",
    "Department of Consumer and Regulatory Affairs",
]

# Historical baseline budget shares (approximate FY2024 DC budget proportions)
HISTORICAL_SHARES = {
    "Department of Health": 0.08,
    "Metropolitan Police Department": 0.18,
    "Department of Transportation": 0.07,
    "Department of Energy & Environment": 0.04,
    "Office of the Chief Technology Officer": 0.03,
    "Department of Human Services": 0.12,
    "Department of Parks and Recreation": 0.05,
    "DC Public Schools": 0.28,
    "Department of Employment Services": 0.06,
    "Department of Consumer and Regulatory Affairs": 0.04,
}

# Total FY2024 DC budget ~ $20.6B
TOTAL_BUDGET = 20_600_000_000

def load_dc_metrics():
    """Load agency performance metrics."""
    path = DATA_DIR / "dc_agency_metrics.json"
    if path.exists():
        with open(path) as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        print(f"[Scenario] Loaded {len(df)} agency metrics")
        return df
    print("[Scenario] No metrics file found. Using default baseline.")
    return pd.DataFrame({
        "agency_name": AGENCIES,
        "metric_name": ["Composite Performance Index"] * len(AGENCIES),
        "value": [65, 72, 58, 80, 85, 60, 75, 70, 55, 68],
        "reporting_period": ["2024-Q1"] * len(AGENCIES),
    })

def build_regression_model(df):
    """
    Build a simple linear model: performance ~ budget_share.
    Uses synthetic but informed correlation for demonstration.
    """
    df = df.copy()
    df["budget_share"] = df["agency_name"].map(HISTORICAL_SHARES)
    df = df.dropna(subset=["budget_share", "value"])
    if len(df) < 2:
        print("[Scenario] Insufficient data for regression. Using heuristic model.")
        return None, df

    X = df[["budget_share"]].values
    y = df["value"].values
    model = LinearRegression()
    model.fit(X, y)
    r2 = model.score(X, y)
    print(f"[Scenario] Regression fit: R² = {r2:.3f}")
    return model, df, r2

def run_scenario(allocations):
    """
    Run what-if scenario.
    allocations: dict {agency: percentage (0-1)}
    Returns projected outcome scores.
    """
    df = load_dc_metrics()
    model, baseline_df, r2 = build_regression_model(df)

    results = []
    # Precompute normalized baseline (0-100 scale) for all agencies
    baseline_perf = {}
    for agency in AGENCIES:
        raw = baseline_df[baseline_df["agency_name"] == agency]["value"]
        if not raw.empty:
            baseline_perf[agency] = min(100.0, float(raw.iloc[0]))
        else:
            baseline_perf[agency] = 65.0

    for agency in AGENCIES:
        share = allocations.get(agency, HISTORICAL_SHARES.get(agency, 0.05))
        base = baseline_perf[agency]
        base_share = HISTORICAL_SHARES.get(agency, 0.05)
        change_ratio = (share - base_share) / base_share if base_share > 0 else 0
        # Use model if it's reasonable; otherwise heuristic
        if model is not None and r2 > 0.1:
            projected = model.predict([[share]])[0]
            # Normalize projection too
            if projected > 1000:
                projected = min(100.0, projected / 100.0)
            elif projected > 100:
                projected = 100.0
        else:
            projected = base * (1 + 0.3 * change_ratio)  # 30% elasticity heuristic

        results.append({
            "agency": agency,
            "budget_share": share,
            "budget_dollars": share * TOTAL_BUDGET,
            "projected_performance": round(projected, 1),
        })

    return pd.DataFrame(results)

def sensitivity_analysis(agency, df_results):
    """Show impact of ±10% budget shift for one agency."""
    base_share = df_results[df_results["agency"] == agency]["budget_share"].iloc[0]
    base_perf = df_results[df_results["agency"] == agency]["projected_performance"].iloc[0]

    scenarios = []
    for pct in [-0.10, -0.05, 0, 0.05, 0.10]:
        new_share = base_share * (1 + pct)
        # Re-run heuristic
        change_ratio = (new_share - base_share) / base_share if base_share > 0 else 0
        new_perf = base_perf * (1 + 0.3 * change_ratio)
        scenarios.append({
            "shift_pct": f"{pct*100:+.0f}%",
            "new_share": round(new_share, 4),
            "projected_performance": round(new_perf, 1),
            "delta": round(new_perf - base_perf, 1),
        })
    return pd.DataFrame(scenarios)

def main():
    print("=" * 60)
    print("Scenario Engine — What-if Budget Modeling")
    print("=" * 60)

    # Default scenario: equal redistribution
    default_alloc = {a: 0.10 for a in AGENCIES}
    df = run_scenario(default_alloc)
    print("\n[Scenario] Default scenario (equal 10% each):")
    print(df.to_string(index=False))

    # Save
    out = DATA_DIR / "scenario_default.json"
    df.to_json(out, orient="records", indent=2)
    print(f"\n[Scenario] Saved to {out}")

    # Sensitivity for MPD
    sens = sensitivity_analysis("Metropolitan Police Department", df)
    print("\n[Scenario] Sensitivity: Metropolitan Police Department (±10% budget shift)")
    print(sens.to_string(index=False))

    sens_path = DATA_DIR / "scenario_sensitivity_mpd.json"
    sens.to_json(sens_path, orient="records", indent=2)
    print(f"[Scenario] Saved sensitivity to {sens_path}")

    # A second scenario: education boost
    edu_boost = HISTORICAL_SHARES.copy()
    edu_boost["DC Public Schools"] = 0.35
    # Normalize
    total = sum(edu_boost.values())
    edu_boost = {k: v / total for k, v in edu_boost.items()}
    df2 = run_scenario(edu_boost)
    print("\n[Scenario] Education-boost scenario (DCPS 35%):")
    print(df2.to_string(index=False))
    df2.to_json(DATA_DIR / "scenario_education_boost.json", orient="records", indent=2)

    print("\n[Scenario] Done.")

if __name__ == "__main__":
    main()
