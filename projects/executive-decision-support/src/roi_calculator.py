#!/usr/bin/env python3
"""
ROI Calculator — Program Investment Analysis for Municipal Planning

Calculates:
- Net Present Value (NPV) at 3% discount rate
- Payback period (years)
- Benefit-cost ratio
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).parent.parent
DATA_DIR = BASE / "data"
DATA_DIR.mkdir(exist_ok=True)

DISCOUNT_RATE = 0.03

def calculate_npv(costs, benefits, years=10, discount_rate=DISCOUNT_RATE):
    """
    Calculate NPV from arrays of annual costs and benefits.
    Returns NPV, total costs, total benefits, benefit_cost_ratio.
    """
    cash_flows = np.array(benefits) - np.array(costs)
    pv_flows = []
    for t, cf in enumerate(cash_flows):
        pv = cf / ((1 + discount_rate) ** t)
        pv_flows.append(pv)
    npv = sum(pv_flows)
    total_costs = sum(costs)
    total_benefits_pv = sum([benefits[t] / ((1 + discount_rate) ** t) for t in range(len(benefits))])
    bcr = total_benefits_pv / total_costs if total_costs > 0 else 0
    return {
        "npv": round(npv, 2),
        "total_costs": round(total_costs, 2),
        "total_benefits_pv": round(total_benefits_pv, 2),
        "benefit_cost_ratio": round(bcr, 2),
    }

def calculate_payback(costs, benefits):
    """Calculate simple payback period in years."""
    cumulative = 0
    for t, (c, b) in enumerate(zip(costs, benefits)):
        cumulative += (b - c)
        if cumulative >= 0:
            # Interpolate within year
            prev_cumulative = cumulative - (b - c)
            fraction = abs(prev_cumulative) / (b - c) if (b - c) > 0 else 0
            return t + fraction
    return None  # Never pays back

def evaluate_program(name, annual_cost, annual_benefit, years=10, ramp_up=2):
    """
    Evaluate a single program investment.
    ramp_up: number of years where benefits scale from 0 to full.
    """
    costs = [annual_cost] * years
    benefits = []
    for y in range(years):
        if y < ramp_up:
            benefits.append(annual_benefit * (y + 1) / ramp_up)
        else:
            benefits.append(annual_benefit)

    npv_result = calculate_npv(costs, benefits, years)
    payback = calculate_payback(costs, benefits)

    return {
        "program": name,
        "annual_cost": annual_cost,
        "annual_benefit": annual_benefit,
        "years": years,
        "npv": npv_result["npv"],
        "total_costs": npv_result["total_costs"],
        "total_benefits_pv": npv_result["total_benefits_pv"],
        "benefit_cost_ratio": npv_result["benefit_cost_ratio"],
        "payback_period_years": round(payback, 1) if payback else None,
    }

def main():
    print("=" * 60)
    print("ROI Calculator — Municipal Program Investment Analysis")
    print("=" * 60)

    programs = [
        # (name, annual_cost, annual_benefit, ramp_up_years)
        ("Digital Services Modernization", 5_000_000, 12_000_000, 2),
        ("Youth Job Training Expansion", 3_500_000, 8_000_000, 3),
        ("Green Infrastructure Retrofit", 8_000_000, 15_000_000, 4),
        ("Public Transit Reliability Upgrade", 12_000_000, 20_000_000, 3),
        ("Community Health Screening Program", 2_000_000, 5_500_000, 2),
    ]

    results = []
    for name, cost, benefit, ramp in programs:
        r = evaluate_program(name, cost, benefit, years=10, ramp_up=ramp)
        results.append(r)
        print(f"\n[ROI] {name}")
        print(f"  Annual cost: ${cost:,.0f}")
        print(f"  Annual benefit: ${benefit:,.0f}")
        print(f"  NPV (3%): ${r['npv']:,.0f}")
        print(f"  Benefit-cost ratio: {r['benefit_cost_ratio']:.2f}")
        print(f"  Payback: {r['payback_period_years']} years")

    df = pd.DataFrame(results)
    out_json = DATA_DIR / "roi_analysis.json"
    out_csv = DATA_DIR / "roi_analysis.csv"
    df.to_json(out_json, orient="records", indent=2)
    df.to_csv(out_csv, index=False)
    print(f"\n[ROI] Saved to {out_json}")
    print(f"[ROI] Saved CSV to {out_csv}")

    print("\n[ROI] Done.")

if __name__ == "__main__":
    main()
