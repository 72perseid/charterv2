"""
The dataset profile (SPEC §6.2): what the dataset page shows and, filtered by
privacy level, what the model sees. Plain JSON-serialisable Python only.
"""

from __future__ import annotations

import math
from typing import Any

import pandas as pd

TOP_VALUES = 5
SAMPLE_ROWS = 10
SAMPLE_SEED = 20260907


def _py(value: Any) -> Any:
    """numpy/pandas scalar -> JSON-safe Python."""
    if value is None or value is pd.NA or value is pd.NaT:
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


def column_profile(name: str, original: str, series: pd.Series, kind: str) -> dict:
    non_null = series.dropna()
    out: dict[str, Any] = {
        "name": name,
        "original_name": original,
        "type": kind,
        "null_count": int(series.isna().sum()),
        "distinct_count": int(non_null.nunique()),
    }
    if non_null.empty:
        return out
    if kind in {"integer", "number"}:
        out.update(
            min=_py(non_null.min()),
            max=_py(non_null.max()),
            mean=_py(round(float(non_null.mean()), 4)),
            median=_py(non_null.median()),
        )
    elif kind == "date":
        out.update(min=_py(non_null.min()), max=_py(non_null.max()))
    elif kind == "boolean":
        out["true_count"] = int(non_null.sum())
    else:
        out["max_length"] = int(non_null.astype(str).str.len().max())
        # An all-unique text column is an identifier: its "top values" would be
        # five arbitrary IDs, useless for charting and needlessly revealing.
        if out["distinct_count"] < len(non_null):
            counts = non_null.value_counts().head(TOP_VALUES)
            out["top_values"] = [{"value": str(v), "count": int(c)} for v, c in counts.items()]
    return out


def build_profile(frame: pd.DataFrame, parse_options: dict) -> dict:
    types: dict[str, str] = parse_options["types"]
    originals: list[str] = parse_options["original_columns"]
    return {
        "row_count": int(len(frame)),
        "column_count": int(len(frame.columns)),
        "columns": [
            column_profile(name, originals[i], frame[name], types[name])
            for i, name in enumerate(frame.columns)
        ],
    }


def rows_as_records(frame: pd.DataFrame) -> list[dict]:
    """Rows for the API and for vega: JSON-safe, dates as ISO strings, nulls as null."""
    records = []
    for row in frame.itertuples(index=False, name=None):
        records.append({col: _py(v) for col, v in zip(frame.columns, row, strict=True)})
    return records


def sample_rows(frame: pd.DataFrame) -> list[dict]:
    n = min(SAMPLE_ROWS, len(frame))
    return rows_as_records(frame.sample(n=n, random_state=SAMPLE_SEED).sort_index())


MINIMAL_KEYS = {"name", "original_name", "type", "null_count", "distinct_count"}


def profile_for_model(profile: dict, privacy_level: str, frame: pd.DataFrame | None = None) -> dict:
    """What leaves the box, by privacy level (SPEC §6.2)."""
    columns = profile["columns"]
    if privacy_level == "minimal":
        columns = [{k: v for k, v in c.items() if k in MINIMAL_KEYS} for c in columns]
    out = {
        "row_count": profile["row_count"],
        "column_count": profile["column_count"],
        "columns": columns,
    }
    if privacy_level == "sample" and frame is not None:
        out["sample_rows"] = sample_rows(frame)
    return out
