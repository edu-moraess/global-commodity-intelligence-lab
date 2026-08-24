"""Seasonality analysis (requires sufficient history)."""

from __future__ import annotations

import pandas as pd


def monthly_seasonality(df: pd.DataFrame, price_col: str = "spot_price",
                        asset_col: str = "asset") -> pd.DataFrame:
    """
    Average monthly return by asset. Requires multi-year history ideally.
    Returns empty frame if insufficient data.
    """
    if df.empty or price_col not in df.columns:
        return pd.DataFrame()
    tmp = df.copy()
    tmp["date"] = pd.to_datetime(tmp["date"])
    tmp["month"] = tmp["date"].dt.month
    tmp = tmp.sort_values([asset_col, "date"])
    tmp["ret"] = tmp.groupby(asset_col)[price_col].pct_change()
    if tmp["ret"].notna().sum() < 30:
        return pd.DataFrame()
    return tmp.groupby([asset_col, "month"])["ret"].mean().unstack(fill_value=0)
