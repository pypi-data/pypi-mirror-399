from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Profile:
    n_rows: int
    n_cols: int
    missing_by_col: Dict[str, int]
    dtype_by_col: Dict[str, str]
    numeric_summary: Dict[str, Dict[str, Any]]
    categorical_top: Dict[str, List[tuple[str, int]]]
    corr: pd.DataFrame | None


def build_profile(df: pd.DataFrame, numeric_cols: list[str], categorical_cols: list[str]) -> Profile:
    missing_by_col = {c: int(df[c].isna().sum()) for c in df.columns}
    dtype_by_col = {c: str(df[c].dtype) for c in df.columns}

    numeric_summary: Dict[str, Dict[str, Any]] = {}
    for c in numeric_cols:
        s = pd.to_numeric(df[c], errors="coerce")
        if int(s.count()) == 0:
            numeric_summary[c] = {"count": 0}
            continue
        numeric_summary[c] = {
            "count": int(s.count()),
            "mean": float(np.nanmean(s.values)),
            "std": float(np.nanstd(s.values)),
            "min": float(np.nanmin(s.values)),
            "p25": float(np.nanpercentile(s.values, 25)),
            "median": float(np.nanmedian(s.values)),
            "p75": float(np.nanpercentile(s.values, 75)),
            "max": float(np.nanmax(s.values)),
        }

    categorical_top: Dict[str, List[tuple[str, int]]] = {}
    for c in categorical_cols:
        vc = df[c].astype("object").fillna("NA").value_counts().head(10)
        categorical_top[c] = [(str(k), int(v)) for k, v in vc.items()]

    corr = None
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr(numeric_only=True)

    return Profile(
        n_rows=int(df.shape[0]),
        n_cols=int(df.shape[1]),
        missing_by_col=missing_by_col,
        dtype_by_col=dtype_by_col,
        numeric_summary=numeric_summary,
        categorical_top=categorical_top,
        corr=corr,
    )