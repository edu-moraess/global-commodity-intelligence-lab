import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from app.components.layout import inject_css, status_bar
from src.database.repository import DataRepository

st.set_page_config(page_title="Data Explorer | GCIL", layout="wide")
inject_css()
st.title("🔍 Data Explorer")

repo = DataRepository(prefer_mock=True)
cmd, macro, geo, meta = repo.load_latest()
status_bar(meta, n_records=len(cmd))

if cmd.empty:
    st.warning("No data.")
else:
    cats = ["ALL"] + sorted(cmd["category"].dropna().unique().tolist())
    cat = st.selectbox("Category", cats)
    assets = sorted(cmd["asset"].unique().tolist()) if cat == "ALL" else sorted(cmd[cmd["category"] == cat]["asset"].unique().tolist())
    asset = st.multiselect("Asset(s)", assets, default=assets[:5] if assets else [])
    metrics = [c for c in cmd.columns if c not in ("date", "asset", "category", "ticker", "source")]
    metric = st.selectbox("Metric", metrics or ["spot_price"])

    view = cmd.copy()
    if cat != "ALL":
        view = view[view["category"] == cat]
    if asset:
        view = view[view["asset"].isin(asset)]
    st.dataframe(view[["date", "asset", "category", metric] if metric in view.columns else view.columns], use_container_width=True)
