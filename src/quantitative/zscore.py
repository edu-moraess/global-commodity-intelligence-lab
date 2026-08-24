"""Z-score calculation."""

from __future__ import annotations

import pandas as pd


def rolling_zscore(series: pd.Series, window: int = 20) -> pd.Series:
    mean = series.rolling(window=window, min_periods=max(5, window // 4)).mean()
    std = series.rolling(window=window, min_periods=max(5, window // 4)).std()
    return (series - mean) / std.replace(0, pd.NA)


def add_zscore(df: pd.DataFrame, price_col: str = "spot_price",
               group_col: str = "asset", window: int = 20) -> pd.DataFrame:
    out = df.copy()
    if price_col not in out.columns:
        return out
    out = out.sort_values([group_col, "date"])
    out["z_score"] = out.groupby(group_col)[price_col].transform(
        lambda s: rolling_zscore(s, window=window)
    )
    return out
