"""
The dataset profile (SPEC §6.2): what the dataset page shows and, filtered by
privacy level, what the model sees. Plain JSON-serialisable Python only.
"""

from __future__ import annotations

import math
from typing import Any

import pandas as pd

from datasets.chronology import resolve, user_order
from datasets.periodo import gazetteer

TOP_VALUES = 5
SAMPLE_ROWS = 10
SAMPLE_SEED = 20260907
# A top value longer than this is a sentence (a citation, a note, a link), not
# a category: no chart groups or filters by it, and a few of them are a third
# of the prompt. Such values stay in the profile and are not sent to the model.
MODEL_VALUE_MAX = 40


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


def column_profile(
    name: str,
    original: str,
    series: pd.Series,
    kind: str,
    wanted_order: list[str] | None = None,
    answers: dict[str, dict] | None = None,
    mappings: dict[str, str] | None = None,
    spans: dict[str, tuple[float, float, bool]] | None = None,
) -> dict:
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
        if kind == "period":
            # Every distinct value, oldest first. `unplaced` are the ones that sort
            # last because nothing put them on the timeline. `matches` says, value by
            # value, which PeriodO definition (or date) decided its place.
            values = non_null.astype(str).unique()
            if wanted_order is None:
                resolution = resolve(values, answers, mappings, spans)
                out["order"], out["unplaced"] = resolution.order, resolution.unplaced
                out["order_source"] = "detected"
                out["matches"] = [m.as_dict() for m in resolution.matches]
                out["region"] = resolution.region
                out["periodo_snapshot"] = gazetteer().snapshot
            else:
                out["order"], out["unplaced"] = user_order(values, wanted_order)
                out["order_source"] = "user"
    return out


def period_spans(frame: pd.DataFrame, column: str, link: dict) -> dict:
    """What the dataset itself says about when each value of `column` is: the
    earliest start and the latest end among the rows that carry it, and whether
    those rows disagree (the same period name at two sites seldom has one date).
    `bc` means the years are written as positive numbers counted backwards."""
    start, end = link["start"], link.get("end") or link["start"]
    sign = -1 if link.get("bc") else 1
    rows = frame[[column, start, end]].copy() if end != start else frame[[column, start]].copy()
    rows = rows.dropna(subset=[column, start])
    spans: dict[str, tuple[float, float, bool]] = {}
    for value, group in rows.groupby(column, sort=False):
        starts = group[start].astype(float) * sign
        ends = (group[end].astype(float) * sign).fillna(starts)
        low, high = min(starts.min(), ends.min()), max(starts.max(), ends.max())
        spans[str(value)] = (float(low), float(high), starts.nunique() > 1 or ends.nunique() > 1)
    return spans


def build_profile(frame: pd.DataFrame, parse_options: dict) -> dict:
    types: dict[str, str] = parse_options["types"]
    originals: list[str] = parse_options["original_columns"]
    orders: dict[str, list[str]] = parse_options.get("period_orders") or {}
    answers: dict[str, dict] = parse_options.get("period_answers") or {}
    mappings: dict[str, dict] = parse_options.get("period_mappings") or {}
    links: dict[str, dict] = parse_options.get("period_dates") or {}
    columns = []
    for i, name in enumerate(frame.columns):
        spans = period_spans(frame, name, links[name]) if name in links else None
        column = column_profile(
            name,
            originals[i],
            frame[name],
            types[name],
            orders.get(name),
            answers.get(name),
            mappings.get(name),
            spans,
        )
        if name in links:
            column["dated_by"] = links[name]
        columns.append(column)
    return {
        "row_count": int(len(frame)),
        "column_count": int(len(frame.columns)),
        "columns": columns,
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
# A period column's order lists every distinct value. The server applies it to
# the chart itself (generation/validate.py), so the model never needs it.
SERVER_ONLY_KEYS = {
    "order", "unplaced", "order_source", "matches", "region", "periodo_snapshot", "dated_by",
}  # fmt: skip


def period_orders(profile: dict) -> dict[str, list[str]]:
    """Column name -> values oldest first, for the period columns of a profile."""
    return {
        c["name"]: c["order"]
        for c in profile.get("columns", [])
        if c.get("type") == "period" and c.get("order")
    }


def profile_for_model(profile: dict, privacy_level: str, frame: pd.DataFrame | None = None) -> dict:
    """What leaves the box, by privacy level (SPEC §6.2)."""
    columns = [
        {k: v for k, v in c.items() if k not in SERVER_ONLY_KEYS} for c in profile["columns"]
    ]
    if privacy_level == "minimal":
        columns = [{k: v for k, v in c.items() if k in MINIMAL_KEYS} for c in columns]
    for column in columns:
        # The model must write `name`; an identical original_name only costs tokens.
        if column.get("original_name") == column["name"]:
            del column["original_name"]
        if "top_values" in column:
            short = [v for v in column["top_values"] if len(v["value"]) <= MODEL_VALUE_MAX]
            if short:
                column["top_values"] = short
            else:
                del column["top_values"]
    out = {
        "row_count": profile["row_count"],
        "column_count": profile["column_count"],
        "columns": columns,
    }
    if privacy_level == "sample" and frame is not None:
        out["sample_rows"] = sample_rows(frame)
    return out
