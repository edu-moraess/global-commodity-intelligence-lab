"""
Official Data Contract — Global Commodity Intelligence Lab
===========================================================
Schema for daily structured datasets produced by Grok automation (future)
and consumed by the platform.

Primary format: JSON
Secondary: CSV (tabular export/import)
Historical: Parquet
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator, ConfigDict


class Category(str, Enum):
    ENERGY = "ENERGY"
    METALS = "METALS"
    AGRICULTURE = "AGRICULTURE"
    FERTILIZERS = "FERTILIZERS"
    MACRO = "MACRO"
    GEOPOLITICS = "GEOPOLITICS"


class CurveStructure(str, Enum):
    CONTANGO = "CONTANGO"
    BACKWARDATION = "BACKWARDATION"
    FLAT = "FLAT"
    UNKNOWN = "UNKNOWN"


class VolatilityRegime(str, Enum):
    LOW_VOL = "LOW_VOL"
    NORMAL_VOL = "NORMAL_VOL"
    HIGH_VOL = "HIGH_VOL"
    EXTREME_VOL = "EXTREME_VOL"


class DirectionalBias(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


class CommodityRecord(BaseModel):
    """Single commodity observation for a given date."""

    model_config = ConfigDict(extra="ignore")

    date: date
    asset: str
    ticker: Optional[str] = None
    category: Category
    subcategory: Optional[str] = None
    currency: Optional[str] = "USD"
    unit: Optional[str] = None

    # Prices
    spot_price: Optional[float] = None
    front_future: Optional[float] = None
    future_m1: Optional[float] = None
    future_m2: Optional[float] = None
    future_m3: Optional[float] = None
    future_m6: Optional[float] = None
    future_m12: Optional[float] = None

    # Changes
    daily_change: Optional[float] = None
    weekly_change: Optional[float] = None
    monthly_change: Optional[float] = None

    # Volume & OI
    volume: Optional[float] = None
    open_interest: Optional[float] = None

    # Volatility
    implied_volatility: Optional[float] = None
    historical_volatility: Optional[float] = None

    # Technical
    z_score: Optional[float] = None
    rsi: Optional[float] = None
    macd: Optional[float] = None
    moving_average_20: Optional[float] = None
    moving_average_50: Optional[float] = None
    moving_average_200: Optional[float] = None
    momentum: Optional[float] = None

    # Structure & regime
    curve_structure: Optional[CurveStructure] = None
    seasonality_score: Optional[float] = None
    volatility_regime: Optional[VolatilityRegime] = None

    # Directional
    directional_probability: Optional[float] = Field(None, ge=0.0, le=1.0)
    directional_bias: Optional[DirectionalBias] = None

    # Risk scores (0-100 or normalized)
    supply_risk: Optional[float] = None
    demand_risk: Optional[float] = None
    macro_score: Optional[float] = None
    geopolitical_score: Optional[float] = None
    sentiment_score: Optional[float] = None

    # Positioning
    cot_net_position: Optional[float] = None
    etf_flow: Optional[float] = None

    # Forecast placeholder
    forecast: Optional[Dict[str, Any]] = None

    # Provenance
    source: Optional[str] = None
    source_timestamp: Optional[datetime] = None

    @field_validator("spot_price", "front_future", "future_m1", "future_m2",
                     "future_m3", "future_m6", "future_m12", mode="before")
    @classmethod
    def non_negative_price(cls, v: Any) -> Any:
        if v is not None and isinstance(v, (int, float)) and v < 0:
            raise ValueError("Price fields cannot be negative")
        return v


class MacroRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    date: date
    indicator: str
    region: Optional[str] = None
    value: Optional[float] = None
    previous: Optional[float] = None
    change: Optional[float] = None
    unit: Optional[str] = None
    source: Optional[str] = None
    source_timestamp: Optional[datetime] = None


class GeopoliticalEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")

    event_id: str
    date: date
    region: Optional[str] = None
    country: Optional[str] = None
    event_type: Optional[str] = None
    severity: Optional[float] = Field(None, ge=0.0, le=10.0)
    supply_impact: Optional[float] = None
    demand_impact: Optional[float] = None
    inflation_impact: Optional[float] = None
    growth_impact: Optional[float] = None
    affected_commodities: Optional[List[str]] = None
    summary: Optional[str] = None
    source: Optional[str] = None


class DailyDataset(BaseModel):
    """Root object for a daily intelligence dump."""

    model_config = ConfigDict(extra="ignore")

    dataset_date: date
    generated_at: Optional[datetime] = None
    source: str = "GROK_DAILY_INTELLIGENCE"
    version: str = "1.0"
    commodities: List[CommodityRecord] = Field(default_factory=list)
    macro: List[MacroRecord] = Field(default_factory=list)
    geopolitics: List[GeopoliticalEvent] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None


def validate_dataset(data: Dict[str, Any]) -> DailyDataset:
    """Validate and parse a raw dict into the official schema."""
    return DailyDataset.model_validate(data)


def schema_json() -> Dict[str, Any]:
    """Export JSON Schema for documentation / external producers."""
    return DailyDataset.model_json_schema()
