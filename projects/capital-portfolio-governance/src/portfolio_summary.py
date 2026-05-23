"""
Portfolio Summary — Aggregate Metrics for Capital Portfolio Governance
Produces top-level KPIs from all data sources.
"""

import json
from pathlib import Path
from collections import Counter

DATA_DIR = Path(__file__).parent.parent / "data"


def load_json(filepath: Path) -> list[dict]:
    """Load JSON data file."""
    if not filepath.exists():
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def portfolio_summary() -> dict:
    """
    Compute comprehensive portfolio summary from all data sources.
    """
    # Load USASpending grants
    grants = load_json(DATA_DIR / "usaspending_transit_grants.json")
    
    # Load EVM results
    evm = load_json(DATA_DIR / "evm_results.json")
    
    # Load variance report
    variances = load_json(DATA_DIR / "variance_report.json")
    
    summary = {
        "usaspending": {},
        "evm": {},
        "variance": {},
        "overall": {},
    }
    
    # USASpending summary
    if grants:
        amounts = [float(g.get("Award Amount", 0)) for g in grants if g.get("Award Amount")]
        agencies = Counter(g.get("Awarding Sub Agency", "Unknown") for g in grants)
        cfdas = Counter(g.get("CFDA Number", "Unknown") for g in grants)
        
        summary["usaspending"] = {
            "total_grants": len(grants),
            "total_portfolio_value": round(sum(amounts), 2),
            "avg_grant_value": round(sum(amounts) / len(amounts), 2) if amounts else 0,
            "top_agency": agencies.most_common(1)[0] if agencies else ("None", 0),
            "agency_breakdown": dict(agencies.most_common(5)),
            "cfda_breakdown": dict(cfdas.most_common(5)),
        }
    
    # EVM summary
    if evm:
        cpis = [e["CPI"] for e in evm if e.get("CPI") is not None]
        spis = [e["SPI"] for e in evm if e.get("SPI") is not None]
        eacs = [e["EAC"] for e in evm if e.get("EAC") is not None]
        
        summary["evm"] = {
            "projects_analyzed": len(evm),
            "avg_cpi": round(sum(cpis) / len(cpis), 3) if cpis else 0,
            "avg_spi": round(sum(spis) / len(spis), 3) if spis else 0,
            "total_eac": round(sum(eacs), 2) if eacs else 0,
            "on_budget": sum(1 for c in cpis if c >= 0.95),
            "over_budget": sum(1 for c in cpis if c < 0.95),
        }
    
    # Variance summary
    if variances:
        healthy = sum(1 for v in variances if v.get("status") == "Healthy")
        watch = sum(1 for v in variances if v.get("status") == "Watch")
        at_risk = sum(1 for v in variances if v.get("status") == "At Risk")
        
        summary["variance"] = {
            "total_projects": len(variances),
            "healthy": healthy,
            "watch": watch,
            "at_risk": at_risk,
            "health_pct": round(healthy / len(variances) * 100, 1) if variances else 0,
        }
    
    # Overall
    summary["overall"] = {
        "data_sources": [
            "USASpending.gov (federal transit grants)",
            "FTA NTD (transit database — manual/CSV)",
            "WMATA Open Data (station/line inventory)",
        ],
        "last_updated": str(__import__("datetime").datetime.now().isoformat()),
        "coverage": "Federal Transit Administration (FTA) grants, 2019–2025",
    }
    
    return summary


def print_summary(summary: dict):
    """Pretty-print portfolio summary."""
    print("=" * 60)
    print("CAPITAL PORTFOLIO GOVERNANCE — EXECUTIVE SUMMARY")
    print("=" * 60)
    
    us = summary.get("usaspending", {})
    if us:
        print(f"\n📊 USASpending.gov Grants")
        print(f"   Total Grants:        {us.get('total_grants', 0)}")
        print(f"   Portfolio Value:       ${us.get('total_portfolio_value', 0):,.2f}")
        print(f"   Avg Grant:            ${us.get('avg_grant_value', 0):,.2f}")
        if us.get("top_agency"):
            print(f"   Top Agency:           {us['top_agency'][0]} ({us['top_agency'][1]} grants)")
    
    ev = summary.get("evm", {})
    if ev:
        print(f"\n📈 EVM Metrics")
        print(f"   Projects Analyzed:    {ev.get('projects_analyzed', 0)}")
        print(f"   Avg CPI:              {ev.get('avg_cpi', 0)}")
        print(f"   Avg SPI:              {ev.get('avg_spi', 0)}")
        print(f"   On Budget:            {ev.get('on_budget', 0)}")
        print(f"   Over Budget:          {ev.get('over_budget', 0)}")
    
    va = summary.get("variance", {})
    if va:
        print(f"\n⚠️  Variance Health")
        print(f"   Healthy:              {va.get('healthy', 0)} ({va.get('health_pct', 0)}%)")
        print(f"   Watch:                {va.get('watch', 0)}")
        print(f"   At Risk:              {va.get('at_risk', 0)}")
    
    ov = summary.get("overall", {})
    if ov:
        print(f"\n📋 Overview")
        print(f"   Coverage:             {ov.get('coverage', 'N/A')}")
        print(f"   Sources:              {', '.join(ov.get('data_sources', []))}")
        print(f"   Last Updated:         {ov.get('last_updated', 'N/A')}")


def save_summary(summary: dict, filepath: Path | None = None) -> Path:
    """Save summary to JSON."""
    if filepath is None:
        filepath = DATA_DIR / "portfolio_summary.json"
    
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n[Summary] Saved to {filepath}")
    return filepath


if __name__ == "__main__":
    summary = portfolio_summary()
    print_summary(summary)
    save_summary(summary)
