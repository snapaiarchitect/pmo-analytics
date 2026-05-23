import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

st.set_page_config(page_title="Capital Portfolio Governance", layout="wide")

# ── Load Data ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    contracts = pd.read_csv('data/federal_contracts_all.csv')
    grants = pd.read_csv('data/usaspending_transit_grants.csv')
    ntd = pd.read_csv('data/ntd_capital_expenses.csv')
    # clean NTD
    ntd['total'] = pd.to_numeric(ntd['total'], errors='coerce').fillna(0)
    for col in ['passenger_vehicles', 'guideway', 'stations']:
        if col in ntd.columns:
            ntd[col] = pd.to_numeric(ntd[col], errors='coerce').fillna(0)
    return contracts, grants, ntd

contracts, grants, ntd = load_data()

# ── Sidebar ────────────────────────────────────────────────────────────────
st.sidebar.title("Capital Portfolio Governance")
st.sidebar.markdown("Federal transit investment analytics")
st.sidebar.markdown("---")
tab = st.sidebar.radio("Select View", ["Contracts", "Capital", "Portfolio"])

# ── TAB 1: Contracts ─────────────────────────────────────────────────────────
if tab == "Contracts":
    st.header("Federal Contracts Portfolio")
    st.markdown(f"**Source:** USASpending.gov — {len(contracts):,} contracts, **${contracts.award_amount.sum()/1e9:.1f}B** total")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Contracts", f"{len(contracts):,}")
    col2.metric("Total Obligations", f"${contracts.award_amount.sum()/1e9:.1f}B")
    col3.metric("Unique Vendors", f"{contracts.recipient.nunique():,}")
    col4.metric("Avg Duration", f"{contracts.duration_days.mean():.0f} days")

    st.subheader("Top Agencies by Obligation")
    agency_spend = contracts.groupby('agency')['award_amount'].sum().sort_values(ascending=False).head(15).reset_index()
    agency_spend['award_amount_b'] = agency_spend['award_amount'] / 1e9
    fig = px.bar(agency_spend, x='award_amount_b', y='agency', orientation='h',
                 labels={'award_amount_b': 'Obligations ($B)', 'agency': 'Agency'},
                 color='award_amount_b', color_continuous_scale='Blues')
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Vendor Concentration (HHI)")
    vendor_spend = contracts.groupby('recipient')['award_amount'].sum()
    shares = (vendor_spend / vendor_spend.sum() * 100)
    hhi = (shares ** 2).sum()
    top_vendors = vendor_spend.sort_values(ascending=False).head(15).reset_index()
    top_vendors['award_amount_b'] = top_vendors['award_amount'] / 1e9

    c1, c2 = st.columns([2, 1])
    with c1:
        fig2 = px.bar(top_vendors, x='award_amount_b', y='recipient', orientation='h',
                      labels={'award_amount_b': 'Obligations ($B)', 'recipient': 'Vendor'},
                      color='award_amount_b', color_continuous_scale='Viridis')
        fig2.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig2, use_container_width=True)
    with c2:
        st.metric("Vendor HHI", f"{hhi:.0f}")
        if hhi > 2500:
            st.error("Highly Concentrated")
        elif hhi > 1500:
            st.warning("Moderately Concentrated")
        else:
            st.success("Competitive")
        st.markdown("HHI \> 2,500 = highly concentrated market")

    st.subheader("Obligation Trends Over Time")
    contracts['start_year'] = pd.to_datetime(contracts['start_date'], errors='coerce').dt.year
    yearly = contracts.dropna(subset=['start_year']).groupby('start_year')['award_amount'].agg(['sum', 'count']).reset_index()
    yearly['sum_b'] = yearly['sum'] / 1e9
    fig3 = make_subplots(specs=[[{"secondary_y": True}]])
    fig3.add_trace(go.Bar(x=yearly['start_year'], y=yearly['sum_b'], name='Obligations ($B)', marker_color='steelblue'), secondary_y=False)
    fig3.add_trace(go.Scatter(x=yearly['start_year'], y=yearly['count'], name='Contract Count', mode='lines+markers', line=dict(color='firebrick')), secondary_y=True)
    fig3.update_layout(title='Federal Contract Obligations by Year', xaxis_title='Year')
    fig3.update_yaxes(title_text="Obligations ($B)", secondary_y=False)
    fig3.update_yaxes(title_text="Count", secondary_y=True)
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Geographic Distribution")
    state_spend = contracts.dropna(subset=['state']).groupby('state')['award_amount'].sum().sort_values(ascending=False).head(15).reset_index()
    state_spend['award_amount_b'] = state_spend['award_amount'] / 1e9
    fig4 = px.bar(state_spend, x='state', y='award_amount_b',
                  labels={'award_amount_b': 'Obligations ($B)', 'state': 'State'},
                  color='award_amount_b', color_continuous_scale='RdYlBu')
    st.plotly_chart(fig4, use_container_width=True)

# ── TAB 2: Capital ───────────────────────────────────────────────────────────
if tab == "Capital":
    st.header("FTA Capital Investment Analysis")
    st.markdown(f"**Source:** FTA NTD 2024 — {len(ntd):,} records, **${ntd.total.sum()/1e9:.1f}B** total capital")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Records", f"{len(ntd):,}")
    col2.metric("Total Capital", f"${ntd.total.sum()/1e9:.1f}B")
    col3.metric("Unique Agencies", f"{ntd.agency.nunique():,}")
    col4.metric("Unique Modes", f"{ntd.mode_name.nunique()}")

    st.subheader("Capital by Transit Mode")
    mode_spend = ntd.groupby('mode_name')['total'].sum().sort_values(ascending=False).reset_index()
    mode_spend['total_m'] = mode_spend['total'] / 1e6
    fig = px.bar(mode_spend, x='total_m', y='mode_name', orientation='h',
                 labels={'total_m': 'Capital ($M)', 'mode_name': 'Mode'},
                 color='total_m', color_continuous_scale='Plasma')
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Rehabilitation vs Expansion")
    form_spend = ntd.groupby('form_type')['total'].sum().sort_values(ascending=False).reset_index()
    form_spend['total_m'] = form_spend['total'] / 1e6
    c1, c2 = st.columns(2)
    with c1:
        fig2 = px.pie(form_spend, values='total_m', names='form_type',
                      title='Capital by Form Type')
        st.plotly_chart(fig2, use_container_width=True)
    with c2:
        fig3 = px.bar(form_spend, x='total_m', y='form_type', orientation='h',
                      labels={'total_m': 'Capital ($M)', 'form_type': 'Form Type'},
                      color='total_m', color_continuous_scale='Spectral')
        fig3.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Top Agencies by Capital Expenditure")
    agency_cap = ntd.groupby('agency')['total'].sum().sort_values(ascending=False).head(20).reset_index()
    agency_cap['total_m'] = agency_cap['total'] / 1e6
    fig4 = px.bar(agency_cap, x='total_m', y='agency', orientation='h',
                  labels={'total_m': 'Capital ($M)', 'agency': 'Agency'},
                  color='total_m', color_continuous_scale='RdYlGn')
    fig4.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig4, use_container_width=True)

    st.subheader("Capital Intensity by Population")
    uza_df = ntd.groupby(['uza_name', 'primary_uza_population'])['total'].sum().reset_index()
    uza_df = uza_df.dropna(subset=['primary_uza_population'])
    uza_df['capital_per_capita'] = uza_df['total'] / uza_df['primary_uza_population']
    uza_df = uza_df[uza_df.capital_per_capita <= uza_df.capital_per_capita.quantile(0.98)]
    fig5 = px.scatter(uza_df, x='primary_uza_population', y='capital_per_capita',
                      size='total', color='total',
                      hover_name='uza_name',
                      labels={'primary_uza_population': 'Population', 'capital_per_capita': 'Capital per Capita ($)'},
                      title='Capital Intensity by Urbanized Area')
    st.plotly_chart(fig5, use_container_width=True)

# ── TAB 3: Portfolio ─────────────────────────────────────────────────────────
if tab == "Portfolio":
    st.header("Combined Portfolio Executive View")
    total_contracts = contracts.award_amount.sum()
    total_grants = grants.amount.sum()
    total_ntd = ntd.total.sum()
    total_portfolio = total_contracts + total_grants + total_ntd

    st.markdown(f"**Combined Portfolio:** **${total_portfolio/1e9:.1f}B** across 3 verified federal data sources")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Federal Contracts", f"${total_contracts/1e9:.1f}B")
    col2.metric("Transit Grants", f"${total_grants/1e9:.1f}B")
    col3.metric("NTD Capital", f"${total_ntd/1e9:.1f}B")
    col4.metric("Total Records", f"{len(contracts)+len(grants)+len(ntd):,}")

    st.subheader("Portfolio Composition")
    composition = pd.DataFrame({
        'Source': ['Contracts', 'Grants', 'NTD Capital'],
        'Amount': [total_contracts/1e9, total_grants/1e9, total_ntd/1e9]
    })
    fig = px.pie(composition, values='Amount', names='Source',
                 title='Portfolio Composition by Source ($B)',
                 color_discrete_sequence=['steelblue', 'firebrick', 'seagreen'])
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Multi-Source Timeline")
    contracts['year'] = pd.to_datetime(contracts['start_date'], errors='coerce').dt.year
    contract_timeline = contracts.dropna(subset=['year']).groupby('year')['award_amount'].sum() / 1e9
    grants['year'] = pd.to_datetime(grants['start_date'], errors='coerce').dt.year
    grant_timeline = grants.dropna(subset=['year']).groupby('year')['amount'].sum() / 1e9
    all_years = sorted(set(contract_timeline.index) | set(grant_timeline.index))
    c_vals = [contract_timeline.get(y, 0) for y in all_years]
    g_vals = [grant_timeline.get(y, 0) for y in all_years]

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=all_years, y=c_vals, mode='lines+markers', name='Contracts ($B)', line=dict(color='steelblue', width=3)))
    fig2.add_trace(go.Scatter(x=all_years, y=g_vals, mode='lines+markers', name='Grants ($B)', line=dict(color='firebrick', width=3)))
    fig2.update_layout(title='Contracts + Grants Timeline', xaxis_title='Year', yaxis_title='Obligations ($B)')
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Top Grant Recipients")
    grant_top = grants.groupby('recipient')['amount'].sum().sort_values(ascending=False).head(15).reset_index()
    grant_top['amount_b'] = grant_top['amount'] / 1e9
    fig3 = px.bar(grant_top, x='amount_b', y='recipient', orientation='h',
                  labels={'amount_b': 'Grants ($B)', 'recipient': 'Recipient'},
                  color='amount_b', color_continuous_scale='Reds')
    fig3.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Portfolio Health Score — Top Grant Recipients")
    grant_health = grants.groupby('recipient').agg({'amount': ['sum', 'count', 'mean']}).reset_index()
    grant_health.columns = ['recipient', 'total_amount', 'grant_count', 'avg_grant']
    grant_health = grant_health.sort_values('total_amount', ascending=False).head(15)
    grant_health['health_score'] = (
        (grant_health['total_amount'] / grant_health['total_amount'].max()) * 0.5 +
        (grant_health['grant_count'] / grant_health['grant_count'].max()) * 0.3 +
        (grant_health['avg_grant'] / grant_health['avg_grant'].max()) * 0.2
    ) * 100
    fig4 = px.bar(grant_health, x='health_score', y='recipient', orientation='h',
                  color='health_score', color_continuous_scale='RdYlGn',
                  labels={'health_score': 'Health Score', 'recipient': 'Recipient'})
    fig4.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig4, use_container_width=True)

    st.subheader("Contract Risk Heatmap by Agency")
    risk_agencies = contracts.groupby('agency').agg({
        'award_amount': ['sum', 'count', 'mean'],
        'duration_days': 'mean'
    }).reset_index()
    risk_agencies.columns = ['agency', 'total', 'count', 'avg', 'avg_duration']
    risk_agencies = risk_agencies.sort_values('total', ascending=False).head(10)
    metrics = ['total', 'count', 'avg', 'avg_duration']
    for m in metrics:
        risk_agencies[m + '_risk'] = (risk_agencies[m] / risk_agencies[m].max()) * 10
    heatmap_data = risk_agencies.set_index('agency')[[m + '_risk' for m in metrics]]
    heatmap_data.columns = ['Obligation Volume', 'Contract Count', 'Avg Value', 'Duration']
    fig5 = px.imshow(heatmap_data.values, x=heatmap_data.columns, y=heatmap_data.index,
                     color_continuous_scale='Reds', title='Risk Score (0-10)')
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown("---")
    st.markdown("**Data Authenticity:** All data sourced from verified federal APIs. No synthetic data used.")
