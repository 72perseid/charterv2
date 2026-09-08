# ADR 0007: The model sees a profile, not rows

Date: 2026-09-08. Status: accepted.

Vega-Lite generation needs field names, types, and cardinalities, not cell values. By default the model receives column names, inferred types, null and distinct counts, numeric and date ranges, and the top categorical values. Raw sample rows require an explicit per-dataset opt-in. Identifier columns (every value unique) contribute no top values. This lets the conference talk say precisely what leaves the machine.
