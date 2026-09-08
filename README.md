# Chart-er

A tabular dataset and a sentence in; a Vega-Lite chart, and the full record of how it was produced, out.

Chart-er is built for archaeologists and students who work in Excel and have never written a plotting script. A signed-in user uploads a CSV or Excel file, picks columns, describes the chart in plain language, and a language model of the user's choosing, paid for with the user's own key, writes the Vega-Lite specification. Every revision is stored with the exact request that produced it.

The design is written up in [SPEC.md](SPEC.md). This README grows with each build step.

## What leaves the server

Only the dataset profile (column names, inferred types, null and distinct counts, ranges, top categorical values) is sent, and only to the model endpoint the user configured. Raw rows are never sent unless the user switches a dataset to *sample* mode, which adds ten rows chosen with a fixed seed.

## Running it

Requirements: Docker with the Compose plugin.

```sh
cp deploy/.env.example deploy/.env      # then set SECRET_KEY and POSTGRES_PASSWORD
docker compose -f deploy/compose.yml up --build -d
open http://localhost:8080
```

The stack is four containers: PostgreSQL 16, the Django API, a worker that parses uploads and (from build step 4) calls the model, and Caddy serving the static frontend. Only Caddy publishes a port, on `127.0.0.1:8080` by default.

To create an admin user for `/admin`:

```sh
docker compose -f deploy/compose.yml exec api python manage.py createsuperuser
```

## Tests

```sh
docker compose -f deploy/compose.yml run --rm api pytest
docker compose -f deploy/compose.yml run --rm api ruff check .
cd frontend && npm ci && npm run check && npm test
```

## Files

CSV, TSV, and xlsx up to 20 MB, 100 000 rows, 200 columns. Text files are decoded as UTF-8, then Windows-1254 (Turkish), then Latin-1. The delimiter is sniffed among `, ; tab |`; a semicolon implies a decimal comma, otherwise the decimal mark is detected. Dates are read day-first. Grouped numbers such as `1.250,50` are understood. For xlsx the first non-empty sheet is used and the header is the first row with at least half its cells filled; both can be overridden on the dataset page. Every choice is recorded with the dataset.

## Status

Build step 2 of 6 (datasets: upload, worker, ingest, profile, dataset page). See SPEC.md §12.

## License

MIT.
