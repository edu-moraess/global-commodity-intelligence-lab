"""Plotly chart helpers."""

from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


TEMPLATE = "plotly_dark"


def price_bar(df: pd.DataFrame, title: str = "Spot Prices"):
    if df.empty or "spot_price" not in df.columns:
        return go.Figure()
    fig = px.bar(df, x="asset", y="spot_price", color="category",
                 title=title, template=TEMPLATE)
    fig.update_layout(height=400, margin=dict(t=40, b=20))
    return fig


def returns_heatmap(df: pd.DataFrame, col: str = "daily_change"):
    if df.empty or col not in df.columns:
        return go.Figure()
    pivot = df.pivot_table(index="category", columns="asset", values=col, aggfunc="last")
    fig = px.imshow(pivot, text_auto=".2%", aspect="auto", color_continuous_scale="RdYlGn",
                    title=f"Heatmap — {col}", template=TEMPLATE)
    fig.update_layout(height=350)
    return fig


def correlation_heatmap(corr: pd.DataFrame):
    if corr.empty:
        return go.Figure()
    fig = px.imshow(corr, text_auto=".2f", aspect="auto",
                    color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
                    title="Correlation Matrix (returns)", template=TEMPLATE)
    fig.update_layout(height=500)
    return fig


def ranking_bar(df: pd.DataFrame, col: str = "daily_change", top: int = 10):
    if df.empty or col not in df.columns:
        return go.Figure()
    tmp = df.dropna(subset=[col]).sort_values(col, ascending=True).tail(top)
    fig = px.bar(tmp, x=col, y="asset", orientation="h", color=col,
                 color_continuous_scale="RdYlGn", title=f"Top movers — {col}",
                 template=TEMPLATE)
    fig.update_layout(height=400)
    return fig
