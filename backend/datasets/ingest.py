"""
File in, typed DataFrame out (SPEC §6.1). Every choice made along the way is
returned in `parse_options` so the dataset page can show it and a bundle can
reproduce it. Nothing here touches the database.
"""

from __future__ import annotations

import io
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from datasets.chronology import looks_chronological

TEXT_KINDS = {"csv", "tsv", "txt"}
EXCEL_KINDS = {"xlsx"}
ENCODINGS = ("utf-8", "cp1254", "latin-1")  # utf-8-sig is detected by its BOM first
DELIMITERS = (",", ";", "\t", "|")
NA_VALUES = ["", "NA", "N/A", "n/a", "NaN", "nan", "null", "NULL", "-", "—"]

BOOL_WORDS = {
    "true": True,
    "false": False,
    "yes": True,
    "no": False,
    "evet": True,
    "hayır": False,
    "hayir": False,
}

# 1.234.567,89 (Turkish) and 1,234,567.89 (English). Two-digit groups such as
# 12.05.2024 do not match, so dates are never mistaken for grouped numbers.
GROUPED_TR = re.compile(r"^-?\d{1,3}(\.\d{3})+(,\d+)?$")
GROUPED_EN = re.compile(r"^-?\d{1,3}(,\d{3})+(\.\d+)?$")
DATE_LIKE = re.compile(r"^\s*\d{1,4}[-./]\d{1,2}[-./]\d{1,4}([ T]\d{1,2}:\d{2}(:\d{2})?)?\s*$")


class IngestError(Exception):
    """A problem the user can act on. The message is shown verbatim."""


@dataclass
class Limits:
    max_rows: int
    max_columns: int


@dataclass
class Parsed:
    frame: pd.DataFrame
    parse_options: dict


def kind_of(filename: str) -> str:
    ext = Path(filename).suffix.lower().lstrip(".")
    if ext == "xls":
        raise IngestError(
            "Old Excel (.xls) files are not supported. Save the file as .xlsx and upload again."
        )
    if ext in TEXT_KINDS:
        return "text"
    if ext in EXCEL_KINDS:
        return "excel"
    raise IngestError("Unsupported file type. Upload a .csv, .tsv, .txt, or .xlsx file.")


# --- text files -----------------------------------------------------------


def decode(raw: bytes) -> tuple[str, str]:
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw[3:].decode("utf-8", errors="replace"), "utf-8-sig"
    for encoding in ENCODINGS:
        try:
            return raw.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1", errors="replace"), "latin-1"  # cannot fail


def sniff_delimiter(text: str) -> str:
    lines = [line for line in text.splitlines()[:20] if line.strip()]
    if not lines:
        raise IngestError("The file is empty.")

    def score(delim: str) -> tuple[int, int]:
        counts = [line.count(delim) for line in lines]
        if max(counts) == 0:
            return (0, 0)
        mode = max(set(counts), key=counts.count)
        consistent = sum(1 for c in counts if c == mode and c > 0)
        return (consistent, mode)

    best = max(DELIMITERS, key=score)
    return best if score(best)[0] > 0 else ","


def _read_text(text: str, delimiter: str, decimal: str, header_row: int) -> pd.DataFrame:
    return pd.read_csv(
        io.StringIO(text),
        sep=delimiter,
        decimal=decimal,
        header=header_row,
        na_values=NA_VALUES,
        keep_default_na=False,
        skip_blank_lines=True,
        dtype=None,
        engine="python" if delimiter == "|" else "c",
    )


def _numeric_columns(frame: pd.DataFrame) -> int:
    return int(sum(pd.api.types.is_numeric_dtype(frame[c]) for c in frame.columns))


def parse_text(raw: bytes, overrides: dict) -> Parsed:
    text, encoding = decode(raw)
    delimiter = overrides.get("delimiter") or sniff_delimiter(text)
    header_row = int(overrides.get("header_row") or 0)

    if overrides.get("decimal"):
        decimal = overrides["decimal"]
        frame = _read_text(text, delimiter, decimal, header_row)
    elif delimiter == ";":
        decimal = ","
        frame = _read_text(text, delimiter, decimal, header_row)
    else:
        # Detect: whichever decimal mark yields more numeric columns wins; ties go to '.'.
        with_dot = _read_text(text, delimiter, ".", header_row)
        with_comma = _read_text(text, delimiter, ",", header_row)
        if _numeric_columns(with_comma) > _numeric_columns(with_dot):
            decimal, frame = ",", with_comma
        else:
            decimal, frame = ".", with_dot

    return Parsed(
        frame,
        {
            "kind": "text",
            "encoding": encoding,
            "delimiter": delimiter,
            "decimal": decimal,
            "header_row": header_row,
        },
    )


# --- Excel ------------------------------------------------------------------


def detect_header_row(raw: pd.DataFrame) -> int:
    """First row where at least half the cells are filled (SPEC §14.4)."""
    for i in range(min(len(raw), 50)):
        if raw.iloc[i].notna().mean() >= 0.5:
            return i
    return 0


def parse_excel(path: Path, overrides: dict) -> Parsed:
    book = pd.ExcelFile(path, engine="openpyxl")
    sheets = book.sheet_names
    if not sheets:
        raise IngestError("The workbook has no sheets.")

    wanted = overrides.get("sheet")
    if wanted is not None and wanted not in sheets:
        raise IngestError(f"There is no sheet named '{wanted}'.")

    chosen = None
    raw = None
    for name in [wanted] if wanted else sheets:
        candidate = book.parse(name, header=None)
        if not candidate.dropna(how="all").empty:
            chosen, raw = name, candidate
            break
    if raw is None:
        raise IngestError("Every sheet in the workbook is empty.")

    header_row = overrides.get("header_row")
    header_row = int(header_row) if header_row is not None else detect_header_row(raw)
    if header_row >= len(raw):
        raise IngestError(f"Header row {header_row} is past the end of the sheet.")

    header = raw.iloc[header_row].tolist()
    frame = raw.iloc[header_row + 1 :].reset_index(drop=True)
    frame.columns = [("" if pd.isna(h) else str(h)) for h in header]
    frame = frame.dropna(how="all")

    return Parsed(
        frame,
        {
            "kind": "excel",
            "sheet": chosen,
            "sheets": sheets,
            "header_row": header_row,
        },
    )


# --- shared -----------------------------------------------------------------


def normalise_columns(frame: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Strip and collapse whitespace, name blanks, and de-duplicate. Returns
    the frame and the original names in order."""
    originals = [str(c) for c in frame.columns]
    seen: dict[str, int] = {}
    names: list[str] = []
    for i, original in enumerate(originals):
        name = re.sub(r"\s+", " ", original).strip()
        if not name or name.lower().startswith("unnamed:"):
            name = f"column_{i + 1}"
        base = name
        while name in seen:
            seen[base] += 1
            name = f"{base}_{seen[base]}"
        seen.setdefault(name, 1)
        names.append(name)
    frame = frame.copy()
    frame.columns = names
    return frame, originals


def _normalise_number_strings(values: pd.Series, decimal: str) -> pd.Series:
    def one(v: str) -> str:
        v = v.strip()
        if GROUPED_TR.match(v):
            return v.replace(".", "").replace(",", ".")
        if GROUPED_EN.match(v):
            return v.replace(",", "")
        if decimal == "," and "," in v and "." not in v:
            return v.replace(",", ".")
        return v

    return values.map(one)


def coerce_series(series: pd.Series, decimal: str = ".") -> tuple[pd.Series, str]:
    """Return the series in its canonical dtype and the profile type name:
    integer | number | date | boolean | string. A string column may still be
    promoted to 'period' by `mark_periods`; its dtype stays string."""
    non_null = series.dropna()
    if non_null.empty:
        return series.astype("string"), "string"

    if pd.api.types.is_bool_dtype(series):
        return series.astype("boolean"), "boolean"
    if pd.api.types.is_datetime64_any_dtype(series):
        out = pd.to_datetime(series, errors="coerce")
        if getattr(out.dt, "tz", None) is not None:
            out = out.dt.tz_convert(None)
        return out, "date"
    if pd.api.types.is_integer_dtype(series):
        return series.astype("Int64"), "integer"
    if pd.api.types.is_float_dtype(series):
        if (non_null % 1 == 0).all():
            return series.round().astype("Int64"), "integer"
        return series.astype("float64"), "number"

    # Text (or mixed) values. Try booleans, then numbers, then dates, in that order.
    text = non_null.astype(str).str.strip()
    lowered = text.str.lower()
    if lowered.isin(BOOL_WORDS.keys()).all():
        mapped = series.astype(object).where(series.notna(), None)
        mapped = mapped.map(lambda v: BOOL_WORDS[str(v).strip().lower()] if v is not None else None)
        return mapped.astype("boolean"), "boolean"

    numeric = pd.to_numeric(_normalise_number_strings(text, decimal), errors="coerce")
    if numeric.notna().all():
        full = pd.Series(pd.NA, index=series.index, dtype="Float64")
        full.loc[numeric.index] = numeric.values
        if (numeric % 1 == 0).all():
            return full.round().astype("Int64"), "integer"
        return full.astype("float64"), "number"

    if text.map(lambda v: bool(DATE_LIKE.match(v))).mean() >= 0.95:
        parsed = pd.to_datetime(text, errors="coerce", dayfirst=True, format="mixed")
        if parsed.notna().mean() >= 0.95:
            full = pd.Series(pd.NaT, index=series.index, dtype="datetime64[ns]")
            full.loc[parsed.index] = parsed.values
            return full, "date"

    # Text is trimmed, non-breaking spaces included: "LN" and "LN " are one value,
    # and a cell of spaces is empty.
    out = (
        series.astype(object)
        .where(series.notna(), None)
        .map(lambda v: None if v is None else (str(v).replace("\xa0", " ").strip() or None))
    )
    return out.astype("string"), "string"


def coerce_frame(frame: pd.DataFrame, decimal: str = ".") -> tuple[pd.DataFrame, dict[str, str]]:
    out = pd.DataFrame(index=frame.index)
    types: dict[str, str] = {}
    for column in frame.columns:
        out[column], types[column] = coerce_series(frame[column], decimal)
    return out, types


def date_links(types: dict[str, str], wanted: dict) -> dict[str, dict]:
    """The user's "this column is dated by those columns" links that still hold
    after this read: the dated column is text, the start (and end) are numbers."""
    links: dict[str, dict] = {}
    for column, link in wanted.items():
        start, end = link.get("start"), link.get("end") or None
        numeric = all(types.get(c) in {"integer", "number"} for c in (start, end) if c)
        if types.get(column) in {"string", "period"} and start and numeric:
            links[column] = {"start": start, "end": end, "bc": bool(link.get("bc"))}
    return links


def mark_periods(
    frame: pd.DataFrame, types: dict[str, str], wanted: dict, dated: dict | None = None
) -> tuple[dict[str, str], dict[str, list[str]]]:
    """Text columns that hold archaeological periods become type 'period'
    (SPEC §6.1 step 6). `wanted` is the user's say per column: a list is their
    own order, True forces the type, False forbids it, absent means detect.
    A column the user dated from other columns (`dated`) is a period column.
    Returns the types and the user-given orders that were applied."""
    types = dict(types)
    orders: dict[str, list[str]] = {}
    for column, kind in types.items():
        if kind != "string":
            continue
        choice = wanted.get(column)
        if column in (dated or {}) and not isinstance(choice, list):
            choice = True
        if choice is False:
            continue
        if isinstance(choice, list):
            types[column] = "period"
            orders[column] = [str(v) for v in choice]
        elif choice is True or looks_chronological(frame[column].dropna().unique(), column):
            types[column] = "period"
    return types, orders


def enforce_limits(frame: pd.DataFrame, limits: Limits) -> None:
    if len(frame.columns) > limits.max_columns:
        raise IngestError(
            f"The file has {len(frame.columns)} columns; the limit is {limits.max_columns}."
        )
    if len(frame) > limits.max_rows:
        raise IngestError(f"The file has {len(frame):,} rows; the limit is {limits.max_rows:,}.")
    if len(frame) == 0:
        raise IngestError("The file has a header but no data rows.")


def parse_file(path: Path, filename: str, overrides: dict, limits: Limits) -> Parsed:
    """The whole of §6.1 except writing to disk."""
    kind = kind_of(filename)
    parsed = (
        parse_text(path.read_bytes(), overrides) if kind == "text" else parse_excel(path, overrides)
    )
    frame, originals = normalise_columns(parsed.frame)
    enforce_limits(frame, limits)
    frame, types = coerce_frame(frame, parsed.parse_options.get("decimal", "."))
    links = date_links(types, overrides.get("period_dates") or {})
    types, period_orders = mark_periods(frame, types, overrides.get("periods") or {}, links)
    parsed.parse_options["period_dates"] = links
    parsed.parse_options["original_columns"] = originals
    parsed.parse_options["types"] = types
    parsed.parse_options["period_orders"] = period_orders
    parsed.parse_options["period_mappings"] = overrides.get("period_mappings") or {}
    return Parsed(frame, parsed.parse_options)
