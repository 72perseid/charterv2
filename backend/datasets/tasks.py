"""
Worker-side dataset processing: claim, ingest, profile, persist (SPEC §6.1).
"""

from __future__ import annotations

import logging
import time
from pathlib import Path

import pandas as pd
from django.conf import settings
from django.db import connection, transaction
from django.utils import timezone

from datasets.chronology import resolve
from datasets.ingest import IngestError, Limits, parse_file
from datasets.models import Dataset
from datasets.profile import build_profile, period_spans
from datasets.storage import PARSED_NAME, dataset_dir
from generation.periods import ask

log = logging.getLogger("charter.worker")

CLAIM_SQL = """
UPDATE datasets SET status = 'running', error_message = NULL
WHERE id = (
    SELECT id FROM datasets WHERE status = 'pending'
    ORDER BY created_at
    FOR UPDATE SKIP LOCKED
    LIMIT 1
)
RETURNING id
"""


def claim_dataset() -> Dataset | None:
    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute(CLAIM_SQL)
        row = cursor.fetchone()
    return Dataset.objects.get(pk=row[0]) if row else None


def ingest_dataset(dataset: Dataset) -> None:
    """Parse the original file, write parsed.parquet, store profile and counts."""
    overrides = dict(dataset.parse_options.get("overrides", {}))
    limits = Limits(settings.UPLOAD_MAX_ROWS, settings.UPLOAD_MAX_COLUMNS)
    parsed = parse_file(Path(dataset.original_path), dataset.original_filename, overrides, limits)

    # Answers the user's model gave about period labels are kept across re-reads;
    # new questions are asked now, once, and then forgotten as questions.
    answers = dict(dataset.parse_options.get("period_answers") or {})
    requests = dict(dataset.parse_options.get("period_requests") or {})
    for column in overrides.pop("period_questions", []):
        if parsed.parse_options["types"].get(column) != "period":
            continue
        known = answers.get(column, {})
        mapped = parsed.parse_options["period_mappings"].get(column)
        link = parsed.parse_options["period_dates"].get(column)
        spans = period_spans(parsed.frame, column, link) if link else None
        resolution = resolve(
            parsed.frame[column].dropna().astype(str).unique(), known, mapped, spans
        )
        new, requests[column] = ask(dataset.user_id, column, resolution)
        answers[column] = {**known, **new}
    parsed.parse_options["period_answers"] = answers
    parsed.parse_options["period_requests"] = requests

    directory = dataset_dir(dataset.user_id, dataset.pk)
    directory.mkdir(parents=True, exist_ok=True)
    parsed_path = directory / PARSED_NAME
    parsed.frame.to_parquet(parsed_path, index=False)

    profile = build_profile(parsed.frame, parsed.parse_options)
    dataset.parsed_path = str(parsed_path)
    dataset.parse_options = {**parsed.parse_options, "overrides": overrides}
    dataset.sheet_name = parsed.parse_options.get("sheet")
    dataset.profile = profile
    dataset.row_count = profile["row_count"]
    dataset.column_count = profile["column_count"]
    dataset.status = Dataset.Status.DONE
    dataset.error_message = None
    dataset.save()


def process_one_dataset() -> bool:
    dataset = claim_dataset()
    if dataset is None:
        return False
    started = time.monotonic()
    outcome = "done"
    try:
        ingest_dataset(dataset)
    except IngestError as exc:
        outcome = "failed"
        _fail(dataset, str(exc))
    except Exception:
        outcome = "failed"
        log.exception("dataset %s: unexpected error", dataset.pk)
        _fail(
            dataset, "The file could not be parsed. Check that it opens in a spreadsheet program."
        )
    log.info(
        "dataset=%s user=%s outcome=%s rows=%s columns=%s duration_ms=%d",
        dataset.pk,
        dataset.user_id,
        outcome,
        dataset.row_count,
        dataset.column_count,
        int((time.monotonic() - started) * 1000),
    )
    return True


def _fail(dataset: Dataset, message: str) -> None:
    dataset.status = Dataset.Status.FAILED
    dataset.error_message = message
    dataset.save(update_fields=["status", "error_message"])


def load_rows(dataset: Dataset) -> pd.DataFrame:
    return pd.read_parquet(dataset.parsed_path)


def mark_for_reingest(dataset: Dataset, overrides: dict) -> None:
    dataset.parse_options = {**dataset.parse_options, "overrides": overrides}
    dataset.status = Dataset.Status.PENDING
    dataset.error_message = None
    dataset.save(update_fields=["parse_options", "status", "error_message"])


def utcnow():
    return timezone.now()
