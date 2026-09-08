"""
Worker-side chart generation (SPEC §6.3): claim a pending revision, build the
prompt, call the user's endpoint, validate, retry once, persist everything.
"""

from __future__ import annotations

import logging
import time
from datetime import timedelta
from urllib.parse import urlparse

from django.conf import settings
from django.db import connection, transaction
from django.utils import timezone

from accounts.crypto import decrypt
from accounts.models import ModelConfig
from charts.models import ChartRevision
from datasets.profile import profile_for_model
from datasets.tasks import load_rows
from generation.prompt import build_messages
from generation.provider import ProviderError, ProviderResult, chat_completion
from generation.validate import SpecError, validate_spec

log = logging.getLogger("charter.worker")

CLAIM_SQL = """
UPDATE chart_revisions
SET status = 'running', attempts = attempts + 1, started_at = now(), error_message = NULL
WHERE id = (
    SELECT id FROM chart_revisions WHERE status = 'pending'
    ORDER BY created_at
    FOR UPDATE SKIP LOCKED
    LIMIT 1
)
RETURNING id
"""


def claim_revision() -> ChartRevision | None:
    with transaction.atomic(), connection.cursor() as cursor:
        cursor.execute(CLAIM_SQL)
        row = cursor.fetchone()
    if row is None:
        return None
    return ChartRevision.objects.select_related("chart", "chart__dataset", "parent").get(pk=row[0])


def process_one_revision() -> bool:
    revision = claim_revision()
    if revision is None:
        return False
    started = time.monotonic()
    outcome = "done"
    try:
        generate(revision)
    except (ProviderError, SpecError) as exc:
        outcome = "failed"
        _fail(revision, str(exc))
    except Exception:
        outcome = "failed"
        log.exception("revision %s: unexpected error", revision.pk)
        _fail(revision, "Generation failed unexpectedly. The request and response were kept.")
    log.info(
        "revision=%s chart=%s user=%s endpoint=%s model=%s outcome=%s duration_ms=%s tokens=%s",
        revision.pk,
        revision.chart_id,
        revision.user_id,
        revision.endpoint_host,
        revision.model,
        outcome,
        int((time.monotonic() - started) * 1000),
        (revision.usage or {}).get("total_tokens"),
    )
    return True


def generate(revision: ChartRevision) -> None:
    config = ModelConfig.objects.filter(user_id=revision.user_id).first()
    if config is None:
        raise ProviderError("No model is configured. Add one under Settings.")
    dataset = revision.chart.dataset
    if dataset.status != "done" or not dataset.profile:
        raise SpecError("The dataset has not been parsed yet.")

    frame = load_rows(dataset) if dataset.privacy_level == "sample" else None
    visible = profile_for_model(dataset.profile, dataset.privacy_level, frame)
    field_names = {c["name"] for c in dataset.profile["columns"]}
    parent = revision.parent
    api_key = decrypt(config.api_key_encrypted)

    revision.model = config.model
    revision.endpoint_host = urlparse(config.base_url).hostname or ""
    revision.temperature = config.temperature
    revision.seed = settings.GENERATION_SEED
    revision.prompt_version = settings.PROMPT_VERSION
    revision.app_version = settings.APP_VERSION

    retry_error: str | None = None
    last_result: ProviderResult | None = None
    for attempt in range(2):
        messages = build_messages(
            profile_for_model=visible,
            x_field=revision.x_field,
            y_field=revision.y_field,
            color_field=revision.color_field,
            prompt=revision.prompt,
            parent_spec=parent.spec if parent and parent.spec else None,
            parent_prompt=parent.prompt if parent else None,
            retry_error=retry_error,
        )
        result = chat_completion(
            base_url=config.base_url,
            api_key=api_key,
            model=config.model,
            messages=messages,
            temperature=config.temperature,
            max_tokens=settings.GENERATION_MAX_TOKENS,
            json_object=True,
            seed=settings.GENERATION_SEED,
        )
        last_result = result
        _record(revision, messages, result, attempt)
        try:
            validated = validate_spec(
                result.text,
                field_names=field_names,
                x_field=revision.x_field,
                y_field=revision.y_field,
                color_field=revision.color_field,
            )
        except SpecError as exc:
            retry_error = str(exc)
            if attempt == 1:
                raise
            continue
        revision.spec = validated.spec
        revision.corrections = validated.corrections
        break

    revision.status = ChartRevision.Status.DONE
    revision.error_message = None
    _finish(revision)
    revision.save()

    chart = revision.chart
    newest = chart.revisions.order_by("-revision_no").values_list("pk", flat=True).first()
    if newest == revision.pk:
        chart.current_revision = revision
        chart.save(update_fields=["current_revision"])
    assert last_result is not None


def _record(revision: ChartRevision, messages: list[dict], result: ProviderResult, attempt: int):
    """The exact request and raw response, kept even when validation fails."""
    revision.request = {
        "attempt": attempt + 1,
        "messages": messages,
        "parameters": {k: v for k, v in result.request_body.items() if k not in {"messages"}},
        "adjustments": result.adjustments,
    }
    revision.response_text = result.text
    revision.usage = result.usage
    revision.model = result.model or revision.model
    revision.save(update_fields=["request", "response_text", "usage", "model"])


def _finish(revision: ChartRevision) -> None:
    revision.finished_at = timezone.now()
    if revision.started_at:
        delta: timedelta = revision.finished_at - revision.started_at
        revision.duration_ms = int(delta.total_seconds() * 1000)


RECORD_FIELDS = [
    "model",
    "endpoint_host",
    "temperature",
    "seed",
    "prompt_version",
    "app_version",
]


def _fail(revision: ChartRevision, message: str) -> None:
    revision.status = ChartRevision.Status.FAILED
    revision.error_message = message
    _finish(revision)
    revision.save(
        update_fields=["status", "error_message", "finished_at", "duration_ms", *RECORD_FIELDS]
    )
