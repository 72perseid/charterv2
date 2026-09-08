# ADR 0005: pandas and openpyxl for tabular parsing

Date: 2026-09-08. Status: accepted.

Delimiter sniffing, decimal-comma handling, encoding fallbacks, Excel sheets, and type inference are solved problems in pandas, and every reviewer can read a `read_csv` call. The v1 pipeline effectively wrote its own CSV parser inside a low-code tool and hit base64 size limits on xlsx.

Note: pandas 3 is what the image ships; its default string dtype is backed by pyarrow (see ADR 0001).
