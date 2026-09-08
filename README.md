# Chart-er

A tabular dataset and a sentence in; a Vega-Lite chart, and the full record of how it was produced, out.

Chart-er is built for archaeologists and students who work in Excel and have never written a plotting script. A signed-in user uploads a CSV or Excel file, picks columns, describes the chart in plain language, and a language model of the user's choosing, paid for with the user's own key, writes the Vega-Lite specification. Every revision is stored with the exact request that produced it.

The design is written up in [SPEC.md](SPEC.md). This README grows with each build step.

## What leaves the server

Only the dataset profile (column names, inferred types, null and distinct counts, ranges, top categorical values) is sent, and only to the model endpoint the user configured. Raw rows are never sent unless the user switches a dataset to *sample* mode, which adds ten rows chosen with a fixed seed.

## Running it

Requirements: Docker with the Compose plugin.

```sh
cp deploy/.env.example deploy/.env      # then set SECRET_KEY, POSTGRES_PASSWORD, FERNET_KEY
APP_VERSION=$(git rev-parse --short HEAD) docker compose -f deploy/compose.yml up --build -d
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

## Model access

Each user stores an OpenAI-compatible base URL, a model name, and their own API key under Settings. The server makes one HTTP call to `{base_url}/chat/completions`; there is no vendor SDK and no key of Chart-er's own. Keys are encrypted at rest with the operator's `FERNET_KEY`, which means the operator can decrypt them. By default the server only calls `https://` endpoints on public hosts; set `ALLOW_PRIVATE_ENDPOINTS=true` to point it at a local model.

## Generating a chart

The worker builds a prompt from the template in `backend/prompts/` (versioned; `p2026-09-a` today), the dataset profile at the dataset's privacy level, the chosen fields, and the request. It asks for a JSON object, validates the answer against the vendored Vega-Lite v6 schema, replaces or drops encodings that name fields the dataset does not have, strips anything that would carry data, and refuses layered or concatenated specs. One retry with the validation error appended, then `failed` with the reason. Every revision keeps the exact messages sent, the parameters after any per-endpoint adjustments, the raw response, model, endpoint host, temperature, seed, prompt version, app version, token usage, and timings.

## Reproducibility bundle

Every chart page offers a bundle download: one JSON file (`charter-bundle/1`) with the chart, the dataset's profile and parse options, and every revision with its stored request, raw response, validated specification, corrections, model, endpoint host, temperature, seed, prompt version, app version, token usage, cost, and timings. Together with the original file it is enough to re-run or audit any revision.

## Files

CSV, TSV, and xlsx up to 20 MB, 100 000 rows, 200 columns. Text files are decoded as UTF-8, then Windows-1254 (Turkish), then Latin-1. The delimiter is sniffed among `, ; tab |`; a semicolon implies a decimal comma, otherwise the decimal mark is detected. Dates are read day-first. Grouped numbers such as `1.250,50` are understood. For xlsx the first non-empty sheet is used and the header is the first row with at least half its cells filled; both can be overridden on the dataset page. Every choice is recorded with the dataset.

## Status

Build step 5 of 6 (viewer: revision list and form, current revision, PNG/SVG/JSON export, reproducibility bundle). See SPEC.md §12.

## License

MIT.
