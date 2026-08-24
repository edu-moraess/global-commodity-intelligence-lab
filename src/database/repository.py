"""Lightweight repository abstraction (file-based).

Data modes (config.toml [app].data_mode):
  auto — latest valid RAW if present, else MOCK
  mock — always MOCK
  raw  — RAW only; clear error meta if none
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore

from src.ingestion.loader import (
    load_mock,
    load_raw_by_date,
    dataset_to_commodities_df,
    dataset_to_macro_df,
    dataset_to_geopolitics_df,
    list_available_raw_dates,
)
from src.processing.transformations import enrich_commodities
from src.processing.historical import load_historical, append_historical
from src.ingestion.schema import DailyDataset

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config.toml"

VALID_MODES = {"auto", "mock", "raw"}


def _read_data_mode() -> str:
    """Read data_mode from config.toml; default auto."""
    if not CONFIG_PATH.exists():
        return "auto"
    try:
        with open(CONFIG_PATH, "rb") as f:
            cfg = tomllib.load(f)
        mode = str(cfg.get("app", {}).get("data_mode", "auto")).strip().lower()
        return mode if mode in VALID_MODES else "auto"
    except Exception:
        return "auto"


def _pack(
    ds: Optional[DailyDataset],
    errors: List[str],
    meta: Dict[str, Any],
    mode: str,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
    if ds is None:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), meta
    cmd = enrich_commodities(dataset_to_commodities_df(ds))
    return cmd, dataset_to_macro_df(ds), dataset_to_geopolitics_df(ds), meta


class DataRepository:
    """Central access point for UI and engines."""

    def __init__(self, data_mode: Optional[str] = None):
        """
        data_mode: override config (auto|mock|raw). None → read config.toml.
        """
        self.data_mode = (data_mode or _read_data_mode()).lower()
        if self.data_mode not in VALID_MODES:
            self.data_mode = "auto"
        self._last_meta: Dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_latest(
        self,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        """Return (commodities_df, macro_df, geo_df, meta)."""
        if self.data_mode == "mock":
            return self._load_mock()

        if self.data_mode == "raw":
            return self._load_raw_strict()

        # auto
        return self._load_auto()

    def load_historical_df(self, name: str = "commodities_history") -> pd.DataFrame:
        return load_historical(name)

    @property
    def last_meta(self) -> Dict[str, Any]:
        return self._last_meta

    # ------------------------------------------------------------------
    # Internal strategies
    # ------------------------------------------------------------------

    def _load_mock(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        ds, errors, meta = load_mock()
        meta = {
            **meta,
            "mode": "MOCK",
            "data_mode_config": self.data_mode,
            "source": meta.get("source") or "MOCK_SYNTHETIC",
            "errors": errors,
            "ok": ds is not None and not errors,
        }
        if ds is not None:
            meta["date"] = str(ds.dataset_date)
            meta["source"] = ds.source if ds.source else "MOCK_SYNTHETIC"
        self._last_meta = meta
        return _pack(ds, errors, meta, "MOCK")

    def _load_raw_strict(
        self,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        dates = list_available_raw_dates()
        if not dates:
            meta = {
                "mode": "RAW",
                "data_mode_config": "raw",
                "ok": False,
                "errors": ["No RAW datasets found under data/raw/"],
                "source": None,
                "date": None,
            }
            self._last_meta = meta
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), meta

        # Walk from newest to oldest until a valid payload is found
        for d in reversed(dates):
            ds, errors, meta = load_raw_by_date(d)
            if ds is not None and not errors:
                meta = {
                    **meta,
                    "mode": "RAW",
                    "data_mode_config": "raw",
                    "date": str(d),
                    "source": ds.source or "GROK_DAILY_INTELLIGENCE",
                    "errors": errors,
                    "ok": True,
                }
                self._last_meta = meta
                return _pack(ds, errors, meta, "RAW")

        meta = {
            "mode": "RAW",
            "data_mode_config": "raw",
            "ok": False,
            "errors": ["RAW files exist but none passed validation"],
            "source": None,
            "date": str(dates[-1]) if dates else None,
        }
        self._last_meta = meta
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), meta

    def _load_auto(
        self,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        dates = list_available_raw_dates()
        for d in reversed(dates):
            ds, errors, meta = load_raw_by_date(d)
            if ds is not None and not errors:
                meta = {
                    **meta,
                    "mode": "RAW",
                    "data_mode_config": "auto",
                    "date": str(d),
                    "source": ds.source or "GROK_DAILY_INTELLIGENCE",
                    "errors": errors,
                    "ok": True,
                }
                self._last_meta = meta
                return _pack(ds, errors, meta, "RAW")

        # Fallback MOCK — never mix with partial RAW
        return self._load_mock()


def get_repository(data_mode: Optional[str] = None) -> DataRepository:
    """Factory used by Streamlit pages — single entry point."""
    return DataRepository(data_mode=data_mode)
