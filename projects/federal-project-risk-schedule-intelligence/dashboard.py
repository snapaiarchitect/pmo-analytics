import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os

# Page config
st.set_page_config(
    page_title="Federal Contract Risk & Schedule Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

@st.cache_data
def load_data():
    """Load all contract data."""
    try:
        contracts = pd.read_csv(os.path.join(DATA_DIR, 'hybrid_forecast_results.csv'))
        agency_stats = pd.read_csv(os.path.join(DATA_DIR, 'agency_schedule_stats.csv'), index_col=0)
        return contracts, agency_stats
    except:
        return None, None

# Sidebar
st.sidebar.title("🎯 Federal Contract Intelligence")
st.sidebar.markdown("---")
st.sidebar.info("""
**Real Data Sources:**
- USASpending.gov (1,000+ federal contracts)
- Risk-adjusted schedule forecasting
- Monte Carlo simulation (10,000 runs/contract)
""")

# Main content
st.title("Federal Contract Risk & Schedule Intelligence")
st.markdown("""
**Risk-adjusted completion forecasting** combining agency-level risk patterns 
with live federal contract data from USASpending.gov.
""")

# Load data
contracts, agency_stats = load_data()

if contracts is None:
    st.error("""
    ⚠️ Data not found. Please run the data pipeline first:
    ```bash
    python src/download_federal_contracts.py
    python src/risk_classifier.py
    python src/schedule_analyzer.py
    python src/hybrid_model.py
    ```
    """)
    st.stop()

# Executive Summary Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Contracts", len(contracts))
with col2:
    critical = (contracts['risk_level'] == 'Critical').sum()
    st.metric("Critical Risk", critical, delta=f"{critical/len(contracts):.1%}")
with col3:
    high = (contracts['risk_level'] == 'High').sum()
    st.metric("High Risk", high, delta=f"{high/len(contracts):.1%}")
with col4:
    avg_p80 = contracts['p80'].mean()
    st.metric("Avg P80 Score", f"{avg_p80:.1f}/100")

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Portfolio Risk Heatmap", "📈 Schedule Variance", "🎯 Risk-Adjusted Forecast", "🏛️ Agency Breakdown"])

# Tab 1: Risk Heatmap
with tab1:
    st.subheader("Portfolio Risk Heatmap")
    
    # Risk level distribution
    risk_dist = contracts['risk_level'].value_counts().reindex(['Low', 'Medium', 'High', 'Critical']).fillna(0)
    
    fig_risk = go.Figure(data=[
        go.Bar(
            x=risk_dist.index,
            y=risk_dist.values,
            marker_color=['#2ecc71', '#f1c40f', '#e67e22', '#e74c3c']
        )
    ])
    fig_risk.update_layout(
        title="Contracts by Risk Level",
        xaxis_title="Risk Level",
        yaxis_title="Number of Contracts",
        showlegend=False
    )
    st.plotly_chart(fig_risk, use_container_width=True)
    
    # Heatmap by agency + risk level
    heatmap_data = contracts.groupby(['agency', 'risk_level']).size().unstack(fill_value=0)
    heatmap_data = heatmap_data.reindex(columns=['Low', 'Medium', 'High', 'Critical'], fill_value=0)
    
    fig_heatmap = px.imshow(
        heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        color_continuous_scale='RdYlGn_r',
        title="Risk Distribution by Agency"
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

# Tab 2: Schedule Variance
with tab2:
    st.subheader("Schedule Variance Analysis")
    
    # P50/P80/P95 comparison by agency
    fig_delay = go.Figure()
    
    for percentile, color, name in [
        ('p50', '#3498db', 'P50 (Median)'),
        ('p80', '#e67e22', 'P80 (Likely)'),
        ('p95', '#e74c3c', 'P95 (Worst Case)')
    ]:
        fig_delay.add_trace(go.Bar(
            name=name,
            x=contracts.groupby('agency')[percentile].mean().index,
            y=contracts.groupby('agency')[percentile].mean().values,
            marker_color=color
        ))
    
    fig_delay.update_layout(
        title="Risk Score Forecasts by Agency",
        xaxis_title="Agency",
        yaxis_title="Risk Score (0-100)",
        barmode='group'
    )
    st.plotly_chart(fig_delay, use_container_width=True)
    
    # SPI vs Risk Score scatter
    fig_scatter = px.scatter(
        contracts,
        x='risk_score',
        y='p80',
        color='risk_level',
        size='base_duration',
        hover_data=['award_id', 'agency'],
        title="Risk Score vs Schedule Performance",
        color_discrete_map={
            'Low': '#2ecc71',
            'Medium': '#f1c40f',
            'High': '#e67e22',
            'Critical': '#e74c3c'
        }
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# Tab 3: Risk-Adjusted Forecast
with tab3:
    st.subheader("Risk-Adjusted Completion Forecast")
    
    # Top risk contracts
    top_risk = contracts.nlargest(10, 'p80')
    
    fig_mc = go.Figure()
    
    for _, contract in top_risk.iterrows():
        fig_mc.add_trace(go.Scatter(
            x=['P50', 'P80', 'P95'],
            y=[contract['p50'], contract['p80'], contract['p95']],
            mode='lines+markers',
            name=f"{str(contract['recipient'])[:30]}...",
            line=dict(width=2),
            marker=dict(size=8)
        ))
    
    fig_mc.update_layout(
        title="Top 10 At-Risk Contracts: Risk Score Forecasts",
        xaxis_title="Confidence Level",
        yaxis_title="Projected Risk Score (0-100)",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.5)
    )
    st.plotly_chart(fig_mc, use_container_width=True)
    
    # Distribution of P80 scores
    fig_hist = px.histogram(
        contracts,
        x='p80',
        color='risk_level',
        nbins=30,
        title="Distribution of P80 Risk Scores",
        color_discrete_map={
            'Low': '#2ecc71',
            'Medium': '#f1c40f',
            'High': '#e67e22',
            'Critical': '#e74c3c'
        }
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# Tab 4: Agency Breakdown
with tab4:
    st.subheader("Agency Performance Breakdown")
    
    if agency_stats is not None:
        # Agency performance table
        display_cols = ['avg_duration', 'contract_count']
        display_df = agency_stats[display_cols].copy()
        display_df.columns = ['Avg Duration (days)', 'Contracts']
        display_df = display_df.sort_values('Avg Duration (days)', ascending=False)
        
        st.dataframe(display_df.style.format({
            'Avg Duration (days)': '{:.0f}'
        }), use_container_width=True)
    
    # Top at-risk contracts table
    st.subheader("Top 20 At-Risk Contracts")
    top20 = contracts.nlargest(20, 'p80')[['award_id', 'recipient', 'agency', 'base_duration', 'p50', 'p80', 'p95', 'risk_level']]
    top20.columns = ['Award ID', 'Recipient', 'Agency', 'Base Duration', 'P50 Score', 'P80 Score', 'P95 Score', 'Risk Level']
    
    def color_risk(val):
        colors = {
            'Critical': 'background-color: #e74c3c; color: white',
            'High': 'background-color: #e67e22; color: white',
            'Medium': 'background-color: #f1c40f',
            'Low': 'background-color: #2ecc71; color: white'
        }
        return colors.get(val, '')
    
    st.dataframe(
        top20.style.applymap(color_risk, subset=['Risk Level']).format({
            'P50 Score': '{:.1f}',
            'P80 Score': '{:.1f}',
            'P95 Score': '{:.1f}',
            'Base Duration': '{:.0f}'
        }),
        use_container_width=True
    )

# Footer
st.markdown("---")
st.caption("""
🎯 **Federal Contract Risk & Schedule Intelligence** | Built with real data from USASpending.gov
| Risk-adjusted Monte Carlo forecasting | No synthetic data | 100% real federal contract data
""")
