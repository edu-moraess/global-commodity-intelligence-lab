"""Futures curve structure classification."""

from __future__ import annotations

from typing import Optional

import pandas as pd


def classify_curve(front: Optional[float], m1: Optional[float],
                   m2: Optional[float] = None, threshold: float = 0.001) -> str:
    """
    CONTANGO: longer-dated > front
    BACKWARDATION: longer-dated < front
    FLAT: approximately equal
    UNKNOWN: insufficient data
    """
    if front is None or m1 is None:
        return "UNKNOWN"
    if front == 0:
        return "UNKNOWN"
    spread = (m1 - front) / abs(front)
    if abs(spread) < threshold:
        return "FLAT"
    if spread > 0:
        return "CONTANGO"
    return "BACKWARDATION"


def add_curve_structure(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "front_future" not in out.columns and "spot_price" in out.columns:
        out["front_future"] = out["spot_price"]
    front_col = "front_future" if "front_future" in out.columns else "spot_price"
    m1_col = "future_m1" if "future_m1" in out.columns else None
    if m1_col is None:
        out["curve_structure"] = "UNKNOWN"
        return out
    out["curve_structure"] = out.apply(
        lambda r: classify_curve(r.get(front_col), r.get(m1_col)), axis=1
    )
    return out
