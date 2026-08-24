import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from app.components.layout import inject_css, status_bar
from src.database.repository import get_repository
from src.forecasting.directional import extract_forecasts

st.set_page_config(page_title="Forecasts | GCIL", layout="wide")
inject_css()
st.title("🔮 Forecasts")

st.warning("No synthetic forecasts are presented as real predictions. Architecture only.")

repo = get_repository()
cmd, _, _, meta = repo.load_latest()
status_bar(meta, n_records=len(cmd))

fc = extract_forecasts(cmd)
if not fc.empty:
    st.dataframe(fc, use_container_width=True)
else:
    st.info(
        "No forecast objects present in current dataset. "
        "Future sources: MODEL_FORECAST | GROK_FORECAST | MARKET_SIGNAL"
    )

st.markdown("""
### Evaluation metrics (prepared for Phase 4/5)
- Hit ratio · Forecast error · Brier score · Calibration · Directional accuracy
""")
