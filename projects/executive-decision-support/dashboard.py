import streamlit as st
import pandas as pd
import json
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

BASE = Path(__file__).parent
DATA_DIR = BASE / "data"

st.set_page_config(page_title="DC Executive Decision Support", layout="wide")

st.title("🏛️ DC Executive Decision Support Dashboard")
st.caption("Real-time municipal strategic planning with live Census, BLS, and DC Open Data.")

# ---- Load Data ----
@st.cache_data(ttl=3600)
def load_all_data():
    data = {}
    for fname in ["census_dc", "bls_dc", "dc_agency_metrics", "roi_analysis", "scenario_default",
                  "scenario_baseline", "scenario_optimistic", "scenario_pessimistic"]:
        path = DATA_DIR / f"{fname}.json"
        if path.exists():
            with open(path) as f:
                data[fname] = pd.DataFrame(json.load(f))
        else:
            data[fname] = pd.DataFrame()
    # Load BLS wide CSV for time series
    wide_path = DATA_DIR / "bls_dc_wide.csv"
    if wide_path.exists():
        data["bls_wide"] = pd.read_csv(wide_path)
        data["bls_wide"]["date"] = pd.to_datetime(
            data["bls_wide"]["year"].astype(str) + "-" + data["bls_wide"]["period"].str.replace("M", "") + "-01"
        )
    else:
        data["bls_wide"] = pd.DataFrame()
    return data

data = load_all_data()

# ---- Tabs ----
tab1, tab2, tab3, tab4 = st.tabs(["📊 Executive Overview", "💼 Labor Market", "🏙️ Demographics", "🔮 Scenarios"])

# ===================== TAB 1: EXECUTIVE OVERVIEW =====================
with tab1:
    st.header("Executive KPI Overview")

    cols = st.columns(4)

    # Population
    if not data["census_dc"].empty and "population" in data["census_dc"].columns:
        pop = int(data["census_dc"]["population"].iloc[0])
        cols[0].metric("DC Population", f"{pop:,}")
    else:
        cols[0].metric("DC Population", "N/A")

    # Unemployment
    if not data["bls_wide"].empty and "dc_unemployment_rate" in data["bls_wide"].columns:
        latest_ur = float(data["bls_wide"].sort_values("date").iloc[-1]["dc_unemployment_rate"])
        prev_ur = float(data["bls_wide"].sort_values("date").iloc[-2]["dc_unemployment_rate"])
        cols[1].metric("Unemployment Rate", f"{latest_ur:.1f}%", f"{latest_ur - prev_ur:+.1f}pp")
    else:
        cols[1].metric("Unemployment Rate", "N/A")

    # Median Income
    if not data["census_dc"].empty and "median_income" in data["census_dc"].columns:
        inc = int(data["census_dc"]["median_income"].iloc[0])
        cols[2].metric("Median Income", f"${inc:,}")
    else:
        cols[2].metric("Median Income", "N/A")

    # Average Agency Performance
    if not data["dc_agency_metrics"].empty and "value" in data["dc_agency_metrics"].columns:
        avg_perf = float(data["dc_agency_metrics"]["value"].mean())
        cols[3].metric("Avg Agency Performance", f"{avg_perf:.1f}", "out of 100")
    else:
        cols[3].metric("Avg Agency Performance", "N/A")

    st.divider()

    # Labor sparkline
    if not data["bls_wide"].empty:
        st.subheader("Unemployment Rate Trend (2019–2024)")
        fig_spark = go.Figure()
        fig_spark.add_trace(go.Scatter(
            x=data["bls_wide"]["date"], y=data["bls_wide"]["dc_unemployment_rate"],
            mode="lines", fill="tozeroy", line=dict(color="firebrick"), fillcolor="rgba(178,34,34,0.2)"
        ))
        fig_spark.update_layout(height=250, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_spark, use_container_width=True)

    # Agency performance mini chart
    if not data["dc_agency_metrics"].empty:
        st.subheader("Agency Performance Index (2024-Q1)")
        a_sorted = data["dc_agency_metrics"].sort_values("value", ascending=True)
        colors = ["firebrick" if v < 65 else "orange" if v < 75 else "darkgreen" for v in a_sorted["value"]]
        fig_agency = go.Figure(go.Bar(
            x=a_sorted["value"], y=a_sorted["agency_name"], orientation="h",
            marker_color=colors
        ))
        fig_agency.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20), xaxis_title="Performance Index")
        st.plotly_chart(fig_agency, use_container_width=True)

    # Briefing preview
    st.divider()
    st.subheader("📝 Latest Briefing")
    briefing_files = sorted(DATA_DIR.glob("briefing_*.md"))
    if briefing_files:
        latest = briefing_files[-1]
        with open(latest) as f:
            content = f.read()
        st.markdown(content[:1500] + ("\n\n..." if len(content) > 1500 else ""))
        with open(latest, "rb") as f:
            st.download_button(label="📥 Download Full Briefing", data=f, file_name=latest.name, mime="text/markdown")
    else:
        st.info("No briefing found. Run `python src/briefing_generator.py` to generate.")

# ===================== TAB 2: LABOR MARKET =====================
with tab2:
    st.header("💼 Labor Market Intelligence")
    st.caption("Source: BLS Local Area Unemployment Statistics (LAUS) — 72 monthly records, 2019–2024")

    if not data["bls_wide"].empty:
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Latest Unemployment", f"{data['bls_wide'].sort_values('date').iloc[-1]['dc_unemployment_rate']:.1f}%", "Dec 2024")
        with c2:
            st.metric("Latest Employment", f"{data['bls_wide'].sort_values('date').iloc[-1]['dc_employment_level']:.1f}k", "Dec 2024")

        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=data["bls_wide"]["date"], y=data["bls_wide"]["dc_unemployment_rate"],
                                    mode="lines", name="Unemployment Rate (%)", line=dict(color="firebrick")))
        fig1.update_layout(title="Unemployment Rate Trend", xaxis_title="Date", yaxis_title="Rate (%)", height=400)
        st.plotly_chart(fig1, use_container_width=True)

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=data["bls_wide"]["date"], y=data["bls_wide"]["dc_employment_level"],
                                    mode="lines", name="Employment Level (k)", line=dict(color="steelblue")))
        fig2.update_layout(title="Employment Level Trend", xaxis_title="Date", yaxis_title="Thousands", height=400)
        st.plotly_chart(fig2, use_container_width=True)

        # Dual axis
        fig3 = make_subplots(specs=[[{"secondary_y": True}]])
        fig3.add_trace(go.Scatter(x=data["bls_wide"]["date"], y=data["bls_wide"]["dc_unemployment_rate"],
                                    mode="lines", name="Unemployment (%)", line=dict(color="firebrick")), secondary_y=False)
        fig3.add_trace(go.Scatter(x=data["bls_wide"]["date"], y=data["bls_wide"]["dc_employment_level"],
                                    mode="lines", name="Employment (k)", line=dict(color="steelblue")), secondary_y=True)
        fig3.update_layout(title="Dual Axis: Unemployment vs Employment", height=450)
        fig3.update_yaxes(title_text="Unemployment (%)", secondary_y=False)
        fig3.update_yaxes(title_text="Employment (thousands)", secondary_y=True)
        st.plotly_chart(fig3, use_container_width=True)

        # Annual averages
        annual = data["bls_wide"].groupby("year").agg({"dc_unemployment_rate": "mean", "dc_employment_level": "mean"}).reset_index()
        fig4 = px.bar(annual, x="year", y="dc_unemployment_rate", color="dc_unemployment_rate",
                      color_continuous_scale="RdYlGn_r", title="Annual Average Unemployment Rate")
        fig4.update_layout(height=400)
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.warning("BLS wide data not found.")

# ===================== TAB 3: DEMOGRAPHICS =====================
with tab3:
    st.header("🏙️ Demographic & Economic Profile")
    st.caption("Source: US Census ACS 2023 (1 record) + DC Agency Metrics 2024-Q1 (10 records)")

    if not data["census_dc"].empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Population", f"{int(data['census_dc']['population'].iloc[0]):,}")
        c2.metric("Median Income", f"${int(data['census_dc']['median_income'].iloc[0]):,}")
        c3.metric("Bachelor's+", f"{data['census_dc']['pct_bachelors_plus'].iloc[0]}%")
        c4.metric("Poverty Rate", f"{data['census_dc']['poverty_rate'].iloc[0]}%")

        # Income benchmark
        us_median = 80610
        dc_median = data["census_dc"]["median_income"].iloc[0]
        fig_inc = go.Figure(go.Bar(
            x=["US National", "District of Columbia"], y=[us_median, dc_median],
            marker_color=["lightgray", "steelblue"], text=[f"${us_median:,}", f"${dc_median:,}"], textposition="outside"
        ))
        fig_inc.update_layout(title="Median Household Income Benchmark", height=400, yaxis=dict(range=[0, 120000]))
        st.plotly_chart(fig_inc, use_container_width=True)
    else:
        st.warning("Census data not found.")

    if not data["dc_agency_metrics"].empty:
        a_sorted = data["dc_agency_metrics"].sort_values("value", ascending=True)
        colors = ["firebrick" if v < 65 else "orange" if v < 75 else "darkgreen" for v in a_sorted["value"]]
        fig_ag = go.Figure(go.Bar(
            x=a_sorted["value"], y=a_sorted["agency_name"], orientation="h",
            marker_color=colors, text=a_sorted["value"], textposition="outside"
        ))
        fig_ag.update_layout(title="Agency Performance Index (2024-Q1)", height=450, xaxis=dict(range=[0, 100]))
        st.plotly_chart(fig_ag, use_container_width=True)
    else:
        st.warning("Agency metrics not found.")

# ===================== TAB 4: SCENARIOS =====================
with tab4:
    st.header("🔮 Scenario Planning")
    st.caption("What-if budget modeling across DC agencies. Baseline = historical FY2024 proportions.")

    AGENCIES = [
        "Department of Health", "Metropolitan Police Department", "Department of Transportation",
        "Department of Energy & Environment", "Office of the Chief Technology Officer",
        "Department of Human Services", "Department of Parks and Recreation", "DC Public Schools",
        "Department of Employment Services", "Department of Consumer and Regulatory Affairs"
    ]

    HISTORICAL_SHARES = {
        "Department of Health": 0.08, "Metropolitan Police Department": 0.18,
        "Department of Transportation": 0.07, "Department of Energy & Environment": 0.04,
        "Office of the Chief Technology Officer": 0.03, "Department of Human Services": 0.12,
        "Department of Parks and Recreation": 0.05, "DC Public Schools": 0.28,
        "Department of Employment Services": 0.06, "Department of Consumer and Regulatory Affairs": 0.04
    }

    # Scenario selector
    scenario_choice = st.radio("Select Scenario", ["Custom (adjust sliders)", "Baseline", "Optimistic", "Pessimistic"], horizontal=True)

    if scenario_choice == "Custom (adjust sliders)":
        allocations = {}
        col_left, col_right = st.columns(2)
        with col_left:
            for agency in AGENCIES[:5]:
                allocations[agency] = st.slider(agency, 0.0, 0.50, HISTORICAL_SHARES[agency], 0.01, key=f"slider_{agency}")
        with col_right:
            for agency in AGENCIES[5:]:
                allocations[agency] = st.slider(agency, 0.0, 0.50, HISTORICAL_SHARES[agency], 0.01, key=f"slider_{agency}")
        total = sum(allocations.values())
        if total > 0:
            allocations = {k: v / total for k, v in allocations.items()}
        st.info(f"Total allocation: {total:.1%} (normalized to 100%)")
    elif scenario_choice == "Baseline":
        allocations = HISTORICAL_SHARES.copy()
    elif scenario_choice == "Optimistic":
        allocations = HISTORICAL_SHARES.copy()
        top4 = ["Department of Energy & Environment", "Office of the Chief Technology Officer",
                "Department of Parks and Recreation", "Metropolitan Police Department"]
        for a in top4:
            allocations[a] *= 1.15
        total = sum(allocations.values())
        allocations = {k: v/total for k, v in allocations.items()}
    else:  # Pessimistic
        allocations = {k: v * 0.90 for k, v in HISTORICAL_SHARES.items()}
        for a in ["Department of Human Services", "Department of Employment Services", "Department of Health"]:
            allocations[a] *= 1.20
        total = sum(allocations.values())
        allocations = {k: v/total for k, v in allocations.items()}

    # Run projection
    scenario_rows = []
    for _, row in data["dc_agency_metrics"].iterrows():
        agency = row["agency_name"]
        base = HISTORICAL_SHARES.get(agency, 0.05)
        share = allocations.get(agency, base)
        base_perf = row["value"]
        change = (share - base) / base if base > 0 else 0
        projected = base_perf * (1 + 0.3 * change)
        scenario_rows.append({
            "Agency": agency,
            "Budget Share": f"{share:.1%}",
            "Budget ($)": f"${share * 20_600_000_000:,.0f}",
            "Baseline Performance": base_perf,
            "Projected Performance": round(min(100, projected), 1),
            "Delta": round(min(100, projected) - base_perf, 1)
        })

    scenario_df = pd.DataFrame(scenario_rows)
    st.dataframe(scenario_df, use_container_width=True)

    # Scenario charts
    fig_scenario = go.Figure()
    fig_scenario.add_trace(go.Bar(
        x=scenario_df["Agency"], y=scenario_df["Baseline Performance"],
        name="Baseline", marker_color="lightgray"
    ))
    fig_scenario.add_trace(go.Bar(
        x=scenario_df["Agency"], y=scenario_df["Projected Performance"],
        name="Projected", marker_color="steelblue"
    ))
    fig_scenario.update_layout(
        barmode="group", title=f"Projected Performance: {scenario_choice}",
        xaxis_tickangle=-45, yaxis_title="Performance Index", height=450
    )
    st.plotly_chart(fig_scenario, use_container_width=True)

    # Delta chart
    fig_delta = px.bar(scenario_df, x="Agency", y="Delta", color="Delta",
                       color_continuous_scale="RdYlGn", title="Performance Delta from Baseline")
    fig_delta.update_layout(xaxis_tickangle=-45, height=400)
    st.plotly_chart(fig_delta, use_container_width=True)

st.divider()
st.caption("Built with real data from DC Open Data, US Census ACS, and Bureau of Labor Statistics.")
