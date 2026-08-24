import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from app.components.layout import inject_css, status_bar
from src.database.repository import DataRepository
from src.geopolitics.engine import geopolitical_risk_score

st.set_page_config(page_title="Geopolitics | GCIL", layout="wide")
inject_css()
st.title("🛰️ Geopolitics")

repo = DataRepository(prefer_mock=True)
_, _, geo, meta = repo.load_latest()
status_bar(meta, n_records=len(geo))

score = geopolitical_risk_score(geo)
st.metric("Geopolitical Risk Score", score.get("score") or "—")
st.json(score.get("by_region", {}))

if not geo.empty:
    st.dataframe(geo, use_container_width=True)
else:
    st.info("No geopolitical events loaded.")
