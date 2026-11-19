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

from generation.intent import AGGREGATES, AUTO

SCHEMA_URL = "https://vega.github.io/schema/vega-lite/v6.json"
FORBIDDEN_TOP = ("layer", "concat", "hconcat", "vconcat", "repeat", "facet", "spec")
CHANNEL_FALLBACK = {"x": "x_field", "y": "y_field", "color": "color_field"}
# Channels whose scale has an order worth fixing for a period column.
ORDERED_CHANNELS = (
    "x", "y", "xOffset", "yOffset", "color", "fill", "stroke", "opacity", "size",
    "shape", "strokeDash", "row", "column",
)  # fmt: skip
FILTER_OPERATORS = {"equal", "oneOf", "range", "lt", "lte", "gt", "gte", "valid"}
POINT_MARKS = {"point", "tick", "circle", "square"}
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


def order_periods(encoding: dict, period_orders: dict[str, list[str]]) -> list[str]:
    """Period columns are drawn oldest first (SPEC §6.3 step 4). The order comes
    from the dataset profile, not from the model, so it is the same on every
    run and at every privacy level. A sort the request asked for by another
    measure ("-y", a field, an encoding) is left alone; "descending" means
    newest first."""
    notes: list[str] = []
    for channel in ORDERED_CHANNELS:
        definition = encoding.get(channel)
        if not isinstance(definition, dict):
            continue
        order = period_orders.get(definition.get("field"))
        if not order or "aggregate" in definition or "bin" in definition:
            continue
        sort = definition.get("sort")
        if "sort" in definition and not (
            isinstance(sort, list) or sort in ("ascending", "descending")
        ):
            continue
        # A revision copies its parent's sort list, so a reversed list is "descending" too.
        newest_first = sort == "descending" or sort == list(reversed(order)) != list(order)
        wanted = list(reversed(order)) if newest_first else list(order)
        if sort == wanted and definition.get("type") == "ordinal":
            continue
        definition["sort"] = wanted
        definition["type"] = "ordinal"
        definition.pop("timeUnit", None)
        direction = "newest first" if newest_first else "oldest first"
        notes.append(f'{channel}: "{definition["field"]}" put in chronological order, {direction}')
    return notes


def _mark(spec: dict) -> str | None:
    mark = spec["mark"]
    return mark.get("type") if isinstance(mark, dict) else mark


def _set_mark(spec: dict, kind: str) -> None:
    if isinstance(spec["mark"], dict):
        spec["mark"]["type"] = kind
    else:
        spec["mark"] = kind


def apply_show(spec: dict, show: str) -> list[str]:
    """Make the spec agree with what the user chose to show (generation/intent.py).
    The choice is the user's, so it is applied, and each change is recorded."""
    y = spec["encoding"].get("y")
    if show == AUTO or not isinstance(y, dict):
        return []
    notes: list[str] = []
    if show in AGGREGATES:
        wanted = AGGREGATES[show]
        if y.get("aggregate") != wanted:
            y["aggregate"] = wanted
            notes.append(f'y: aggregate set to "{wanted}", as chosen ({show})')
        if _mark(spec) == "boxplot":
            _set_mark(spec, "bar")
            notes.append(f'mark set to "bar": a box plot cannot show a {show}')
        return notes
    if "aggregate" in y:
        notes.append(f'y: aggregate "{y.pop("aggregate")}" removed, as chosen ({show})')
    if show == "distribution" and _mark(spec) != "boxplot":
        _set_mark(spec, "boxplot")
        notes.append('mark set to "boxplot", as chosen (distribution)')
    if show == "points" and _mark(spec) not in POINT_MARKS:
        _set_mark(spec, "point")
        notes.append('mark set to "point", as chosen (points)')
    return notes


def _filter_fields(predicate) -> list[str]:
    """Every field a filter predicate names, through and / or / not."""
    if isinstance(predicate, list):
        return [name for part in predicate for name in _filter_fields(part)]
    if not isinstance(predicate, dict):
        return []  # an expression string: Vega evaluates it, nothing to look up
    names = [predicate["field"]] if isinstance(predicate.get("field"), str) else []
    for key in ("and", "or", "not"):
        names += _filter_fields(predicate.get(key))
    return names


def clean_filters(spec: dict, field_names: set[str]) -> list[str]:
    """A filter may only name fields of the profile; one that does not is
    rejected, because the limit it stands for cannot be applied. A condition
    with a field and nothing to compare it with ("is not missing", written in
    a form Vega-Lite does not have) limits nothing: it is dropped, and noted."""
    transforms = spec.get("transform")
    if not isinstance(transforms, list):
        return []
    notes: list[str] = []
    kept: list = []
    for transform in transforms:
        predicate = transform.get("filter") if isinstance(transform, dict) else None
        if not isinstance(predicate, dict):
            kept.append(transform)
            continue
        for name in _filter_fields(predicate):
            if name not in field_names:
                raise SpecError(
                    f'The filter names "{name}", which is not a field in the profile. '
                    "Filter only on fields from the profile, or leave the filter out."
                )
        joined = isinstance(predicate.get("and"), list)
        parts = predicate["and"] if joined else [predicate]
        real = []
        for part in parts:
            if isinstance(part, dict) and "field" in part and not FILTER_OPERATORS & part.keys():
                text = json.dumps(part, ensure_ascii=False)
                notes.append(f"removed a filter condition that compares nothing: {text}")
            else:
                real.append(part)
        if real:
            kept.append({**transform, "filter": {"and": real} if len(real) > 1 else real[0]})
    if kept:
        spec["transform"] = kept
    else:
        del spec["transform"]
    return notes


def apply_filter(spec: dict, row_filter: dict | None) -> list[str]:
    """The row filter the user chose stands in the spec exactly once, whatever
    the model wrote for that field."""
    if row_filter is None:
        return []
    wanted = {"filter": dict(row_filter)}
    transforms = spec.get("transform") if isinstance(spec.get("transform"), list) else []
    if wanted in transforms:
        return []
    kept = [
        t
        for t in transforms
        if not (isinstance(t, dict) and row_filter["field"] in _filter_fields(t.get("filter")))
    ]
    spec["transform"] = [wanted, *kept]
    value = json.dumps(row_filter["equal"], ensure_ascii=False)
    return [f'filter set to "{row_filter["field"]}" = {value}, as chosen']


def _most_specific(errors: list):
    """The schema is a union of chart kinds, so a mistake anywhere surfaces as
    "matches none of them" at the top, with the whole spec quoted. The useful
    message is the deepest one, and among equals the one that complains least:
    that is the branch the spec nearly fits."""

    def leaves(e):
        if not e.context:
            yield e
        for child in e.context:
            yield from leaves(child)

    return max(
        (leaf for error in errors for leaf in leaves(error)),
        key=lambda e: (
            len(e.absolute_path),
            e.validator != "required",  # "needs layer / facet / spec": other chart kinds
            -e.message.count("'"),
            -len(e.message),
        ),
    )


def validate_spec(
    text: str,
    *,
    field_names: set[str],
    x_field: str,
    y_field: str,
    color_field: str | None,
    period_orders: dict[str, list[str]] | None = None,
    show: str = AUTO,
    row_filter: dict | None = None,
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

    # Every encoded field must exist. One unknown field falls back to the user's
    # choice for that channel, or the channel is dropped, and that is recorded.
    # An answer whose x and y are both invented, or that names no real field at
    # all, was not written for this dataset: repairing it would dress up a
    # chart nobody asked for, so it is rejected.
    named = {
        channel: definition["field"]
        for channel, definition in spec["encoding"].items()
        if isinstance(definition, dict) and definition.get("field") is not None
    }
    unknown = {channel: name for channel, name in named.items() if name not in field_names}
    if unknown and (len(unknown) == len(named) or {"x", "y"} <= unknown.keys()):
        names = ", ".join(f'"{name}"' for name in dict.fromkeys(unknown.values()))
        raise SpecError(
            f"The answer uses field names that are not in the profile: {names}. "
            "Use only the field names given in the profile, exactly as written."
        )
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

    corrections += clean_filters(spec, field_names)
    corrections += apply_show(spec, show)
    corrections += apply_filter(spec, row_filter)
    corrections += order_periods(spec["encoding"], period_orders or {})

    errors = list(schema_validator().iter_errors(spec))
    if errors:
        error = _most_specific(errors)
        path = "/".join(str(p) for p in error.absolute_path) or "the top level"
        raise SpecError(f"Not valid Vega-Lite v6 at {path}: {error.message[:300]}")

    return Validated(spec=spec, corrections=corrections)
