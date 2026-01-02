from __future__ import annotations

import os
from typing import Tuple, List

import pandas as pd


def load_table(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    lower = path.lower()
    if lower.endswith(".csv"):
        return pd.read_csv(path)
    if lower.endswith(".xlsx") or lower.endswith(".xls"):
        return pd.read_excel(path)
    raise ValueError("Unsupported file format. Use .csv, .xlsx, or .xls")


def infer_column_types(df: pd.DataFrame) -> Tuple[List[str], List[str], List[str]]:
    numeric_cols: list[str] = []
    categorical_cols: list[str] = []
    datetime_cols: list[str] = []

    for c in df.columns:
        s = df[c]
        if pd.api.types.is_datetime64_any_dtype(s):
            datetime_cols.append(c)
        elif pd.api.types.is_numeric_dtype(s):
            numeric_cols.append(c)
        else:
            categorical_cols.append(c)

    return numeric_cols, categorical_cols, datetime_cols


def safe_nunique(series: pd.Series) -> int:
    try:
        return int(series.nunique(dropna=True))
    except Exception:
        return 0