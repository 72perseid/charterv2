from datetime import datetime
from typing import Any

from ninja import Schema
from pydantic import Field


class DatasetOut(Schema):
    id: int
    name: str
    original_filename: str
    row_count: int
    column_count: int
    size_bytes: int
    privacy_level: str
    status: str
    error_message: str | None
    created_at: datetime


class DatasetDetail(DatasetOut):
    sheet_name: str | None
    parse_options: dict[str, Any]
    profile: dict[str, Any]


class PeriodDates(Schema):
    """One column dated by others in the same dataset: `start`, and `end` if
    there is one. `bc`: the years are positive numbers counted backwards."""

    start: str
    end: str | None = None
    bc: bool = False


class DatasetPatch(Schema):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    privacy_level: str | None = None
    sheet: str | None = None
    header_row: int | None = Field(default=None, ge=0, le=1000)
    # Per column: a list is the chronological order (oldest first), true makes
    # the column a period with the detected order, false keeps it plain text,
    # null returns it to automatic detection.
    periods: dict[str, list[str] | bool | None] | None = None
    # Per column, per value: what the value means, as a period name or a date
    # ("Early Chalcolithic", "720-650 BC"). null or "" removes the mapping.
    period_mappings: dict[str, dict[str, str | None]] | None = None
    # Per column: the columns of this dataset that give its values their dates.
    # null removes the link.
    period_dates: dict[str, PeriodDates | None] | None = None


class PeriodQuestion(Schema):
    column: str


class RowsOut(Schema):
    total: int
    offset: int
    limit: int
    columns: list[str]
    rows: list[dict[str, Any]]


class Detail(Schema):
    detail: str
