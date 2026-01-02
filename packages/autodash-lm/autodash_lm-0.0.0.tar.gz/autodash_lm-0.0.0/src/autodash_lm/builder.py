from __future__ import annotations

from typing import List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .theme import Theme
from .utils import safe_nunique


def fig_missingness(df: pd.DataFrame, theme: Theme) -> go.Figure:
    missing = df.isna().sum().sort_values(ascending=False)
    fig = px.bar(
        x=missing.index.astype(str),
        y=missing.values,
        title="Missing values by column",
        labels={"x": "column", "y": "missing"},
    )
    fig.update_layout(template=theme.plotly_template())
    return fig


def fig_numeric_distribution(df: pd.DataFrame, col: str, theme: Theme) -> go.Figure:
    s = pd.to_numeric(df[col], errors="coerce")
    fig = px.histogram(s, nbins=40, title=f"Distribution: {col}", labels={"value": col})
    fig.update_layout(template=theme.plotly_template())
    return fig


def fig_categorical_counts(df: pd.DataFrame, col: str, theme: Theme) -> go.Figure:
    s = df[col].astype("object").fillna("NA")
    vc = s.value_counts().head(30)
    fig = px.bar(
        x=vc.index.astype(str),
        y=vc.values,
        title=f"Top categories: {col}",
        labels={"x": col, "y": "count"},
    )
    fig.update_layout(template=theme.plotly_template())
    return fig


def fig_corr_heatmap(df: pd.DataFrame, numeric_cols: List[str], theme: Theme) -> go.Figure:
    corr = df[numeric_cols].corr(numeric_only=True)
    fig = go.Figure(
        data=go.Heatmap(
            z=corr.values,
            x=corr.columns.astype(str),
            y=corr.index.astype(str),
            colorscale="RdBu",
            zmin=-1,
            zmax=1,
            colorbar=dict(title="corr"),
        )
    )
    fig.update_layout(title="Correlation heatmap", template=theme.plotly_template())
    return fig


def pick_interesting_numeric(df: pd.DataFrame, numeric_cols: List[str]) -> List[str]:
    scored = []
    for c in numeric_cols:
        s = pd.to_numeric(df[c], errors="coerce")
        if s.count() < max(10, int(0.1 * len(df))):
            continue
        var = float(s.var(skipna=True)) if s.count() else 0.0
        scored.append((var, c))
    scored.sort(reverse=True)
    return [c for _, c in scored[:6]]


def pick_interesting_categorical(df: pd.DataFrame, cat_cols: List[str]) -> List[str]:
    scored = []
    for c in cat_cols:
        n = safe_nunique(df[c])
        if n <= 1:
            continue
        if n <= 30:
            score = 10
        elif n <= 100:
            score = 4
        else:
            score = 0
        scored.append((score, c))
    scored.sort(reverse=True)
    return [c for _, c in scored[:6]]