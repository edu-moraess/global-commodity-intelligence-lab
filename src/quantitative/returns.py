"""Return calculations."""

from __future__ import annotations

import numpy as np
import pandas as pd


def simple_return(series: pd.Series, periods: int = 1) -> pd.Series:
    return series.pct_change(periods=periods)


def log_return(series: pd.Series, periods: int = 1) -> pd.Series:
    return np.log(series / series.shift(periods))


def rolling_return(series: pd.Series, window: int) -> pd.Series:
    return series.pct_change(periods=window)


def compute_returns(df: pd.DataFrame, price_col: str = "spot_price",
                    group_col: str = "asset") -> pd.DataFrame:
    """Add 1D / 5D / 21D returns to a long-format commodities frame."""
    out = df.copy()
    if price_col not in out.columns:
        return out
    out = out.sort_values([group_col, "date"])
    for w, name in [(1, "ret_1d"), (5, "ret_5d"), (21, "ret_21d")]:
        out[name] = out.groupby(group_col)[price_col].transform(
            lambda s: simple_return(s, periods=w)
        )
    return out
