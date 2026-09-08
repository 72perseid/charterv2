"""
The reproducibility bundle (SPEC §7, GET /charts/{id}/export): everything
needed to explain how each chart came to be, in one JSON document. The
dataset's rows are not included; the profile and parse options say how they
were read, and the original file is downloadable separately.
"""

from __future__ import annotations

from django.conf import settings
from django.utils import timezone

from charts.models import Chart, ChartRevision

BUNDLE_FORMAT = "charter-bundle/1"

REVISION_FIELDS = [
    "id",
    "revision_no",
    "parent_id",
    "x_field",
    "y_field",
    "color_field",
    "prompt",
    "status",
    "attempts",
    "error_message",
    "spec",
    "corrections",
    "request",
    "response_text",
    "model",
    "endpoint_host",
    "temperature",
    "seed",
    "prompt_version",
    "app_version",
    "usage",
    "cost_usd",
    "started_at",
    "finished_at",
    "duration_ms",
    "created_at",
]


def revision_record(revision: ChartRevision) -> dict:
    record = {name: getattr(revision, name) for name in REVISION_FIELDS}
    for key in ("started_at", "finished_at", "created_at"):
        if record[key] is not None:
            record[key] = record[key].isoformat()
    return record


def build_bundle(chart: Chart) -> dict:
    dataset = chart.dataset
    return {
        "format": BUNDLE_FORMAT,
        "exported_at": timezone.now().isoformat(),
        "app_version": settings.APP_VERSION,
        "chart": {
            "id": chart.pk,
            "title": chart.title,
            "current_revision_id": chart.current_revision_id,
            "created_at": chart.created_at.isoformat(),
        },
        "dataset": {
            "id": dataset.pk,
            "name": dataset.name,
            "original_filename": dataset.original_filename,
            "size_bytes": dataset.size_bytes,
            "row_count": dataset.row_count,
            "column_count": dataset.column_count,
            "privacy_level": dataset.privacy_level,
            "parse_options": dataset.parse_options,
            "profile": dataset.profile,
            "created_at": dataset.created_at.isoformat(),
        },
        "revisions": [revision_record(r) for r in chart.revisions.order_by("revision_no")],
    }
