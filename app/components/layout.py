"""Shared layout & status bar."""

from __future__ import annotations

import streamlit as st
from typing import Any, Dict


def inject_css():
    st.markdown("""
    <style>
    .stApp { background-color: #0b0f14; color: #e0e6ed; }
    .metric-card {
        background: linear-gradient(145deg, #121820, #0e141c);
        border: 1px solid #1e2a38;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
    }
    .status-dot { display: inline-block; width: 10px; height: 10px;
                  border-radius: 50%; margin-right: 6px; }
    .status-ok { background: #00c853; }
    .status-mock { background: #ffab00; }
    .status-err { background: #ff1744; }
    h1, h2, h3 { color: #00e5ff !important; font-family: 'JetBrains Mono', monospace; }
    .block-container { padding-top: 1.5rem; }
    </style>
    """, unsafe_allow_html=True)


def status_bar(meta: Dict[str, Any], n_records: int = 0, quality: float | None = None):
    """
    Clear LIVE vs DEMO distinction.

    meta keys expected:
      mode: MOCK | RAW
      source, date, errors, ok, data_mode_config
    """
    mode = str(meta.get("mode", "UNKNOWN")).upper()
    is_mock = mode == "MOCK"
    is_error = meta.get("ok") is False and mode == "RAW"
    cfg = meta.get("data_mode_config", "auto")

    if is_error:
        dot = "status-err"
        label = "RAW ERROR"
    elif is_mock:
        dot = "status-mock"
        label = "DEMO / MOCK DATA"
    else:
        dot = "status-ok"
        label = "LIVE / RAW DATA"

    source = meta.get("source") or ("MOCK_SYNTHETIC" if is_mock else "GROK_DAILY_INTELLIGENCE")
    update = meta.get("date") or ("MOCK" if is_mock else "—")
    q = f"{quality:.1f}%" if quality is not None else "—"

    st.markdown(f"""
    <div class="metric-card">
    <b>DATA STATUS</b> <span class="status-dot {dot}"></span>{label} &nbsp;|&nbsp;
    <b>SOURCE</b> {source} &nbsp;|&nbsp;
    <b>DATASET</b> {update} &nbsp;|&nbsp;
    <b>RECORDS</b> {n_records} &nbsp;|&nbsp;
    <b>QUALITY</b> {q} &nbsp;|&nbsp;
    <b>MODE</b> {cfg}
    </div>
    """, unsafe_allow_html=True)

    if is_mock:
        st.warning(
            "⚠️ DEMO / MOCK DATA — Not real market data. "
            "For architecture validation only. Switch to LIVE when RAW is available."
        )
    elif is_error:
        errs = meta.get("errors") or ["Unknown RAW error"]
        st.error("❌ RAW mode active but no valid dataset loaded.\n" + "\n".join(str(e) for e in errs))
    else:
        st.success(f"✅ LIVE / RAW DATA — Source: {source} | Dataset: {update}")
