"""Historical layer — non-destructive append / consolidate."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HIST_DIR = PROJECT_ROOT / "data" / "historical"


def load_historical(name: str = "commodities_history") -> pd.DataFrame:
    path = HIST_DIR / f"{name}.parquet"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


def append_historical(df: pd.DataFrame, name: str = "commodities_history",
                      key_cols: list[str] | None = None) -> Path:
    """
    Append new observations without destroying existing history.
    Deduplicates on key_cols (default date + asset).
    """
    key_cols = key_cols or ["date", "asset"]
    HIST_DIR.mkdir(parents=True, exist_ok=True)
    path = HIST_DIR / f"{name}.parquet"
    existing = load_historical(name)
    if existing.empty:
        combined = df.copy()
    else:
        combined = pd.concat([existing, df], ignore_index=True)
        present = [k for k in key_cols if k in combined.columns]
        if present:
            combined = combined.drop_duplicates(subset=present, keep="last")
    combined.to_parquet(path, index=False)
    return path


def slice_history(df: pd.DataFrame, days: Optional[int] = None) -> pd.DataFrame:
    if df.empty or days is None or "date" not in df.columns:
        return df
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    cutoff = df["date"].max() - pd.Timedelta(days=days)
    return df[df["date"] >= cutoff]
