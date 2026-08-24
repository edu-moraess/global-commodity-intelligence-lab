"""Geopolitical risk engine."""

from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd


def geopolitical_risk_score(events: pd.DataFrame) -> Dict[str, Any]:
    """Aggregate severity into a simple 0-100 risk score."""
    if events.empty or "severity" not in events.columns:
        return {"score": None, "n_events": 0, "by_region": {}}
    sev = events["severity"].dropna()
    if sev.empty:
        return {"score": None, "n_events": len(events), "by_region": {}}
    # Normalize average severity (0-10) to 0-100
    score = float(sev.mean() * 10)
    by_region = {}
    if "region" in events.columns:
        by_region = events.groupby("region")["severity"].mean().mul(10).to_dict()
    return {
        "score": round(score, 1),
        "n_events": len(events),
        "by_region": {k: round(v, 1) for k, v in by_region.items()},
    }
