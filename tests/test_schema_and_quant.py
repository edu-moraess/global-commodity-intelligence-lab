"""Core unit tests — schema, validation, quant engines."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
MOCK = ROOT / "data" / "mock" / "mock_daily.json"

from src.ingestion.schema import validate_dataset, Category
from src.ingestion.validator import validate_raw_payload, quality_report
from src.ingestion.loader import load_mock, dataset_to_commodities_df
from src.quantitative.returns import simple_return, compute_returns
from src.quantitative.zscore import rolling_zscore
from src.quantitative.technical import rsi, macd
from src.quantitative.volatility import classify_vol_regime, rolling_volatility
from src.quantitative.curve import classify_curve
from src.quantitative.correlation import correlation_matrix
from src.processing.transformations import enrich_commodities


def test_mock_exists():
    assert MOCK.exists(), "Mock dataset missing"


def test_schema_validation():
    with open(MOCK) as f:
        payload = json.load(f)
    ok, errors, ds = validate_raw_payload(payload)
    assert ok, errors
    assert ds is not None
    assert len(ds.commodities) >= 20
    assert any(c.category == Category.ENERGY for c in ds.commodities)


def test_quality_report():
    ds, _, _ = load_mock()
    df = dataset_to_commodities_df(ds)
    report = quality_report(df)
    assert report["records"] > 0
    assert report["completeness"] > 50


def test_returns():
    s = pd.Series([100.0, 102.0, 101.0, 105.0])
    r = simple_return(s)
    assert abs(r.iloc[1] - 0.02) < 1e-9


def test_zscore():
    s = pd.Series(range(30), dtype=float)
    z = rolling_zscore(s, window=10)
    assert z.notna().sum() > 0


def test_rsi():
    s = pd.Series([i + (i % 3) for i in range(50)], dtype=float)
    r = rsi(s)
    assert r.notna().sum() > 0
    assert r.dropna().between(0, 100).all()


def test_macd():
    s = pd.Series(range(60), dtype=float)
    m = macd(s)
    assert "macd" in m.columns


def test_vol_regime():
    assert classify_vol_regime(0.1) == "LOW_VOL"
    assert classify_vol_regime(0.9) == "EXTREME_VOL"


def test_curve():
    assert classify_curve(100, 102) == "CONTANGO"
    assert classify_curve(100, 98) == "BACKWARDATION"
    assert classify_curve(100, 100.05) == "FLAT"
    assert classify_curve(None, 100) == "UNKNOWN"


def test_enrich_pipeline():
    ds, _, _ = load_mock()
    df = dataset_to_commodities_df(ds)
    enriched = enrich_commodities(df)
    assert not enriched.empty
    assert "curve_structure" in enriched.columns


def test_correlation_empty_ok():
    # Single day → empty or near-empty corr is acceptable
    ds, _, _ = load_mock()
    df = dataset_to_commodities_df(ds)
    corr = correlation_matrix(df)
    # just ensure it does not raise
    assert isinstance(corr, pd.DataFrame)
