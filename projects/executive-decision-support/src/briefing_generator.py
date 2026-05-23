#!/usr/bin/env python3
"""
Briefing Generator — Auto-Generate Executive Briefing Memos

Produces a Markdown executive memo with:
- Executive Summary
- Key Metrics (from downloaded data)
- Trends
- Recommendations
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent.parent
DATA_DIR = BASE / "data"
DATA_DIR.mkdir(exist_ok=True)

def load_data_sources():
    """Load all downloaded data sources."""
    sources = {}

    # Census DC
    census_path = DATA_DIR / "census_dc.json"
    if census_path.exists():
        with open(census_path) as f:
            sources["census"] = pd.DataFrame(json.load(f))
    else:
        sources["census"] = pd.DataFrame()

    # BLS DC
    bls_path = DATA_DIR / "bls_dc.json"
    if bls_path.exists():
        with open(bls_path) as f:
            sources["bls"] = pd.DataFrame(json.load(f))
    else:
        sources["bls"] = pd.DataFrame()

    # DC Metrics
    dc_path = DATA_DIR / "dc_agency_metrics.json"
    if dc_path.exists():
        with open(dc_path) as f:
            sources["dc"] = pd.DataFrame(json.load(f))
    else:
        sources["dc"] = pd.DataFrame()

    # ROI
    roi_path = DATA_DIR / "roi_analysis.json"
    if roi_path.exists():
        with open(roi_path) as f:
            sources["roi"] = pd.DataFrame(json.load(f))
    else:
        sources["roi"] = pd.DataFrame()

    # Scenarios
    scen_path = DATA_DIR / "scenario_default.json"
    if scen_path.exists():
        with open(scen_path) as f:
            sources["scenario"] = pd.DataFrame(json.load(f))
    else:
        sources["scenario"] = pd.DataFrame()

    return sources

def _df_to_md(df):
    """Convert DataFrame to markdown table without tabulate dependency."""
    if df.empty:
        return ""
    cols = list(df.columns)
    header = "| " + " | ".join(str(c) for c in cols) + " |"
    sep = "|" + "|".join([" --- " for _ in cols]) + "|"
    rows = []
    for _, row in df.iterrows():
        rows.append("| " + " | ".join(str(v) for v in row.values) + " |")
    return "\n".join([header, sep] + rows)


def generate_briefing(sources):
    """Generate the executive briefing markdown."""
    today = datetime.now().strftime("%Y-%m-%d")

    # Extract key metrics
    census = sources["census"]
    bls = sources["bls"]
    dc = sources["dc"]
    roi = sources["roi"]
    scenario = sources["scenario"]

    # DC population
    population = None
    if not census.empty and "population" in census.columns:
        population = int(census["population"].iloc[0])
    elif not census.empty and "population_millions" in census.columns:
        population = int(census["population_millions"].iloc[0] * 1_000_000)

    # Median income
    median_income = None
    if not census.empty and "median_income" in census.columns:
        median_income = int(census["median_income"].iloc[0])

    # Poverty rate
    poverty_rate = None
    if not census.empty and "poverty_rate" in census.columns:
        poverty_rate = float(census["poverty_rate"].iloc[0])

    # Unemployment rate
    unemployment = None
    if not bls.empty and "metric" in bls.columns:
        ur = bls[bls["metric"] == "dc_unemployment_rate"]
        if not ur.empty:
            unemployment = float(ur.sort_values("year").iloc[-1]["value"])

    # Employment level
    employment = None
    if not bls.empty and "metric" in bls.columns:
        emp = bls[bls["metric"] == "dc_employment_level"]
        if not emp.empty:
            employment = int(emp.sort_values("year").iloc[-1]["value"])

    # Agency count
    agency_count = len(dc["agency_name"].unique()) if not dc.empty and "agency_name" in dc.columns else 0

    # Best ROI program
    best_roi = None
    if not roi.empty and "benefit_cost_ratio" in roi.columns:
        best = roi.loc[roi["benefit_cost_ratio"].idxmax()]
        best_roi = (best["program"], best["benefit_cost_ratio"], best["npv"])

    lines = []
    lines.append(f"# Executive Briefing — DC Strategic Planning")
    lines.append(f"**Date:** {today}")
    lines.append(f"**Classification:** Internal — Executive Decision Support")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Executive Summary
    lines.append("## Executive Summary")
    lines.append("")
    lines.append("This briefing synthesizes real-time demographic, economic, and agency performance")
    lines.append("data to inform FY2025 budget allocation and program investment decisions.")
    lines.append("")
    if population:
        lines.append(f"- **DC Population:** {population:,}")
    if median_income:
        lines.append(f"- **Median Household Income:** ${median_income:,}")
    if unemployment is not None:
        lines.append(f"- **Unemployment Rate:** {unemployment:.1f}%")
    if employment:
        lines.append(f"- **Total Nonfarm Employment:** {employment:,}")
    if poverty_rate is not None:
        lines.append(f"- **Poverty Rate:** {poverty_rate:.1f}%")
    if agency_count:
        lines.append(f"- **Agencies Monitored:** {agency_count}")
    if best_roi:
        lines.append(f"- **Top ROI Program:** {best_roi[0]} (BCR: {best_roi[1]:.2f}, NPV: ${best_roi[2]:,.0f})")
    lines.append("")

    # Key Metrics
    lines.append("## Key Metrics")
    lines.append("")
    lines.append("### Demographics (Census ACS 5-Year)")
    if not census.empty:
        lines.append(_df_to_md(census))
    else:
        lines.append("*Census data not available.*")
    lines.append("")

    lines.append("### Employment & Wages (BLS)")
    if not bls.empty:
        latest = bls.sort_values(["year", "period"]).groupby("metric").last().reset_index()
        lines.append(_df_to_md(latest[["metric", "year", "period", "value", "description"]]))
    else:
        lines.append("*BLS data not available.*")
    lines.append("")

    lines.append("### Agency Performance (DC Open Data)")
    if not dc.empty:
        lines.append(_df_to_md(dc.head(10)))
    else:
        lines.append("*DC agency metrics not available.*")
    lines.append("")

    # Trends
    lines.append("## Trends")
    lines.append("")
    if not bls.empty and "metric" in bls.columns:
        ur = bls[bls["metric"] == "dc_unemployment_rate"]
        if not ur.empty and len(ur) > 1:
            ur_sorted = ur.sort_values(["year", "period"])
            first = float(ur_sorted.iloc[0]["value"])
            last = float(ur_sorted.iloc[-1]["value"])
            delta = last - first
            direction = "increased" if delta > 0 else "decreased"
            lines.append(f"- **DC Unemployment** has {direction} from {first:.1f}% to {last:.1f}%")
            lines.append(f"  over the observed period ({ur_sorted.iloc[0]['year']}–{ur_sorted.iloc[-1]['year']}).")
        else:
            lines.append("- **DC Unemployment:** Insufficient time-series for trend analysis.")
    if not census.empty and "pct_bachelors_plus" in census.columns:
        edu = float(census["pct_bachelors_plus"].iloc[0])
        lines.append(f"- **Education:** {edu:.1f}% of DC adults hold a bachelor's degree or higher.")
    lines.append("")

    # Recommendations
    lines.append("## Recommendations")
    lines.append("")
    if best_roi:
        lines.append(f"1. **Prioritize {best_roi[0]}** — highest benefit-cost ratio ({best_roi[1]:.2f})")
        lines.append(f"   with estimated NPV of ${best_roi[2]:,.0f} over 10 years.")
    if not roi.empty and "npv" in roi.columns:
        positive_npv = roi[roi["npv"] > 0]
        if not positive_npv.empty:
            lines.append(f"2. **Fund all positive-NPV programs** — {len(positive_npv)} of {len(roi)} evaluated")
            lines.append(f"   programs show positive returns at 3% discount rate.")
    lines.append("3. **Monitor unemployment trend** — any sustained increase above 5.5% should")
    lines.append("   trigger workforce retraining program acceleration.")
    lines.append("4. **Leverage Open Data** — expand agency performance metric coverage beyond")
    lines.append("   the current baseline to enable richer scenario modeling.")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*Data sources: DC Open Data Portal, US Census Bureau ACS 5-Year Estimates,")
    lines.append("Bureau of Labor Statistics. Generated automatically by executive-decision-support.*")

    return "\n".join(lines)

def main():
    print("=" * 60)
    print("Briefing Generator — Executive Memo")
    print("=" * 60)

    sources = load_data_sources()
    briefing = generate_briefing(sources)

    today = datetime.now().strftime("%Y%m%d")
    out_path = DATA_DIR / f"briefing_{today}.md"
    with open(out_path, "w") as f:
        f.write(briefing)

    print(f"\n[Briefing] Generated {len(briefing)} characters")
    print(f"[Briefing] Saved to {out_path}")
    print("\n[Briefing] Preview (first 800 chars):")
    print(briefing[:800])
    print("...")

    print("\n[Briefing] Done.")

if __name__ == "__main__":
    main()
