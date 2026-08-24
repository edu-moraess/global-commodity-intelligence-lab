import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from app.components.layout import inject_css, status_bar
from src.database.repository import get_repository
from src.processing.historical import load_historical, slice_history

st.set_page_config(page_title="Historical | GCIL", layout="wide")
inject_css()
st.title("📜 Historical")

repo = get_repository()
cmd, _, _, meta = repo.load_latest()
status_bar(meta, n_records=len(cmd))

hist = load_historical()
if hist.empty:
    st.info(
        "Historical parquet not yet accumulated. "
        "Run `python scripts/ingest_daily.py` after placing a RAW file. "
        "Single-day snapshot shown below."
    )
    if not cmd.empty:
        st.dataframe(cmd, use_container_width=True)
else:
    window = st.selectbox(
        "Window",
        [7, 30, 90, 365, None],
        format_func=lambda x: "Full" if x is None else f"{x}d",
    )
    view = slice_history(hist, window)
    st.dataframe(view, use_container_width=True)
