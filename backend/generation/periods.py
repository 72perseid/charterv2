"""
Ask the user's model about period labels nothing local could place (ADR 0018).
This is the one other thing that leaves the box besides the dataset profile, so
it happens only when the user presses the button for a column, and the exact
request and raw answer are kept with the dataset like a revision's are.

The model is asked for a period *name*; `datasets/chronology.py` looks that name
up in PeriodO, so the date still comes from a published definition whenever
PeriodO has one. The model's own years are the fallback and are marked as such.
"""

from __future__ import annotations

import json
from urllib.parse import urlparse

from django.conf import settings
from django.utils import timezone

from accounts.crypto import decrypt
from accounts.models import ModelConfig
from datasets.chronology import Resolution, is_undated
from generation.prompt import load_template
from generation.provider import ProviderError, chat_completion
from generation.validate import SpecError, parse_json

MAX_LABELS = 100
YEARS = range(-3_000_000, 2101)


def labels_to_ask(resolution: Resolution) -> list[str]:
    return [v for v in resolution.unplaced if not is_undated(v)][:MAX_LABELS]


def build_messages(column: str, resolution: Resolution, labels: list[str]) -> list[dict]:
    template = load_template(settings.PERIODS_PROMPT_VERSION)
    placed = "\n".join(
        f"- {m.value}: {round(m.start)} to {round(m.stop)}" for m in resolution.matches
    )
    user = template.user.format(
        column=column,
        region=resolution.region or "(none)",
        placed=placed or "(none)",
        labels=json.dumps(labels, ensure_ascii=False, indent=1),
    )
    return [{"role": "system", "content": template.system}, {"role": "user", "content": user}]


def read_answers(text: str, labels: list[str]) -> dict[str, dict]:
    """Keep only well-formed answers for labels that were asked about."""
    data = parse_json(text)
    answers: dict[str, dict] = {}
    for label in labels:
        raw = data.get(label)
        if not isinstance(raw, dict):
            continue
        name = raw.get("name") if isinstance(raw.get("name"), str) else None
        start, end = raw.get("start"), raw.get("end")
        years_ok = all(
            isinstance(y, int) and not isinstance(y, bool) and y in YEARS for y in (start, end)
        )
        if not name and not years_ok:
            continue
        answers[label] = {
            "name": name.strip()[:120] if name else None,
            "start": start if years_ok else None,
            "end": end if years_ok else None,
        }
    return answers


def ask(user_id, column: str, resolution: Resolution) -> tuple[dict[str, dict], dict]:
    """(answers, record). The record is stored whatever happens; a failure is an
    `error` in it, never a failed dataset."""
    labels = labels_to_ask(resolution)
    record: dict = {"asked_at": timezone.now().isoformat(), "labels": labels}
    record["prompt_version"] = settings.PERIODS_PROMPT_VERSION
    if not labels:
        return {}, record
    config = ModelConfig.objects.filter(user_id=user_id).first()
    if config is None:
        record["error"] = "No model is configured. Add one under Settings."
        return {}, record

    messages = build_messages(column, resolution, labels)
    record.update(messages=messages, endpoint_host=urlparse(config.base_url).hostname or "")
    try:
        result = chat_completion(
            base_url=config.base_url,
            api_key=decrypt(config.api_key_encrypted),
            model=config.model,
            messages=messages,
            temperature=config.temperature,
            max_tokens=settings.GENERATION_MAX_TOKENS,
            json_object=True,
            seed=settings.GENERATION_SEED,
        )
    except ProviderError as exc:
        record["error"] = str(exc)
        return {}, record
    record.update(
        response_text=result.text,
        model=result.model or config.model,
        usage=result.usage,
        parameters={k: v for k, v in result.request_body.items() if k != "messages"},
        adjustments=result.adjustments,
    )
    try:
        answers = read_answers(result.text, labels)
    except SpecError as exc:
        record["error"] = str(exc)
        return {}, record
    record["answered"] = sorted(answers)
    return answers, record
