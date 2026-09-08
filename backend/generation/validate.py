"""
Turns model output into a Vega-Lite v6 spec we are willing to store, or says
precisely why not (SPEC §6.3 step 4). Corrections are recorded, not hidden.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from django.conf import settings
from jsonschema import Draft7Validator
from jsonschema.exceptions import best_match

SCHEMA_URL = "https://vega.github.io/schema/vega-lite/v6.json"
FORBIDDEN_TOP = ("layer", "concat", "hconcat", "vconcat", "repeat", "facet", "spec")
CHANNEL_FALLBACK = {"x": "x_field", "y": "y_field", "color": "color_field"}
FENCE = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$", re.IGNORECASE)


class SpecError(Exception):
    """Why the model's answer was rejected. Fed back to the model on retry."""


@dataclass
class Validated:
    spec: dict
    corrections: list[str] = field(default_factory=list)


@lru_cache
def schema_validator() -> Draft7Validator:
    schema = json.loads(
        (Path(settings.PROMPTS_DIR) / "vega-lite-v6.schema.json").read_text(encoding="utf-8")
    )
    return Draft7Validator(schema)


def parse_json(text: str) -> dict:
    cleaned = FENCE.sub("", text.strip())
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        # Prose around the object: keep the outermost braces.
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start == -1 or end == -1:
            raise SpecError("The answer is not JSON.") from None
        try:
            data = json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError as exc:
            raise SpecError(
                f"The answer is not valid JSON: {exc.msg} at position {exc.pos}."
            ) from exc
    if not isinstance(data, dict):
        raise SpecError("The answer must be a JSON object.")
    return data


def validate_spec(
    text: str,
    *,
    field_names: set[str],
    x_field: str,
    y_field: str,
    color_field: str | None,
) -> Validated:
    spec = parse_json(text)
    corrections: list[str] = []

    for key in FORBIDDEN_TOP:
        if key in spec:
            raise SpecError(f'"{key}" is not allowed; use a single mark with an encoding.')
    if "mark" not in spec:
        raise SpecError('The specification has no "mark".')
    if not isinstance(spec.get("encoding"), dict) or not spec["encoding"]:
        raise SpecError('The specification has no "encoding".')

    # Data is supplied by the browser; strip anything that carries values.
    for key in ("datasets", "values", "url"):
        if key in spec:
            spec.pop(key)
            corrections.append(f'removed top-level "{key}"')
    if spec.get("data") != {"name": "main"}:
        spec["data"] = {"name": "main"}
        corrections.append('set data to {"name": "main"}')
    if isinstance(spec.get("transform"), list):
        kept = [t for t in spec["transform"] if not (isinstance(t, dict) and "url" in t)]
        if len(kept) != len(spec["transform"]):
            corrections.append("removed transforms that load data")
        spec["transform"] = kept
    spec["$schema"] = SCHEMA_URL

    # Every encoded field must exist. Unknown fields fall back to the user's choice
    # for that channel, or the channel is dropped.
    fallback = {"x_field": x_field, "y_field": y_field, "color_field": color_field}
    for channel, definition in list(spec["encoding"].items()):
        if not isinstance(definition, dict):
            continue
        name = definition.get("field")
        if name is None or name in field_names:
            continue
        replacement = fallback.get(CHANNEL_FALLBACK.get(channel, ""))
        if replacement:
            definition["field"] = replacement
            corrections.append(f'{channel}: unknown field "{name}" replaced with "{replacement}"')
        else:
            spec["encoding"].pop(channel)
            corrections.append(f'{channel}: unknown field "{name}", channel removed')
    if not spec["encoding"]:
        raise SpecError("No encoding channel names a field from the profile.")

    error = best_match(schema_validator().iter_errors(spec))
    if error is not None:
        path = "/".join(str(p) for p in error.absolute_path) or "(root)"
        raise SpecError(f"Not valid Vega-Lite v6 at {path}: {error.message[:300]}")

    return Validated(spec=spec, corrections=corrections)
