"""Normalization & cleaning."""

from __future__ import annotations

import pandas as pd


def normalize_categories(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "category" in out.columns:
        out["category"] = out["category"].astype(str).str.upper().str.strip()
    return out


def ensure_date(df: pd.DataFrame, col: str = "date") -> pd.DataFrame:
    out = df.copy()
    if col in out.columns:
        out[col] = pd.to_datetime(out[col], errors="coerce").dt.date
    return out


def drop_duplicates_key(df: pd.DataFrame, keys: list[str] | None = None) -> pd.DataFrame:
    keys = keys or ["date", "asset"]
    present = [k for k in keys if k in df.columns]
    if not present:
        return df
    return df.drop_duplicates(subset=present, keep="last")
