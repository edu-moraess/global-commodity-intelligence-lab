"""Correlation matrix engine."""

from __future__ import annotations

import pandas as pd


def correlation_matrix(df: pd.DataFrame, price_col: str = "spot_price",
                       asset_col: str = "asset", method: str = "pearson",
                       min_periods: int = 5) -> pd.DataFrame:
    """
    Build pairwise correlation of returns (or levels) across assets.
    Expects long format with date + asset + price.
    """
    if df.empty or price_col not in df.columns:
        return pd.DataFrame()
    pivot = df.pivot_table(index="date", columns=asset_col, values=price_col, aggfunc="last")
    rets = pivot.pct_change().dropna(how="all")
    if rets.empty:
        return pd.DataFrame()
    return rets.corr(method=method, min_periods=min_periods)
