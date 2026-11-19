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


ORDER = ["Kalkolitik", "Demir Çağı", "Roma"]
PERIOD_KW = {
    "field_names": FIELDS | {"Dönem"},
    "x_field": "Dönem",
    "y_field": "Sayı",
    "color_field": None,
    "period_orders": {"Dönem": ORDER},
}


def period_spec(**x) -> str:
    spec = json.loads(json.dumps(GOOD))
    spec["encoding"]["x"] = {"field": "Dönem", "type": "nominal", **x}
    return json.dumps(spec)


def test_period_field_is_put_in_chronological_order():
    out = validate_spec(period_spec(), **PERIOD_KW)
    assert out.spec["encoding"]["x"] == {"field": "Dönem", "type": "ordinal", "sort": ORDER}
    assert out.corrections == ['x: "Dönem" put in chronological order, oldest first']


def test_period_order_replaces_the_models_guess_and_a_time_unit():
    out = validate_spec(
        period_spec(type="temporal", timeUnit="year", sort=["Roma", "Demir Çağı"]), **PERIOD_KW
    )
    assert out.spec["encoding"]["x"] == {"field": "Dönem", "type": "ordinal", "sort": ORDER}


def test_period_newest_first_and_its_revision():
    newest = ORDER[::-1]
    out = validate_spec(period_spec(sort="descending"), **PERIOD_KW)
    assert out.spec["encoding"]["x"]["sort"] == newest
    assert out.corrections == ['x: "Dönem" put in chronological order, newest first']
    # A revision starts from the parent's spec, which already carries the reversed list.
    again = validate_spec(period_spec(type="ordinal", sort=newest), **PERIOD_KW)
    assert again.spec["encoding"]["x"]["sort"] == newest
    assert again.corrections == []


def test_period_sorted_by_another_measure_is_left_alone():
    out = validate_spec(period_spec(sort="-y"), **PERIOD_KW)
    assert out.spec["encoding"]["x"] == {"field": "Dönem", "type": "nominal", "sort": "-y"}
    assert out.corrections == []


def test_period_on_color_and_counted_period():
    spec = json.loads(json.dumps(GOOD))
    spec["encoding"]["color"] = {"field": "Dönem", "type": "nominal"}
    spec["encoding"]["y"] = {"field": "Dönem", "aggregate": "count", "type": "quantitative"}
    out = validate_spec(json.dumps(spec), **PERIOD_KW)
    assert out.spec["encoding"]["color"]["sort"] == ORDER
    assert "sort" not in out.spec["encoding"]["y"]


def test_invented_x_and_y_are_rejected_not_repaired():
    # What a model writes when it never read the profile (a truncated prompt).
    answer = {
        **GOOD,
        "encoding": {
            "x": {"field": "period", "type": "ordinal"},
            "y": {"field": "count", "type": "quantitative", "aggregate": "sum"},
        },
    }
    with pytest.raises(SpecError, match='not in the profile: "period", "count"'):
        validate_spec(json.dumps(answer), **KW)
    # One near miss is still repaired, and says so.
    answer["encoding"]["x"]["field"] = "Alan"
    out = validate_spec(json.dumps(answer), **KW)
    assert out.spec["encoding"]["y"]["field"] == "Sayı"
    assert out.corrections == ['y: unknown field "count" replaced with "Sayı"']


@pytest.mark.parametrize(
    ("show", "mark", "aggregate"),
    [
        ("auto", "bar", "sum"),
        ("total", "bar", "sum"),
        ("average", "bar", "mean"),
        ("count", "bar", "count"),
        ("distribution", "boxplot", None),
        ("points", "point", None),
    ],
)
def test_the_chosen_show_decides_mark_and_aggregate(show, mark, aggregate):
    out = validate_spec(json.dumps(GOOD), show=show, **KW)
    assert out.spec["mark"] == mark
    assert out.spec["encoding"]["y"].get("aggregate") == aggregate
    assert bool(out.corrections) == (show not in {"auto", "total"})


def test_show_turns_a_boxplot_back_into_bars_for_a_total():
    answer = {**GOOD, "mark": {"type": "boxplot"}}
    answer["encoding"] = {**GOOD["encoding"], "y": {"field": "Sayı", "type": "quantitative"}}
    out = validate_spec(json.dumps(answer), show="total", **KW)
    assert out.spec["mark"] == {"type": "bar"}
    assert out.spec["encoding"]["y"]["aggregate"] == "sum"


def test_the_chosen_filter_stands_in_the_spec_once():
    chosen = {"field": "Alan", "equal": "Açma A"}
    out = validate_spec(json.dumps(GOOD), row_filter=chosen, **KW)
    assert out.spec["transform"] == [{"filter": chosen}]
    assert out.corrections == ['filter set to "Alan" = "Açma A", as chosen']
    # The model wrote it already: nothing to correct. It wrote another value: replaced.
    same = {**GOOD, "transform": [{"filter": chosen}]}
    assert validate_spec(json.dumps(same), row_filter=chosen, **KW).corrections == []
    other = {**GOOD, "transform": [{"filter": {"field": "Alan", "equal": "Açma B"}}]}
    out = validate_spec(json.dumps(other), row_filter=chosen, **KW)
    assert out.spec["transform"] == [{"filter": chosen}]


def test_a_filter_on_an_unknown_field_is_rejected():
    answer = {**GOOD, "transform": [{"filter": {"field": "Region", "equal": "Thessaly"}}]}
    with pytest.raises(SpecError, match='The filter names "Region"'):
        validate_spec(json.dumps(answer), **KW)
    nested = {"not": {"field": "Bölge", "equal": "x"}}
    with pytest.raises(SpecError, match='The filter names "Bölge"'):
        validate_spec(json.dumps({**GOOD, "transform": [{"filter": nested}]}), **KW)
    # A filter the model wrote on a real field is kept as written.
    kept = {**GOOD, "transform": [{"filter": {"field": "Alan", "equal": "Açma A"}}]}
    assert validate_spec(json.dumps(kept), **KW).spec["transform"] == kept["transform"]


def test_a_filter_condition_that_compares_nothing_is_dropped():
    empty = {"field": "Alan", "not": {"missing": True}}
    real = {"field": "Alan", "equal": "Açma A"}
    answer = {**GOOD, "transform": [{"filter": {"and": [real, empty]}}]}
    out = validate_spec(json.dumps(answer), **KW)
    assert out.spec["transform"] == [{"filter": real}]
    assert out.corrections == [
        "removed a filter condition that compares nothing: " + json.dumps(empty, ensure_ascii=False)
    ]
    # Nothing real is left: no transform at all.
    out = validate_spec(json.dumps({**GOOD, "transform": [{"filter": empty}]}), **KW)
    assert "transform" not in out.spec


def test_schema_errors_name_the_place_not_the_whole_spec():
    misplaced = {**GOOD, "aggregate": {"groupby": ["Alan"]}}
    with pytest.raises(SpecError) as caught:
        validate_spec(json.dumps(misplaced), **KW)
    message = str(caught.value)
    assert "top level" in message and "'aggregate' was unexpected" in message
    assert "'mark'" not in message and "$schema" not in message
