"""Metric cards."""

from __future__ import annotations

import streamlit as st
import pandas as pd


def top_movers(df: pd.DataFrame, n: int = 5):
    if df.empty or "daily_change" not in df.columns:
        st.info("No change data available.")
        return
    tmp = df.dropna(subset=["daily_change"]).copy()
    gainers = tmp.nlargest(n, "daily_change")[["asset", "daily_change", "spot_price"]]
    losers = tmp.nsmallest(n, "daily_change")[["asset", "daily_change", "spot_price"]]
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("▲ Top Gainers")
        st.dataframe(gainers.style.format({"daily_change": "{:.2%}", "spot_price": "{:.2f}"}), use_container_width=True)
    with c2:
        st.subheader("▼ Top Losers")
        st.dataframe(losers.style.format({"daily_change": "{:.2%}", "spot_price": "{:.2f}"}), use_container_width=True)
