import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from app.components.layout import inject_css, status_bar
from app.components.charts import correlation_heatmap
from src.database.repository import get_repository
from src.quantitative.correlation import correlation_matrix

st.set_page_config(page_title="Quantitative | GCIL", layout="wide")
inject_css()
st.title("📐 Quantitative")

repo = get_repository()
cmd, _, _, meta = repo.load_latest()
status_bar(meta, n_records=len(cmd))

if not cmd.empty:
    cols = [c for c in [
        "asset", "spot_price", "daily_change", "z_score", "rsi", "macd",
        "hist_vol", "volatility_regime", "curve_structure", "momentum"
    ] if c in cmd.columns]
    st.dataframe(cmd[cols], use_container_width=True)

    corr = correlation_matrix(cmd)
    if not corr.empty:
        st.plotly_chart(correlation_heatmap(corr), use_container_width=True)
    else:
        st.info(
            "Correlation matrix requires multi-period history "
            "(populates after historical accumulation)."
        )
else:
    st.warning("No data.")
