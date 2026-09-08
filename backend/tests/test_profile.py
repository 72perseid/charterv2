import pandas as pd

from datasets.profile import build_profile, profile_for_model, rows_as_records, sample_rows


def frame_and_options():
    frame = pd.DataFrame(
        {
            "alan": pd.Series(["A", "A", "B", None], dtype="string"),
            "derinlik": [1.5, 2.5, None, 0.5],
            "adet": pd.Series([3, 1, 7, 2], dtype="Int64"),
            "tarih": pd.to_datetime(["2019-05-03", "2019-05-04", "2019-05-05", None]),
            "ok": pd.Series([True, False, True, None], dtype="boolean"),
        }
    )
    options = {
        "types": {
            "alan": "string",
            "derinlik": "number",
            "adet": "integer",
            "tarih": "date",
            "ok": "boolean",
        },
        "original_columns": ["Alan ", "Derinlik", "Adet", "Tarih", "OK"],
    }
    return frame, options


def test_build_profile():
    frame, options = frame_and_options()
    profile = build_profile(frame, options)
    assert profile["row_count"] == 4 and profile["column_count"] == 5
    by_name = {c["name"]: c for c in profile["columns"]}

    assert by_name["alan"]["original_name"] == "Alan "
    assert by_name["alan"]["null_count"] == 1
    assert by_name["alan"]["distinct_count"] == 2
    assert by_name["alan"]["top_values"] == [{"value": "A", "count": 2}, {"value": "B", "count": 1}]
    assert by_name["alan"]["max_length"] == 1

    assert by_name["derinlik"] == {
        "name": "derinlik",
        "original_name": "Derinlik",
        "type": "number",
        "null_count": 1,
        "distinct_count": 3,
        "min": 0.5,
        "max": 2.5,
        "mean": 1.5,
        "median": 1.5,
    }
    assert by_name["adet"]["min"] == 1 and by_name["adet"]["max"] == 7
    assert by_name["tarih"]["min"] == "2019-05-03T00:00:00"
    assert by_name["ok"]["true_count"] == 2


def test_rows_are_json_safe():
    frame, _ = frame_and_options()
    rows = rows_as_records(frame)
    assert rows[2] == {
        "alan": "B",
        "derinlik": None,
        "adet": 7,
        "tarih": "2019-05-05T00:00:00",
        "ok": True,
    }
    assert rows[3]["alan"] is None and rows[3]["tarih"] is None and rows[3]["ok"] is None


def test_privacy_levels():
    frame, options = frame_and_options()
    profile = build_profile(frame, options)

    minimal = profile_for_model(profile, "minimal")
    assert set(minimal["columns"][0]) == {
        "name",
        "original_name",
        "type",
        "null_count",
        "distinct_count",
    }
    assert "sample_rows" not in minimal

    stats = profile_for_model(profile, "statistics")
    assert "top_values" in stats["columns"][0]
    assert "sample_rows" not in stats

    sample = profile_for_model(profile, "sample", frame)
    assert len(sample["sample_rows"]) == 4
    assert sample_rows(frame) == sample_rows(frame)  # fixed seed
