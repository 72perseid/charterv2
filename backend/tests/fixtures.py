"""Fixture builders. The Turkish CSV is a committed file so reviewers can open
it; workbooks are built here because binary xlsx files do not diff."""

from pathlib import Path

from openpyxl import Workbook

FIXTURES = Path(__file__).parent / "fixtures"


def turkish_csv_bytes() -> bytes:
    return (FIXTURES / "kinet_tr.csv").read_bytes()


def plain_csv_bytes() -> bytes:
    return (FIXTURES / "plain_en.csv").read_bytes()


def workbook_with_title_row(path: Path) -> Path:
    """Sheet 1 is empty; sheet 2 has a title row and a blank row above the header."""
    book = Workbook()
    empty = book.active
    empty.title = "Notlar"
    data = book.create_sheet("Veri")
    data.append(["Kinet Höyük 2019 sezonu"])
    data.append([])
    data.append(["Buluntu", "Alan", "Derinlik", "Tarih", "Adet"])
    data.append(["KH-101", "A", 1.2, "2019-06-01", 3])
    data.append(["KH-102", "A", 1.7, "2019-06-02", 1])
    data.append(["KH-103", "B", 0.4, "2019-06-03", 7])
    book.save(path)
    return path
