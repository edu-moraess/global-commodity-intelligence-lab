"""Momentum features."""

from __future__ import annotations

import pandas as pd

from .returns import simple_return


def momentum_score(series: pd.Series, lookbacks: list[int] | None = None) -> pd.Series:
    lookbacks = lookbacks or [5, 21, 63]
    scores = []
    for lb in lookbacks:
        scores.append(simple_return(series, periods=lb))
    # Average of available lookbacks
    stacked = pd.concat(scores, axis=1)
    return stacked.mean(axis=1)


def add_momentum(df: pd.DataFrame, price_col: str = "spot_price",
                 group_col: str = "asset") -> pd.DataFrame:
    out = df.copy()
    if price_col not in out.columns:
        return out
    out = out.sort_values([group_col, "date"])
    out["momentum"] = out.groupby(group_col)[price_col].transform(
        lambda s: momentum_score(s)
    )
    return out
