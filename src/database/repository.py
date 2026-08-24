"""Lightweight repository abstraction (file-based for Phase 1)."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

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


class DataRepository:
    """Central access point for UI and engines."""

    def __init__(self, prefer_mock: bool = True):
        self.prefer_mock = prefer_mock
        self._last_meta: dict = {}

    def load_latest(self):
        """Return (commodities_df, macro_df, geo_df, meta)."""
        if self.prefer_mock:
            ds, errors, meta = load_mock()
            if ds is not None:
                self._last_meta = {**meta, "mode": "MOCK", "errors": errors}
                cmd = enrich_commodities(dataset_to_commodities_df(ds))
                return cmd, dataset_to_macro_df(ds), dataset_to_geopolitics_df(ds), self._last_meta

        dates = list_available_raw_dates()
        if not dates:
            # Fallback to mock if no RAW
            ds, errors, meta = load_mock()
            self._last_meta = {**meta, "mode": "MOCK", "errors": errors}
            if ds is None:
                return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), self._last_meta
            cmd = enrich_commodities(dataset_to_commodities_df(ds))
            return cmd, dataset_to_macro_df(ds), dataset_to_geopolitics_df(ds), self._last_meta

        latest = dates[-1]
        ds, errors, meta = load_raw_by_date(latest)
        self._last_meta = {**meta, "mode": "RAW", "date": str(latest), "errors": errors}
        if ds is None:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), self._last_meta
        cmd = enrich_commodities(dataset_to_commodities_df(ds))
        return cmd, dataset_to_macro_df(ds), dataset_to_geopolitics_df(ds), self._last_meta

    @property
    def last_meta(self) -> dict:
        return self._last_meta
