"""Volatility & regime classification."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .returns import simple_return


def rolling_volatility(series: pd.Series, window: int = 21, annualize: bool = True) -> pd.Series:
    ret = simple_return(series)
    vol = ret.rolling(window=window).std()
    if annualize:
        vol = vol * np.sqrt(252)
    return vol


def volatility_percentile(series: pd.Series, window: int = 252) -> pd.Series:
    return series.rolling(window=window, min_periods=max(20, window // 5)).apply(
        lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False
    )


def classify_vol_regime(vol: float, percentiles: dict | None = None) -> str:
    """
    Classify into LOW_VOL / NORMAL_VOL / HIGH_VOL / EXTREME_VOL
    using percentile thresholds (default 20/50/80).
    """
    if vol is None or (isinstance(vol, float) and np.isnan(vol)):
        return "UNKNOWN"
    p = percentiles or {"low": 0.20, "normal": 0.50, "high": 0.80}
    # Here vol is already a percentile rank 0-1 if coming from volatility_percentile
    if vol <= p["low"]:
        return "LOW_VOL"
    if vol <= p["normal"]:
        return "NORMAL_VOL"
    if vol <= p["high"]:
        return "HIGH_VOL"
    return "EXTREME_VOL"


def add_volatility_features(df: pd.DataFrame, price_col: str = "spot_price",
                            group_col: str = "asset", window: int = 21) -> pd.DataFrame:
    out = df.copy()
    if price_col not in out.columns:
        return out
    out = out.sort_values([group_col, "date"])
    out["hist_vol"] = out.groupby(group_col)[price_col].transform(
        lambda s: rolling_volatility(s, window=window)
    )
    out["vol_pctile"] = out.groupby(group_col)["hist_vol"].transform(
        lambda s: volatility_percentile(s, window=min(252, max(len(s), 30)))
    )
    out["volatility_regime"] = out["vol_pctile"].apply(classify_vol_regime)
    return out
