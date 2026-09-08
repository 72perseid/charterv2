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


class DatasetPatch(Schema):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    privacy_level: str | None = None
    sheet: str | None = None
    header_row: int | None = Field(default=None, ge=0, le=1000)


class RowsOut(Schema):
    total: int
    offset: int
    limit: int
    columns: list[str]
    rows: list[dict[str, Any]]


class Detail(Schema):
    detail: str
