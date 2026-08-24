"""Forecast architecture — placeholders for future models.

Never present synthetic forecasts as real predictions.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional

import pandas as pd


class ForecastSource(str, Enum):
    MODEL_FORECAST = "MODEL_FORECAST"
    GROK_FORECAST = "GROK_FORECAST"
    MARKET_SIGNAL = "MARKET_SIGNAL"


def extract_forecasts(df: pd.DataFrame) -> pd.DataFrame:
    """Pull forecast field if present; otherwise return empty."""
    if "forecast" not in df.columns:
        return pd.DataFrame()
    rows = []
    for _, r in df.iterrows():
        f = r.get("forecast")
        if isinstance(f, dict):
            rows.append({
                "date": r.get("date"),
                "asset": r.get("asset"),
                "source": f.get("source", "UNKNOWN"),
                "direction": f.get("direction"),
                "probability": f.get("probability"),
                "horizon": f.get("horizon"),
            })
    return pd.DataFrame(rows)
