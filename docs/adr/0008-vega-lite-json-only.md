# ADR 0008: Charts are Vega-Lite v6 JSON with data supplied at render time

Date: 2026-09-08. Status: accepted.

Specs are stored as JSONB with `data: {name: "main"}` and never HTML. The browser supplies the rows. This removes the v1 XSS surface, keeps specs portable, and makes revisions diffable. Validation strips anything that would carry data (`values`, `url`, `datasets`, loading transforms) and refuses `layer`, `concat`, `repeat`, and `facet` in v2.
