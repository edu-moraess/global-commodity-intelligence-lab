"""Pipeline transformations combining quant engines."""

from __future__ import annotations

import pandas as pd

from src.quantitative.returns import compute_returns
from src.quantitative.volatility import add_volatility_features
from src.quantitative.zscore import add_zscore
from src.quantitative.technical import add_technicals
from src.quantitative.momentum import add_momentum
from src.quantitative.curve import add_curve_structure
from src.processing.normalization import normalize_categories, ensure_date, drop_duplicates_key


def enrich_commodities(df: pd.DataFrame) -> pd.DataFrame:
    """Full quant enrichment pipeline for a commodities DataFrame."""
    if df.empty:
        return df
    out = ensure_date(df)
    out = normalize_categories(out)
    out = drop_duplicates_key(out)
    out = compute_returns(out)
    out = add_zscore(out)
    out = add_volatility_features(out)
    out = add_technicals(out)
    out = add_momentum(out)
    out = add_curve_structure(out)
    return out
