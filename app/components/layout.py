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
    mode = meta.get("mode", "UNKNOWN")
    is_mock = mode == "MOCK"
    dot = "status-mock" if is_mock else "status-ok"
    label = "DEMO / MOCK DATA" if is_mock else "AVAILABLE"
    source = meta.get("source", "MOCK_SYNTHETIC" if is_mock else "GROK_DAILY_INTELLIGENCE")
    update = meta.get("date") or "2026-08-24 09:00"
    q = f"{quality:.1f}%" if quality is not None else "—"

    st.markdown(f"""
    <div class="metric-card">
    <b>LAST DATA UPDATE</b> &nbsp; {update} &nbsp;|&nbsp;
    <span class="status-dot {dot}"></span><b>DATA STATUS</b> {label} &nbsp;|&nbsp;
    <b>SOURCE</b> {source} &nbsp;|&nbsp;
    <b>RECORDS</b> {n_records} &nbsp;|&nbsp;
    <b>DATA QUALITY</b> {q}
    </div>
    """, unsafe_allow_html=True)
    if is_mock:
        st.warning("⚠️ DEMO / MOCK DATA — Not real market data. For architecture validation only.")
