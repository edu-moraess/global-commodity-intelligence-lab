"""
Global Commodity Intelligence Lab — Main Streamlit entrypoint.
Quantitative terminal for energy, metals, agriculture, fertilizers, macro & geopolitics.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

st.set_page_config(
    page_title="Global Commodity Intelligence Lab",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app.components.layout import inject_css, status_bar
from app.components.charts import price_bar, returns_heatmap, ranking_bar
from app.components.cards import top_movers
from src.database.repository import get_repository
from src.macro.engine import build_macro_summary
from src.geopolitics.engine import geopolitical_risk_score
from src.ingestion.validator import quality_report

inject_css()

st.title("📡 Global Commodity Intelligence Lab")
st.caption("Quantitative intelligence platform — Phase 2A | AUTO data mode")

repo = get_repository()  # reads config.toml data_mode (default: auto)
cmd, macro, geo, meta = repo.load_latest()

n = len(cmd)
q = quality_report(cmd).get("completeness") if not cmd.empty else None
status_bar(meta, n_records=n, quality=q)

st.subheader("Global Snapshot")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Commodities tracked", n)
with col2:
    up = int((cmd["daily_change"] > 0).sum()) if "daily_change" in cmd.columns else 0
    st.metric("In gain", up)
with col3:
    down = int((cmd["daily_change"] < 0).sum()) if "daily_change" in cmd.columns else 0
    st.metric("In loss", down)
with col4:
    geo_score = geopolitical_risk_score(geo)
    st.metric("Geopolitical Risk", geo_score.get("score") or "—")

macro_sum = build_macro_summary(macro)
st.info(
    f"Global Macro Regime (conceptual): **{macro_sum.get('regime')}** | "
    f"Indicators: {macro_sum.get('n_indicators', 0)}"
)

if not cmd.empty:
    st.plotly_chart(price_bar(cmd, "Spot Prices by Asset"), use_container_width=True)
    st.plotly_chart(returns_heatmap(cmd), use_container_width=True)
    top_movers(cmd)
    st.plotly_chart(ranking_bar(cmd), use_container_width=True)
else:
    st.warning("No commodity records loaded for the current data mode.")

if not geo.empty:
    st.subheader("Active Geopolitical Events")
    st.dataframe(geo, use_container_width=True)

st.sidebar.title("Navigation")
st.sidebar.markdown("""
Use the pages menu to explore:
- Overview (this page)
- Energy / Metals / Agriculture / Fertilizers
- Macro / Geopolitics
- Quantitative / Forecasts / Historical
- Data Explorer
""")
st.sidebar.markdown("---")
st.sidebar.caption(
    f"Data mode: **{meta.get('data_mode_config', 'auto')}**\n"
    f"Active: **{meta.get('mode', '—')}**\n"
    "Phase 2A — Real data pipeline ready"
)
