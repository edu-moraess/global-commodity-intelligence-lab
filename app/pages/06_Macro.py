import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from app.components.layout import inject_css, status_bar
from src.database.repository import DataRepository
from src.macro.engine import build_macro_summary

st.set_page_config(page_title="Macro | GCIL", layout="wide")
inject_css()
st.title("🌐 Macro")

repo = DataRepository(prefer_mock=True)
_, macro, _, meta = repo.load_latest()
status_bar(meta, n_records=len(macro))

summary = build_macro_summary(macro)
st.subheader(f"Global Macro Regime: {summary.get('regime')}")
st.json(summary.get("components", {}))

if not macro.empty:
    st.dataframe(macro, use_container_width=True)
else:
    st.info("No macro indicators loaded.")

st.markdown("""
**Components of GLOBAL MACRO REGIME (conceptual):**
- Growth
- Inflation
- Liquidity
- Rates
- USD
- Commodity Demand
""")
