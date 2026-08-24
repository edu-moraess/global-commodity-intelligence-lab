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
    return pd.DataFrame(
        {"macd": macd_line, "macd_signal": signal_line, "macd_hist": hist},
        index=series.index,
    )


def sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window, min_periods=max(1, window // 2)).mean()


def add_technicals(
    df: pd.DataFrame,
    price_col: str = "spot_price",
    group_col: str = "asset",
) -> pd.DataFrame:
    """
    Attach RSI / MACD / SMAs per asset.

    Uses per-group transform-style assignment to avoid index misalignment
    that can occur with groupby.apply returning MultiIndex frames.
    With insufficient history (e.g. single day) values remain NaN — correct.
    """
    out = df.copy()
    if price_col not in out.columns or group_col not in out.columns:
        return out

    out = out.sort_values([group_col, "date"]).reset_index(drop=True)

    rsi_vals = []
    macd_vals = []
    macd_sig = []
    macd_hist = []
    sma20 = []
    sma50 = []
    sma200 = []

    for _, g in out.groupby(group_col, sort=False):
        s = g[price_col]
        r = rsi(s)
        m = macd(s)
        rsi_vals.append(r)
        macd_vals.append(m["macd"])
        macd_sig.append(m["macd_signal"])
        macd_hist.append(m["macd_hist"])
        sma20.append(sma(s, 20))
        sma50.append(sma(s, 50))
        sma200.append(sma(s, 200))

    out["rsi"] = pd.concat(rsi_vals).values if rsi_vals else None
    out["macd"] = pd.concat(macd_vals).values if macd_vals else None
    out["macd_signal"] = pd.concat(macd_sig).values if macd_sig else None
    out["macd_hist"] = pd.concat(macd_hist).values if macd_hist else None
    out["sma_20"] = pd.concat(sma20).values if sma20 else None
    out["sma_50"] = pd.concat(sma50).values if sma50 else None
    out["sma_200"] = pd.concat(sma200).values if sma200 else None
    return out
