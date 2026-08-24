"""Technical indicators: RSI, MACD, SMAs."""

from __future__ import annotations

import pandas as pd


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, pd.NA)
    return 100 - (100 / (1 + rs))


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return pd.DataFrame({"macd": macd_line, "macd_signal": signal_line, "macd_hist": hist})


def sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window, min_periods=max(1, window // 2)).mean()


def add_technicals(df: pd.DataFrame, price_col: str = "spot_price",
                   group_col: str = "asset") -> pd.DataFrame:
    out = df.copy()
    if price_col not in out.columns:
        return out
    out = out.sort_values([group_col, "date"])

    def _tech(s: pd.Series) -> pd.DataFrame:
        r = rsi(s)
        m = macd(s)
        return pd.DataFrame({
            "rsi": r,
            "macd": m["macd"],
            "macd_signal": m["macd_signal"],
            "macd_hist": m["macd_hist"],
            "sma_20": sma(s, 20),
            "sma_50": sma(s, 50),
            "sma_200": sma(s, 200),
        }, index=s.index)

    tech = out.groupby(group_col, group_keys=False)[price_col].apply(
        lambda s: _tech(s)
    )
    # Align indices
    for col in ["rsi", "macd", "macd_signal", "macd_hist", "sma_20", "sma_50", "sma_200"]:
        if col in tech.columns:
            out[col] = tech[col].values if len(tech) == len(out) else None
    return out
