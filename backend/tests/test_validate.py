import json

import pytest

from generation.validate import SpecError, parse_json, validate_spec

FIELDS = {"Alan", "Sayı", "Tarih"}
KW = {"field_names": FIELDS, "x_field": "Alan", "y_field": "Sayı", "color_field": None}

GOOD = {
    "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
    "title": "Buluntu sayısı",
    "data": {"name": "main"},
    "mark": "bar",
    "encoding": {
        "x": {"field": "Alan", "type": "nominal"},
        "y": {"field": "Sayı", "type": "quantitative", "aggregate": "sum"},
    },
}


def test_parse_json_strips_fences_and_prose():
    assert parse_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert parse_json('Here you go: {"a": 1} hope it helps') == {"a": 1}
    with pytest.raises(SpecError, match="not JSON"):
        parse_json("no braces here")
    with pytest.raises(SpecError, match="not valid JSON"):
        parse_json('{"a": }')
    with pytest.raises(SpecError, match="JSON object"):
        parse_json("[1, 2]")


def test_good_spec_passes_unchanged():
    out = validate_spec(json.dumps(GOOD), **KW)
    assert out.spec == GOOD
    assert out.corrections == []


def test_missing_mark_and_encoding():
    with pytest.raises(SpecError, match='no "mark"'):
        validate_spec(json.dumps({"encoding": {"x": {"field": "Alan"}}}), **KW)
    with pytest.raises(SpecError, match='no "encoding"'):
        validate_spec(json.dumps({"mark": "bar"}), **KW)


def test_forbidden_composition():
    with pytest.raises(SpecError, match='"layer" is not allowed'):
        validate_spec(json.dumps({"layer": [GOOD]}), **KW)


def test_unknown_field_is_replaced_or_channel_removed():
    spec = json.loads(json.dumps(GOOD))
    spec["encoding"]["x"]["field"] = "Bölge"
    spec["encoding"]["tooltip"] = {"field": "Yok", "type": "nominal"}
    out = validate_spec(json.dumps(spec), **KW)
    assert out.spec["encoding"]["x"]["field"] == "Alan"
    assert "tooltip" not in out.spec["encoding"]
    assert out.corrections == [
        'x: unknown field "Bölge" replaced with "Alan"',
        'tooltip: unknown field "Yok", channel removed',
    ]


def test_data_carrying_keys_are_stripped():
    spec = dict(GOOD, data={"values": [{"Alan": "A"}]}, datasets={"x": []})
    spec["transform"] = [{"url": "http://evil"}, {"filter": "datum.Sayı > 0"}]
    out = validate_spec(json.dumps(spec), **KW)
    assert out.spec["data"] == {"name": "main"}
    assert "datasets" not in out.spec
    assert out.spec["transform"] == [{"filter": "datum.Sayı > 0"}]
    assert 'set data to {"name": "main"}' in out.corrections
    assert "removed transforms that load data" in out.corrections


def test_schema_violation_is_reported_with_path():
    spec = json.loads(json.dumps(GOOD))
    spec["mark"] = "sparkle"
    with pytest.raises(SpecError, match="Not valid Vega-Lite v6"):
        validate_spec(json.dumps(spec), **KW)
    spec = json.loads(json.dumps(GOOD))
    spec["encoding"]["y"]["type"] = "money"
    with pytest.raises(SpecError, match="encoding/y"):
        validate_spec(json.dumps(spec), **KW)
