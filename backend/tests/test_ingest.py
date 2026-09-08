from pathlib import Path

import pandas as pd  # noqa: E402  (grouped after project imports for readability)
import pytest

from datasets.ingest import (
    IngestError,
    Limits,
    coerce_series,
    decode,
    kind_of,
    normalise_columns,
    parse_file,
    sniff_delimiter,
)
from tests.fixtures import plain_csv_bytes, turkish_csv_bytes, workbook_with_title_row

LIMITS = Limits(max_rows=100_000, max_columns=200)


def test_kind_of():
    assert kind_of("x.CSV") == "text"
    assert kind_of("x.xlsx") == "excel"
    with pytest.raises(IngestError, match="xlsx"):
        kind_of("old.xls")
    with pytest.raises(IngestError, match="Unsupported"):
        kind_of("notes.docx")


def test_decode_prefers_utf8_then_cp1254():
    assert decode("Ağırlık".encode())[1] == "utf-8"
    assert decode("Ağırlık".encode("cp1254")) == ("Ağırlık", "cp1254")
    assert decode(b"\xef\xbb\xbfab")[1] == "utf-8-sig"


def test_sniff_delimiter():
    assert sniff_delimiter("a;b;c\n1;2;3\n") == ";"
    assert sniff_delimiter("a,b,c\n1,2,3\n") == ","
    assert sniff_delimiter("a\tb\n1\t2\n") == "\t"
    assert sniff_delimiter("a|b\n1|2\n") == "|"
    assert sniff_delimiter("Kinet Höyük, 2019;x\n1;2\n") == ";"  # comma in a value, semicolon wins


def test_turkish_csv(tmp_path: Path):
    path = tmp_path / "kinet.csv"
    path.write_bytes(turkish_csv_bytes())
    parsed = parse_file(path, "kinet.csv", {}, LIMITS)
    opts = parsed.parse_options
    assert opts["encoding"] == "cp1254"
    assert opts["delimiter"] == ";"
    assert opts["decimal"] == ","
    assert opts["types"] == {
        "Buluntu No": "string",
        "Alan": "string",
        "Derinlik (m)": "number",
        "Ağırlık (g)": "number",
        "Tarih": "date",
        "Sayı": "integer",
        "Korunmuş": "boolean",
    }
    frame = parsed.frame
    assert frame["Derinlik (m)"].tolist()[:2] == [1.25, 1.40]
    assert frame["Ağırlık (g)"][3] == 1250.5  # 1.250,50 grouped Turkish number
    assert pd.isna(frame["Ağırlık (g)"][2])
    assert frame["Tarih"][0] == pd.Timestamp("2019-05-03")  # dd.mm.yyyy, not mm.dd
    assert frame["Korunmuş"].tolist() == [True, False, True, True, False, True]


def test_plain_csv_detects_dot_decimal(tmp_path: Path):
    path = tmp_path / "plain.csv"
    path.write_bytes(plain_csv_bytes())
    parsed = parse_file(path, "plain.csv", {}, LIMITS)
    assert parsed.parse_options["delimiter"] == ","
    assert parsed.parse_options["decimal"] == "."
    assert parsed.parse_options["types"] == {
        "site": "string",
        "depth": "number",
        "count": "integer",
        "recorded": "date",
    }


def test_xlsx_skips_empty_sheet_and_title_row(tmp_path: Path):
    path = workbook_with_title_row(tmp_path / "book.xlsx")
    parsed = parse_file(path, "book.xlsx", {}, LIMITS)
    opts = parsed.parse_options
    assert opts["sheet"] == "Veri"
    assert opts["sheets"] == ["Notlar", "Veri"]
    assert opts["header_row"] == 2
    assert list(parsed.frame.columns) == ["Buluntu", "Alan", "Derinlik", "Tarih", "Adet"]
    assert opts["types"]["Derinlik"] == "number"
    assert opts["types"]["Adet"] == "integer"
    assert opts["types"]["Tarih"] == "date"
    assert len(parsed.frame) == 3


def test_xlsx_overrides(tmp_path: Path):
    path = workbook_with_title_row(tmp_path / "book.xlsx")
    with pytest.raises(IngestError, match="no sheet named"):
        parse_file(path, "book.xlsx", {"sheet": "Yok"}, LIMITS)
    with pytest.raises(IngestError, match="empty"):
        parse_file(path, "book.xlsx", {"sheet": "Notlar"}, LIMITS)
    parsed = parse_file(path, "book.xlsx", {"sheet": "Veri", "header_row": 3}, LIMITS)
    assert list(parsed.frame.columns)[0] == "KH-101"  # the user chose a data row as header


def test_limits(tmp_path: Path):
    path = tmp_path / "wide.csv"
    path.write_text(",".join(f"c{i}" for i in range(201)) + "\n" + ",".join(["1"] * 201) + "\n")
    with pytest.raises(IngestError, match="201 columns"):
        parse_file(path, "wide.csv", {}, LIMITS)

    path = tmp_path / "long.csv"
    path.write_text("a\n" + "1\n" * 11)
    with pytest.raises(IngestError, match="rows"):
        parse_file(path, "long.csv", {}, Limits(max_rows=10, max_columns=200))

    path = tmp_path / "headeronly.csv"
    path.write_text("a,b\n")
    with pytest.raises(IngestError, match="no data rows"):
        parse_file(path, "headeronly.csv", {}, LIMITS)


def test_normalise_columns():
    frame = pd.DataFrame([[1, 2, 3, 4]], columns=["  Ad  ", "Ad", "", "Unnamed: 3"])
    out, originals = normalise_columns(frame)
    assert list(out.columns) == ["Ad", "Ad_2", "column_3", "column_4"]
    assert originals == ["  Ad  ", "Ad", "", "Unnamed: 3"]


def test_coerce_mixed_numeric_text_stays_string():
    series = pd.Series(["12", "abc", "3"])
    _, kind = coerce_series(series)
    assert kind == "string"


def test_coerce_integer_floats_become_integer():
    out, kind = coerce_series(pd.Series([1.0, 2.0, None]))
    assert kind == "integer"
    assert out.tolist()[:2] == [1, 2]
