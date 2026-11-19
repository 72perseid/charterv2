"""
What the user chose beside the request text (SPEC §6.3 step 1): what the chart
shows and, optionally, which rows it is limited to. The model is told, and
`generation/validate.py` then makes the answer agree, so a choice made here
never depends on how well a model reads a sentence.
"""

from __future__ import annotations

import pandas as pd

AUTO = "auto"
# choice -> what the model is told
SHOW = {
    AUTO: "(not chosen; decide from the request)",
    "total": 'total: "aggregate": "sum" inside the y channel',
    "average": 'average: "aggregate": "mean" inside the y channel',
    "count": 'count: the number of rows, "aggregate": "count" inside the y channel',
    "distribution": 'distribution: mark "boxplot", y not aggregated',
    "points": 'points: one mark per row, mark "point", y not aggregated',
}
AGGREGATES = {"total": "sum", "average": "mean", "count": "count"}
FILTERABLE = {"string", "period", "boolean", "integer", "number"}


class FilterError(ValueError):
    """Why a row filter cannot be used. Shown to the user as it is."""


def filter_literal(column: dict, value: str) -> str | int | float | bool:
    """The filter value in the column's own type, as it has to stand in the spec."""
    kind = column["type"]
    if kind not in FILTERABLE:
        raise FilterError(f"'{column['name']}' is a {kind} column; filter on text or numbers.")
    text = value.strip()
    if kind == "boolean":
        if text.lower() not in {"true", "false"}:
            raise FilterError("A yes/no column is filtered with true or false.")
        return text.lower() == "true"
    if kind in {"integer", "number"}:
        try:
            number = float(text.replace(",", "."))
        except ValueError:
            raise FilterError(f"'{column['name']}' holds numbers; '{value}' is not one.") from None
        return int(number) if number.is_integer() else number
    return text


def occurs(frame: pd.DataFrame, name: str, literal) -> bool:
    return bool((frame[name].dropna() == literal).any())


def row_filter(profile: dict, field: str | None, value: str | None) -> dict | None:
    """{"field", "equal"} for the spec, or None when no filter was chosen."""
    if not field or value is None or not value.strip():
        return None
    column = next((c for c in profile.get("columns", []) if c["name"] == field), None)
    if column is None:
        raise FilterError(f"filter field '{field}' is not a column of this dataset.")
    return {"field": field, "equal": filter_literal(column, value)}
