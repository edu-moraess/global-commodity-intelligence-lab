"""Macro engine — organize indicators & global regime concept."""

from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd


def build_macro_summary(df: pd.DataFrame) -> Dict[str, Any]:
    if df.empty:
        return {"regime": "UNKNOWN", "components": {}}
    # Placeholder scoring — real scores come from dataset / future models
    components = {
        "Growth": None,
        "Inflation": None,
        "Liquidity": None,
        "Rates": None,
        "USD": None,
        "Commodity Demand": None,
    }
    for ind in df.get("indicator", []):
        name = str(ind).lower()
        if "pmi" in name or "gdp" in name:
            components["Growth"] = "data_present"
        if "cpi" in name or "inflation" in name:
            components["Inflation"] = "data_present"
        if "dxy" in name or "usd" in name:
            components["USD"] = "data_present"
        if "yield" in name or "rate" in name or "fed" in name:
            components["Rates"] = "data_present"
    present = sum(1 for v in components.values() if v is not None)
    regime = "PARTIAL" if present else "UNKNOWN"
    return {"regime": regime, "components": components, "n_indicators": len(df)}
