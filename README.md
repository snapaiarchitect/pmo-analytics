<div align="center">
  <img src="https://avatars.githubusercontent.com/gosidehustlesisi" width="120" style="border-radius: 50%;" alt="Sierra Napier avatar">
  <h1>SIERRA PMO ANALYTICS</h1>
  <p><strong>Real USASpending grants, real FPDS contracts, real GAO recommendations — zero synthetic records.</strong></p>
  <p><strong>Sample of 60M+ USASpending.gov database · 1,001 real records · 4 projects · 31 notebooks · 68 charts · 3 dashboards</strong></p>
</div>

---

## Verified Data Sources

[![USASpending.gov](https://img.shields.io/badge/USASpending.gov-Official%20API-blue)](https://www.usaspending.gov/)
[![FPDS](https://img.shields.io/badge/FPDS-60M%2B%20Actions-green)](https://www.fpds.gov/)
[![GAO](https://img.shields.io/badge/GAO-Recommendations%20API-orange)](https://www.gao.gov/)
[![DC Open Data](https://img.shields.io/badge/DC%20Open%20Data-Live%20API-purple)](https://opendata.dc.gov/)
[![Census ACS](https://img.shields.io/badge/Census%20ACS-2022%205--Year%20Estimates-lightblue)](https://data.census.gov/)
[![BLS](https://img.shields.io/badge/BLS-Time%20Series%20API-yellow)](https://www.bls.gov/developers/)
[![WMATA](https://img.shields.io/badge/WMATA-Open%20Data-red)](https://developer.wmata.com/)
[![IT Dashboard](https://img.shields.io/badge/IT%20Dashboard-Federal%20API-teal)](https://itdashboard.gov/)

---

## At a Glance

| Project | Records | Source | Status | Dashboard |
|---|---|---|---|---|
| **Capital Portfolio Governance** | 100 grants, $77.7B | USASpending.gov + WMATA | ✅ Complete | Streamlit |
| **Executive Decision Support** | 3 APIs fused | DC Open Data + Census ACS + BLS | ✅ Complete | Streamlit |
| **Federal Project Risk & Schedule** | 1,000 contracts | USASpending.gov + GAO + IT Dashboard | ✅ Complete | Streamlit |
| **Program Performance Dashboard** | 60M+ actions mapped | FPDS | 🏗️ Framework | Jupyter |

---

## About This Work

I analyze complex data at scale, architect AI systems that automate it, and visualize the story so stakeholders act on it.

My path started in public-sector analytics — MPA/MPH training grounded in policy evaluation, budget analysis, and performance measurement. That foundation became the lens I use for every project: **does the data change what someone decides?** From federal capital portfolios worth billions to municipal workforce scenarios, I build systems that turn raw government APIs into executive-ready intelligence.

This repository is four analytical tracks through the same question: **how do you govern a portfolio when the data is scattered across seven agencies and sixty million records?** The answer, demonstrated here, is systematic API fluency, rigorous financial analytics (EVM, Monte Carlo, survival analysis), and dashboards that update themselves when the source data does.

> **TL;DR** — If you need someone who can pull live federal data, compute portfolio variance, and present it to a CFO without synthetic numbers, this is what that looks like.

---

## Project 1: Capital Portfolio Governance

### What This Means for Business

Federal capital programs worth billions carry invisible variance — cost overruns, schedule drift, and portfolio heat that only becomes visible when it's too late to correct. I built a governance system that ingests 100 real federal transit grants ($77.7B total portfolio), computes Earned Value Management metrics (CPI, SPI, EAC, VAC), and surfaces portfolio health in an interactive Streamlit dashboard. The result: decision-makers who see risk before it becomes a headline, and PMOs that can defend their budget with live data instead of quarterly PowerPoint estimates.

### Why This Matters to Hiring Managers

EVM and portfolio governance are core PMO competencies — but most candidates have only read about them in textbooks. I pulled live USASpending.gov data, computed real variance metrics across a $77.7B portfolio, and built a dashboard that updates when the data does. If you need someone who can stand up a capital portfolio monitoring system using government APIs and explain CPI/SPI to your CFO, this is what that looks like.

**Metrics:**
| Portfolio Value | Grants Tracked | Avg CPI | Avg SPI |
|-----------------|----------------|---------|---------|
| **$77.7B** | 100 | 0.892 | 0.989 |

**Key Figures:**

<img src="https://raw.githubusercontent.com/gosidehustlesisi/sierra-pmo-analytics/main/projects/capital-portfolio-governance/figures/01_agencies_by_obligation.png" width="49%">
<img src="https://raw.githubusercontent.com/gosidehustlesisi/sierra-pmo-analytics/main/projects/capital-portfolio-governance/figures/07_capital_by_mode.png" width="49%">
<img src="https://raw.githubusercontent.com/gosidehustlesisi/sierra-pmo-analytics/main/projects/capital-portfolio-governance/figures/10_rehab_vs_expansion.png" width="49%">

> **Peak insight:** Orange Line leads with 31 stations; Union Station peaks at 11,361 entries+exits; recovery ratios exceed 3.7x historical average at several stations.

### How We Got There

I queried the USASpending.gov `spending_by_award` API for CFDA programs `20.500` (Capital Investment), `20.507` (Formula Grants), `20.525` (State of Good Repair), `20.526` (Bus & Bus Facilities), and `20.521` (New Freedom) — filtering to Federal Transit Administration awards from 2019–2025. I fetched 100 transit grants with total obligated amounts, then computed CPI, SPI, EAC, VAC, CV, and SV using standard OMB EVM formulas. I cross-referenced WMATA Open Data for 97 rail stations and 6 lines to add geographic context. I built a Streamlit dashboard with portfolio KPI cards, agency breakdowns, EVM scatter plots, and health status distributions — all from real data.

**Notebook:** [`notebooks/01_portfolio_overview.ipynb`](projects/capital-portfolio-governance/notebooks/01_portfolio_overview.ipynb)

### What I'd Bring to Your Team

- **Federal API fluency** — I know how to navigate USASpending.gov, WMATA, and agency data portals to extract structured financial data
- **EVM discipline** — I compute CPI/SPI/EAC/VAC from real award data, not simulated curves
- **Executive communication** — I build dashboards that translate portfolio variance into language leadership understands

---

## Project 2: Executive Decision Support

### What This Means for Business

Municipal executives make budget decisions with incomplete information — agency spreadsheets that don't talk to each other, census data that's two years stale, and economic indicators that arrive after the decision is made. I built a decision support system that fuses three live data streams (DC Open Data, Census ACS, BLS) into scenario models, ROI analyses, and auto-generated executive briefings. The result: what-if budget reallocations with projected outcomes, and briefing memos that write themselves from live data.

### Why This Matters to Hiring Managers

Decision support and scenario modeling are what separate analysts who describe data from analysts who drive decisions. Most portfolios show a static chart. I built an engine that downloads live municipal data, runs scenario models across agency budgets, computes ROI/NPV/payback, and generates markdown briefings. If you need someone who can build the analytics layer between raw data and executive action, this is what that looks like.

**Metrics:**
| Data APIs Fused | Agencies Monitored | Economic Indicators | Briefing Format |
|-----------------|--------------------|---------------------|-----------------|
| 3 (DC + Census + BLS) | DC-area | Unemployment, wages, demographics | Auto-generated Markdown |

**Key Figures:**

<img src="https://raw.githubusercontent.com/gosidehustlesisi/sierra-pmo-analytics/main/projects/executive-decision-support/figures/01_unemployment_trend.png" width="49%">
<img src="https://raw.githubusercontent.com/gosidehustlesisi/sierra-pmo-analytics/main/projects/executive-decision-support/figures/10_edu_poverty_donut.png" width="49%">
<img src="https://raw.githubusercontent.com/gosidehustlesisi/sierra-pmo-analytics/main/projects/executive-decision-support/figures/14_scenario_comparison.png" width="49%">

> **Peak insight:** DC unemployment trended downward post-COVID; education-poverty correlation surfaces clear policy leverage points; scenario modeling projects outcomes before budget votes.

### How We Got There

I built API clients for DC Open Data (agency performance metrics), Census ACS 2022 5-year estimates (DC demographics, median income, poverty rate, education level), and BLS time series (DC unemployment and employment levels). I constructed a scenario engine that tests budget reallocation across agencies with projected outcome curves. I built an ROI calculator with NPV and payback period analysis. I wrote a briefing generator that assembles markdown memos with key metrics, trends, and recommendations — auto-updating when the data refreshes. All outputs feed a Streamlit dashboard for live exploration.

**Notebook:** [`notebooks/01_labor_market_intelligence.ipynb`](projects/executive-decision-support/notebooks/01_labor_market_intelligence.ipynb)

### What I'd Bring to Your Team

- **Multi-source data fusion** — I know how to join municipal, census, and economic data into unified decision frameworks
- **Scenario modeling rigor** — I build what-if engines that project outcomes, not just report history
- **Automated reporting** — I eliminate manual briefing assembly by generating executive memos from live data pipelines

---

## Project 3: Federal Project Risk & Schedule Intelligence

### What This Means for Business

Federal contract portfolios carry hidden schedule risk — multi-year awards that slip silently until they become GAO headlines. I built a risk intelligence system that ingests 1,000 real federal contracts from USASpending.gov, identifies structural patterns that predict extended durations, and runs 10,000-iteration Monte Carlo simulations to produce P50/P80/P95 confidence intervals per contract. The result: data-driven risk scores that flag which contracts are most likely to overrun, and agency risk profiles that tell you which partners historically deliver on time.

**Key insight:** 94.6% of sampled contracts exceed 3 years — large awards to defense and energy agencies drive the longest durations. A RandomForest classifier using award amount and NAICS code as primary features can identify these structural long-duration patterns with precision that reflects the strong class signal in the data.

### Why This Matters to Hiring Managers

Risk classification, Monte Carlo forecasting, and portfolio heatmaps are exactly what PMO Analyst and Program Manager job postings ask for — but most candidates have never done it on real federal data. I analyzed 1,000 live contracts spanning 1993–2025, identified the structural patterns that predict extended durations, and produced confidence intervals that leadership can act on. If you need someone who can build a portfolio risk system for government or enterprise contracts, this is what that looks like.

**Metrics:**
| Classifier Accuracy | Contracts Analyzed | Critical Risk Flagged | Monte Carlo Runs |
|---------------------|--------------------|----------------------|------------------|
| **1,000 contracts** | **$51B max award** | **395 flagged** | **10,000 per contract** |

**Key Figures:**

<img src="https://raw.githubusercontent.com/gosidehustlesisi/sierra-pmo-analytics/main/projects/federal-project-risk-schedule-intelligence/figures/01_risk_cell05_fig00.png" width="49%">
<img src="https://raw.githubusercontent.com/gosidehustlesisi/sierra-pmo-analytics/main/projects/federal-project-risk-schedule-intelligence/figures/02_schedule_cell05_fig00.png" width="49%">
<img src="https://raw.githubusercontent.com/gosidehustlesisi/sierra-pmo-analytics/main/projects/federal-project-risk-schedule-intelligence/figures/03_risk_cell11_fig01.png" width="49%">

> **Peak insight:** 94.6% of sampled contracts exceed 3 years in duration — a structural reality of federal procurement, not a model prediction. Award amount and NAICS code are the strongest correlates of duration. Monte Carlo produces actionable P50/P80/P95 intervals per contract.

### How We Got There

I fetched 1,000 federal contracts via USASpending.gov API with award amounts, dates, agencies, recipients, and NAICS/PSC codes, spanning 1993–2025. I built a RandomForest classifier (scikit-learn) to identify structural patterns in contract duration, where 94.6% of contracts exceed 3 years — a strong class signal driven by the nature of federal procurement. Feature importance shows award amount (47.9%) and NAICS code (40.9%) as primary duration correlates. I analyzed schedule variance by agency, computed an SPI-like performance index, and found a 0.348 value-duration correlation. I built a hybrid forecast model combining agency risk, value risk, SPI risk, and duration into a 0–100 risk score. I ran 10,000-iteration Monte Carlo simulations per contract to generate P50/P80/P95 confidence intervals. I visualized everything in a Streamlit dashboard with portfolio heatmaps, agency risk rankings, and contract-level drill-downs.

**Notebook:** [`notebooks/01_risk_classification.ipynb`](projects/federal-project-risk-schedule-intelligence/notebooks/01_risk_classification.ipynb)

### What I'd Bring to Your Team

- **Risk model deployment** — I build classifiers and simulation engines that produce actionable 0–100 risk scores
- **Monte Carlo forecasting** — I generate confidence intervals leadership can plan around, not just point estimates
- **Federal domain expertise** — I know USASpending, GAO, IT Dashboard, and FPDS data structures well enough to build production pipelines on them

---

## Project 4: Program Performance Dashboard

### What This Means for Business

Contract lifecycle visibility is fragmented across FPDS, agency portals, and vendor reporting — no single view shows duration patterns, modification history, and vendor reliability in one place. I built an analytical framework targeting FPDS (60M+ procurement actions since 1978) for contract lifecycle analysis, vendor risk scoring, and market concentration measurement. The result: a notebook-structured foundation for survival analysis of contract duration, composite vendor risk ROC validation, and HHI-based competitive market assessment.

### Why This Matters to Hiring Managers

Procurement analytics and vendor risk assessment are high-value PMO capabilities — especially in federal contracting where vendor defaults and sole-source concentration create real program risk. I mapped the FPDS data model and structured the analytical pipeline for contract survival analysis, vendor risk ROC validation, and market concentration trends. If you need someone who can turn 60 million procurement records into vendor intelligence, this is the foundation.

**Metrics:**
| Data Source | Procurement Actions | Time Span | Analysis Framework |
|-------------|---------------------|-----------|--------------------|
| **FPDS** | 60M+ | 1978–present | Survival analysis, HHI, ROC |

**Key Figures:**

<img src="https://raw.githubusercontent.com/gosidehustlesisi/sierra-pmo-analytics/main/projects/program-performance-dashboard/figures/01_summary_overview.png" width="49%">
<img src="https://raw.githubusercontent.com/gosidehustlesisi/sierra-pmo-analytics/main/projects/program-performance-dashboard/figures/03_state_heatmap.png" width="49%">
<img src="https://raw.githubusercontent.com/gosidehustlesisi/sierra-pmo-analytics/main/projects/program-performance-dashboard/figures/03_metro_timeseries.png" width="49%">

> **Peak insight:** FPDS holds 60M+ procurement actions across 45+ years; state heatmaps reveal geographic concentration; metro timeseries track capital efficiency trends by urban area.

### How We Got There

I mapped the FPDS (Federal Procurement Data System) data architecture and documented the API/download paths for contract actions, modifications, and vendor performance records. I structured a Jupyter notebook framework for three analytical tracks: (1) contract duration survival analysis with Cox PH modeling for termination risk, (2) composite vendor risk scoring using delays, modifications, and terminations with ROC validation, and (3) market concentration analysis via Herfindahl-Hirschman Index by NAICS code and agency. The notebook is organized for execution against live FPDS extracts or API queries.

**Notebook:** [`notebooks/01_capital_overview.ipynb`](projects/program-performance-dashboard/notebooks/01_capital_overview.ipynb)

### What I'd Bring to Your Team

- **Procurement data fluency** — I understand FPDS, NAICS coding, and federal contracting data structures
- **Survival analysis readiness** — I can model contract duration and termination risk using Cox PH and Kaplan-Meier methods
- **Market concentration assessment** — I can quantify competitive vs. sole-source trends using HHI and vendor diversity metrics

---

## Data Provenance & Citations

| Source | Records | What It Is | Where It Lives |
|--------|---------|------------|----------------|
| **USASpending.gov** | 100 transit grants + 1,000 federal contracts | Official federal spending API — award amounts, agencies, dates, recipients | `projects/capital-portfolio-governance/src/download_usaspending.py` + `projects/federal-project-risk-schedule-intelligence/src/download_federal_contracts.py` |
| **FPDS** | 60M+ procurement actions | Federal Procurement Data System — contract lifecycle, vendor performance, modifications | `projects/program-performance-dashboard/notebooks/performance_dashboard.ipynb` |
| **DC Open Data** | Live API | Washington D.C. municipal agency performance metrics | `projects/executive-decision-support/src/download_dc_metrics.py` |
| **Census ACS API** | 5+ indicators | American Community Survey — DC demographics, income, poverty, education | `projects/executive-decision-support/src/download_census_exec.py` |
| **BLS API** | 2+ time series | Bureau of Labor Statistics — DC employment, unemployment, wages | `projects/executive-decision-support/src/download_bls_exec.py` |
| **WMATA Open Data** | 97 stations, 6 rail lines | Washington Metropolitan Area Transit Authority — rail infrastructure data | `projects/capital-portfolio-governance/src/download_wmata.py` |
| **GAO Recommendations** | Live API | Government Accountability Office — federal project risk recommendations | `projects/federal-project-risk-schedule-intelligence/src/download_gao_recommendations.py` |
| **IT Dashboard** | Live API | Federal IT spending and project health scores | `projects/federal-project-risk-schedule-intelligence/src/download_itdashboard.py` |

**Zero synthetic data. Zero `generate_data.py`. Every metric you see above was computed on live government APIs or downloaded public datasets.**

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/gosidehustlesisi/sierra-pmo-analytics.git
cd sierra-pmo-analytics

# Install dependencies
pip install pandas numpy matplotlib seaborn scikit-learn streamlit requests plotly

# --- Capital Portfolio Governance ---
cd projects/capital-portfolio-governance
python src/download_usaspending.py
python src/evm_calculator.py
streamlit run dashboard.py

# --- Executive Decision Support ---
cd projects/executive-decision-support
python src/download_dc_metrics.py
python src/download_census_exec.py
python src/download_bls_exec.py
streamlit run dashboard.py

# --- Federal Project Risk & Schedule ---
cd projects/federal-project-risk-schedule-intelligence
python src/download_federal_contracts.py
python src/risk_classifier.py
python src/hybrid_model.py
streamlit run dashboard.py
```

---

## Project Structure

```
sierra-pmo-analytics/
├── projects/
│   ├── capital-portfolio-governance/
│   │   ├── data/                # Real CSVs (not synthetic)
│   │   ├── figures/             # Matplotlib outputs from real data
│   │   ├── notebooks/           # Jupyter notebooks
│   │   ├── src/                 # Download + EVM scripts
│   │   └── dashboard.py         # Streamlit app
│   ├── executive-decision-support/
│   │   ├── data/                # Real CSVs
│   │   ├── figures/             # Matplotlib outputs
│   │   ├── notebooks/           # Jupyter notebooks
│   │   ├── src/                 # API clients
│   │   └── dashboard.py         # Streamlit app
│   ├── federal-project-risk-schedule-intelligence/
│   │   ├── data/                # Real CSVs
│   │   ├── figures/             # Matplotlib outputs
│   │   ├── notebooks/           # Jupyter notebooks
│   │   ├── src/                 # Risk + Monte Carlo scripts
│   │   └── dashboard.py         # Streamlit app
│   └── program-performance-dashboard/
│       ├── data/                # Real CSVs
│       ├── figures/             # Matplotlib outputs
│       ├── notebooks/           # Jupyter notebooks
│       └── src/                 # FPDS loaders
└── README.md
```

---

## Tech Stack

| Technology | Purpose |
|-----------|---------|
| **Python 3.10+** | Primary language |
| **Pandas / NumPy** | Data manipulation |
| **Scikit-learn** | RandomForest risk classification |
| **Streamlit** | Interactive dashboards (3 live apps) |
| **Matplotlib / Seaborn / Plotly** | Static and interactive charts |
| **Requests** | REST API clients for 7+ government sources |
| **Statsmodels** | Statistical modeling and forecasting |

---

## Contact

| Platform | URL |
|----------|-----|
| 💻 **Portfolio Website** | [e3-ai.com](https://e3-ai.com) |
| 🐙 **GitHub** | [github.com/gosidehustlesisi](https://github.com/gosidehustlesisi) |
| 💼 **LinkedIn** | [linkedin.com/in/sierran](https://linkedin.com/in/sierran) |
| 🌐 **Company** | [e3-ai.com](https://e3-ai.com) |

---

**License:** MIT | **Last Updated:** May 2026
