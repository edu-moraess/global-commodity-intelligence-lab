"""Overview page (mirrors main for multipage consistency)."""

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from app.components.layout import inject_css, status_bar
from app.components.charts import price_bar, returns_heatmap, ranking_bar
from app.components.cards import top_movers
from src.database.repository import DataRepository
from src.geopolitics.engine import geopolitical_risk_score
from src.ingestion.validator import quality_report

st.set_page_config(page_title="Overview | GCIL", layout="wide")
inject_css()
st.title("Overview")

repo = DataRepository(prefer_mock=True)
cmd, macro, geo, meta = repo.load_latest()
n = len(cmd)
q = quality_report(cmd).get("completeness") if not cmd.empty else None
status_bar(meta, n_records=n, quality=q)

if not cmd.empty:
    st.plotly_chart(price_bar(cmd), use_container_width=True)
    st.plotly_chart(returns_heatmap(cmd), use_container_width=True)
    top_movers(cmd)
else:
    st.warning("No commodity data loaded.")
