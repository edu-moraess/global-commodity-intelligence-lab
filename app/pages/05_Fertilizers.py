import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from app.components.layout import inject_css, status_bar
from app.components.charts import price_bar, ranking_bar
from src.database.repository import get_repository
from src.ingestion.validator import quality_report

st.set_page_config(page_title="Fertilizers | GCIL", layout="wide")
inject_css()
st.title("🧪 Fertilizers")

repo = get_repository()
cmd, _, _, meta = repo.load_latest()
df = cmd[cmd["category"] == "FERTILIZERS"] if not cmd.empty else cmd
n = len(df)
q = quality_report(df).get("completeness") if not df.empty else None
status_bar(meta, n_records=n, quality=q)

if not df.empty:
    st.plotly_chart(price_bar(df, "Fertilizers Spot Prices"), use_container_width=True)
    st.plotly_chart(ranking_bar(df), use_container_width=True)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No fertilizer records.")
