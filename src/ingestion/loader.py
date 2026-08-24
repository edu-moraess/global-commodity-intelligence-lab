"""Ingestion loader — RAW → memory / processed."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from .schema import DailyDataset, validate_dataset
from .validator import quality_report, validate_raw_payload

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_MOCK = PROJECT_ROOT / "data" / "mock"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"


def _date_path(d: date) -> Path:
    return DATA_RAW / f"{d.year:04d}" / f"{d.month:02d}" / f"{d.isoformat()}.json"


def load_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_raw_by_date(d: date) -> Tuple[Optional[DailyDataset], List[str], Dict[str, Any]]:
    """Load immutable RAW file for a given date."""
    path = _date_path(d)
    if not path.exists():
        return None, [f"RAW file not found: {path}"], {}
    payload = load_json(path)
    ok, errors, ds = validate_raw_payload(payload)
    meta = {"path": str(path), "ok": ok, "errors": errors}
    return ds, errors, meta


def load_mock() -> Tuple[Optional[DailyDataset], List[str], Dict[str, Any]]:
    """Load synthetic mock dataset (never treated as live)."""
    path = DATA_MOCK / "mock_daily.json"
    if not path.exists():
        return None, [f"Mock file not found: {path}"], {}
    payload = load_json(path)
    ok, errors, ds = validate_raw_payload(payload)
    meta = {"path": str(path), "ok": ok, "errors": errors, "mode": "MOCK"}
    return ds, errors, meta


def dataset_to_commodities_df(ds: DailyDataset) -> pd.DataFrame:
    records = [r.model_dump(mode="json") for r in ds.commodities]
    df = pd.DataFrame(records)
    if not df.empty and "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"]).dt.date
    return df


def dataset_to_macro_df(ds: DailyDataset) -> pd.DataFrame:
    records = [r.model_dump(mode="json") for r in ds.macro]
    return pd.DataFrame(records)


def dataset_to_geopolitics_df(ds: DailyDataset) -> pd.DataFrame:
    records = [r.model_dump(mode="json") for r in ds.geopolitics]
    return pd.DataFrame(records)


def save_processed(df: pd.DataFrame, name: str) -> Path:
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    path = DATA_PROCESSED / f"{name}.parquet"
    df.to_parquet(path, index=False)
    return path


def list_available_raw_dates() -> List[date]:
    dates = []
    if not DATA_RAW.exists():
        return dates
    for p in DATA_RAW.rglob("*.json"):
        try:
            dates.append(date.fromisoformat(p.stem))
        except ValueError:
            continue
    return sorted(dates)
