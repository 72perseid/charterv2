from datetime import datetime
from typing import Any

from ninja import Schema
from pydantic import Field


class RevisionIn(Schema):
    parent_id: int | None = None
    x_field: str = Field(min_length=1, max_length=200)
    y_field: str = Field(min_length=1, max_length=200)
    color_field: str | None = Field(default=None, max_length=200)
    prompt: str = Field(min_length=1, max_length=1000)
    # auto, total, average, count, distribution or points. auto leaves it to the model.
    show: str = "auto"
    # Only rows where filter_field equals filter_value. Both or neither.
    filter_field: str | None = Field(default=None, max_length=200)
    filter_value: str | None = Field(default=None, max_length=200)


class ChartIn(RevisionIn):
    dataset_id: int
    title: str = Field(default="", max_length=200)


class ChartPatch(Schema):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    current_revision_id: int | None = None


class RevisionOut(Schema):
    id: int
    chart_id: int
    revision_no: int
    parent_id: int | None
    x_field: str
    y_field: str
    color_field: str | None
    prompt: str
    show: str
    filter_field: str | None
    filter_value: str | None
    status: str
    attempts: int
    error_message: str | None
    spec: dict[str, Any] | None
    corrections: list[str]
    request: dict[str, Any] | None
    response_text: str | None
    model: str
    endpoint_host: str
    temperature: float | None
    seed: int | None
    prompt_version: str
    app_version: str
    usage: dict[str, Any] | None
    cost_usd: float | None  # fixed at run time
    cost_at_current_prices: float | None  # only when cost_usd is unknown; not stored
    started_at: datetime | None
    finished_at: datetime | None
    duration_ms: int | None
    created_at: datetime


class RevisionSummary(Schema):
    id: int
    revision_no: int
    parent_id: int | None
    x_field: str
    y_field: str
    color_field: str | None
    prompt: str
    show: str
    filter_field: str | None
    filter_value: str | None
    status: str
    error_message: str | None
    model: str
    duration_ms: int | None
    cost_usd: float | None
    created_at: datetime


class ChartOut(Schema):
    id: int
    dataset_id: int
    dataset_name: str
    title: str
    current_revision_id: int | None
    current_status: str | None
    revision_count: int
    created_at: datetime
    updated_at: datetime


class ChartDetail(ChartOut):
    revisions: list[RevisionSummary]


class Detail(Schema):
    detail: str
