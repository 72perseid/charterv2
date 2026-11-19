"""Snapshot the rendered prompt per version and privacy level (SPEC §10).
Delete a snapshot file to regenerate it after an intentional prompt change."""

import json
from pathlib import Path

import pytest

from datasets.profile import profile_for_model
from generation.prompt import (
    build_messages,
    load_template,
    render_profile,
    spec_for_revision,
)

SNAPSHOTS = Path(__file__).parent / "snapshots"

PROFILE = {
    "row_count": 6,
    "column_count": 4,
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
        {
            "name": "Dönem",
            "original_name": "Dönem",
            "type": "period",
            "null_count": 0,
            "distinct_count": 3,
            "top_values": [{"value": "Roma", "count": 3}],
            "max_length": 10,
            "order": ["Demir Çağı", "Helenistik", "Roma"],
            "unplaced": [],
            "order_source": "detected",
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


def test_period_order_stays_on_the_server():
    text = render(
        build_messages(
            profile_for_model=profile_for_model(PROFILE, "statistics"),
            x_field="Dönem",
            y_field="Sayı",
            color_field=None,
            prompt="x",
        )
    )
    assert '"type": "period"' in text and 'period is "ordinal"' in text
    assert "Helenistik" not in text and "order_source" not in text


def test_profile_is_sent_one_column_per_line_without_long_text():
    profile = {
        "row_count": 2,
        "column_count": 2,
        "columns": [
            {
                "name": "Reference",
                "original_name": "Reference",
                "type": "string",
                "null_count": 0,
                "distinct_count": 2,
                "top_values": [
                    {
                        "value": "Halstead, P. 2011. Farming and feasting in the Neolithic",
                        "count": 3,
                    },
                    {"value": "this volume", "count": 2},
                ],
            },
            {
                "name": "gl",
                "original_name": "GL (mm)",
                "type": "number",
                "null_count": 0,
                "distinct_count": 2,
            },
        ],
    }
    visible = profile_for_model(profile, "statistics")
    reference, gl = visible["columns"]
    assert reference["top_values"] == [{"value": "this volume", "count": 2}]
    assert "original_name" not in reference and gl["original_name"] == "GL (mm)"
    assert profile["columns"][0]["top_values"][0]["value"].startswith("Halstead")  # not mutated

    text = render_profile(visible)
    assert json.loads(text) == visible
    assert text.count("\n") == 3  # the opening line, two columns, the closing line


def test_revision_block_leaves_out_the_period_sort_list():
    orders = {"Dönem": ["Demir Çağı", "Helenistik", "Roma"]}
    parent = {
        "mark": "bar",
        "encoding": {
            "x": {"field": "Dönem", "type": "ordinal", "sort": list(orders["Dönem"])},
            "y": {"field": "Sayı", "type": "quantitative", "sort": ["b", "a"]},
        },
    }
    out = spec_for_revision(parent, orders)
    assert "sort" not in out["encoding"]["x"]
    assert out["encoding"]["y"]["sort"] == ["b", "a"]  # not a period column: left alone
    assert parent["encoding"]["x"]["sort"] == orders["Dönem"]  # the stored spec is untouched
    parent["encoding"]["x"]["sort"].reverse()
    assert spec_for_revision(parent, orders)["encoding"]["x"]["sort"] == "descending"


def test_show_and_filter_are_stated_in_the_user_message():
    text = build_messages(
        profile_for_model=profile_for_model(PROFILE, "minimal"),
        x_field="Dönem",
        y_field="Sayı",
        color_field=None,
        prompt="x",
        show="distribution",
        row_filter={"field": "Alan", "equal": "Açma A"},
    )[1]["content"]
    assert 'show: distribution: mark "boxplot", y not aggregated' in text
    assert 'only rows where: Alan = "Açma A"' in text
