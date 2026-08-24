"""Data quality validation layer."""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Tuple

import pandas as pd

from .schema import Category, DailyDataset, validate_dataset


REQUIRED_COMMODITY_FIELDS = ["date", "asset", "category"]
VALID_CATEGORIES = {c.value for c in Category}


def validate_raw_payload(payload: Dict[str, Any]) -> Tuple[bool, List[str], DailyDataset | None]:
    """
    Validate a raw JSON payload against the official schema.
    Returns (ok, list_of_errors, parsed_dataset_or_None).
    """
    errors: List[str] = []
    try:
        ds = validate_dataset(payload)
    except Exception as e:
        return False, [f"Schema validation failed: {e}"], None

    if not ds.commodities and not ds.macro and not ds.geopolitics:
        errors.append("Dataset contains no commodities, macro or geopolitics records")

    for i, rec in enumerate(ds.commodities):
        if rec.spot_price is not None and rec.spot_price < 0:
            errors.append(f"commodities[{i}] ({rec.asset}): negative spot_price")
        if rec.category.value not in VALID_CATEGORIES:
            errors.append(f"commodities[{i}] ({rec.asset}): invalid category {rec.category}")

    # Duplicate check by (date, asset)
    seen = set()
    for i, rec in enumerate(ds.commodities):
        key = (rec.date.isoformat(), rec.asset)
        if key in seen:
            errors.append(f"Duplicate commodity record: {key}")
        seen.add(key)

    ok = len(errors) == 0
    return ok, errors, ds


def quality_report(df: pd.DataFrame, required: List[str] | None = None) -> Dict[str, Any]:
    """Generate a simple data quality report for a commodities DataFrame."""
    required = required or REQUIRED_COMMODITY_FIELDS
    total = len(df)
    if total == 0:
        return {"records": 0, "completeness": 0.0, "issues": ["empty dataframe"]}

    issues: List[str] = []
    missing = {}
    for col in required:
        if col not in df.columns:
            issues.append(f"missing required column: {col}")
            missing[col] = total
        else:
            n_miss = int(df[col].isna().sum())
            if n_miss:
                missing[col] = n_miss
                issues.append(f"{col}: {n_miss} missing values")

    if "spot_price" in df.columns:
        neg = int((df["spot_price"] < 0).sum())
        if neg:
            issues.append(f"spot_price: {neg} negative values")

    if "date" in df.columns:
        try:
            pd.to_datetime(df["date"])
        except Exception:
            issues.append("date column contains invalid dates")

    completeness = 1.0 - (sum(missing.values()) / (total * max(len(required), 1)))
    return {
        "records": total,
        "completeness": round(max(0.0, completeness) * 100, 2),
        "missing": missing,
        "issues": issues,
    }
