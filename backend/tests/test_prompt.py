"""Snapshot the rendered prompt per version and privacy level (SPEC §10).
Delete a snapshot file to regenerate it after an intentional prompt change."""

from pathlib import Path

import pytest

from datasets.profile import profile_for_model
from generation.prompt import build_messages, load_template

SNAPSHOTS = Path(__file__).parent / "snapshots"

PROFILE = {
    "row_count": 6,
    "column_count": 3,
    "columns": [
        {
            "name": "Alan",
            "original_name": "Alan",
            "type": "string",
            "null_count": 0,
            "distinct_count": 3,
            "top_values": [{"value": "Açma A", "count": 2}],
            "max_length": 6,
        },
        {
            "name": "Sayı",
            "original_name": "Sayı",
            "type": "integer",
            "null_count": 0,
            "distinct_count": 6,
            "min": 0,
            "max": 5,
            "mean": 2.5,
            "median": 2.5,
        },
        {
            "name": "Tarih",
            "original_name": "Tarih",
            "type": "date",
            "null_count": 0,
            "distinct_count": 6,
            "min": "2019-05-03T00:00:00",
            "max": "2019-05-08T00:00:00",
        },
    ],
}


def render(messages: list[dict]) -> str:
    return "\n\n".join(f"[{m['role']}]\n{m['content']}" for m in messages)


@pytest.mark.parametrize("level", ["minimal", "statistics"])
def test_prompt_snapshot(level, settings):
    messages = build_messages(
        profile_for_model=profile_for_model(PROFILE, level),
        x_field="Alan",
        y_field="Sayı",
        color_field=None,
        prompt="Alanlara göre buluntu sayısı",
    )
    text = render(messages)
    path = SNAPSHOTS / f"{settings.PROMPT_VERSION}_{level}.txt"
    if not path.exists():
        path.write_text(text, encoding="utf-8")
        pytest.skip(f"wrote snapshot {path.name}")
    assert text == path.read_text(encoding="utf-8")


def test_template_sections_load(settings):
    template = load_template(settings.PROMPT_VERSION)
    assert template.system.startswith("You write Vega-Lite version 6")
    assert "{profile}" in template.user and "{prompt}" in template.user


def test_revision_and_retry_blocks():
    messages = build_messages(
        profile_for_model=profile_for_model(PROFILE, "minimal"),
        x_field="Tarih",
        y_field="Sayı",
        color_field="Alan",
        prompt="make it a line",
        parent_spec={"mark": "bar"},
        parent_prompt="bars please",
        retry_error='The specification has no "mark".',
    )
    assert len(messages) == 3
    assert "Previous request: bars please" in messages[1]["content"]
    assert '"mark": "bar"' in messages[1]["content"]
    assert "color: Alan" in messages[1]["content"]
    assert messages[2]["content"].startswith("Your previous answer was rejected")


def test_prompt_never_contains_rows_below_sample_level():
    minimal = render(
        build_messages(
            profile_for_model=profile_for_model(PROFILE, "statistics"),
            x_field="Alan",
            y_field="Sayı",
            color_field=None,
            prompt="x",
        )
    )
    assert "sample_rows" not in minimal
