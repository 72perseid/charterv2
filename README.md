# Chart-er

A tabular dataset and a sentence in; a Vega-Lite chart, and the full record of how it was produced, out.

Chart-er is built for archaeologists and students who work in Excel and have never written a plotting script. A signed-in user uploads a CSV or Excel file, picks columns, describes the chart in plain language, and a language model of the user's choosing, paid for with the user's own key, writes the Vega-Lite specification. Every revision is stored with the exact request that produced it, so any chart can be traced back to its inputs and replayed.

The design and its reasons are in [SPEC.md](SPEC.md); one short record per decision is in [docs/adr](docs/adr/README.md); the map of the code is [docs/architecture.md](docs/architecture.md); the API is described by [docs/openapi.json](docs/openapi.json). The interface is in English and Turkish.

## What leaves the server

Chart-er sends one thing to one place: the **dataset profile** to the **model endpoint the user configured** with their own key. The profile is column names, inferred types, row count, null and distinct counts, and, at the default *statistics* level, numeric and date ranges and the five most frequent values of repeated text columns. Identifier columns contribute no values. Raw rows are never sent unless the user switches a dataset to *sample* mode, which adds ten rows chosen with a fixed seed and says so next to the prompt box every time.

The user's API key is stored encrypted with a server-side key held by the operator, who can therefore decrypt it. Nothing else is sent anywhere. The reference deployment runs on a rented server in the European Union, not in Turkey; that is a hosting choice, and the software runs unchanged wherever it is installed.

## Running it

Requirements: Docker with the Compose plugin. Nothing else.

```sh
cp deploy/.env.example deploy/.env      # then set SECRET_KEY, POSTGRES_PASSWORD, FERNET_KEY
APP_VERSION=$(git rev-parse --short HEAD) docker compose -f deploy/compose.yml up --build -d
open http://localhost:8080
```

Four containers: PostgreSQL 16, the Django API, a worker that parses uploads and calls the model, and Caddy serving the static frontend and proxying the API. Only Caddy publishes a port, on `127.0.0.1:8080` by default. Put your own TLS-terminating proxy in front of it, or set `CADDY_BIND` and a hostname in `deploy/Caddyfile` to let the compose Caddy own ports 80 and 443 itself.

Create an admin user for `/admin` with:

```sh
docker compose -f deploy/compose.yml exec api python manage.py createsuperuser
```

## Using it

1. **Settings.** Enter an OpenAI-compatible base URL and your API key; the model list loads from the provider, and prices fill in when the provider publishes them. Test the connection.
2. **Datasets.** Upload a CSV, TSV, or xlsx. The worker reads it and the page shows how: encoding, delimiter, decimal mark, sheet, header row, and a typed profile of every column. Override the sheet or header row if needed. Choose what the model may see.
3. **Charts.** On a dataset, pick the x, y, and optional colour columns, describe the chart, and create it. The page polls until the model has answered, renders the chart, and shows the specification and the exact request and response, with tokens and estimated cost.
4. **Revise.** Change the request or the columns; the model also sees the previous specification. Switch between revisions, make any of them current, export PNG, SVG, or the spec, and download the reproducibility bundle.

## Files

CSV, TSV, and xlsx up to 20 MB, 100 000 rows, 200 columns. Text files are decoded as UTF-8, then Windows-1254 (Turkish), then Latin-1. The delimiter is sniffed among `, ; tab |`; a semicolon implies a decimal comma, otherwise the decimal mark is detected. Dates are read day-first. Grouped numbers such as `1.250,50` are understood. For xlsx the first non-empty sheet is used and the header is the first row with at least half its cells filled. Every choice is recorded with the dataset.

## Generating a chart

The worker builds a prompt from the versioned template in `backend/prompts/` (`p2026-09-a` today), the profile at the dataset's privacy level, the chosen fields, and the request. It asks the endpoint for a JSON object with a fixed seed, validates the answer against the vendored Vega-Lite v6 schema, replaces encodings that name unknown fields with the user's choice or drops them, strips anything that would carry data, and refuses layered or concatenated specs. One retry with the validation error appended, then `failed` with the reason. Endpoints that reject a parameter by name (OpenAI's newer models want `max_completion_tokens` and refuse a temperature) get it renamed or dropped, and the adjustment is recorded.

## Reproducibility

Every chart page offers a bundle download: one JSON file (`charter-bundle/1`) with the chart, the dataset's profile and parse options, and every revision with its stored messages, raw response, validated specification, corrections, model, endpoint host, temperature, seed, prompt version, app version (the git commit), token usage, cost, and timings.

Anyone with a bundle and a key can replay a revision without an account or a database:

```sh
docker compose -f deploy/compose.yml run --rm -T api \
  python manage.py replay /tmp/charter-chart-12.json --revision 2 \
  --base-url https://api.openai.com/v1 --model gpt-4.1-mini --api-key sk-...
```

It sends the recorded messages with the recorded parameters, validates the answer the same way, and reports whether the specification is identical or where it differs. Identical output is not guaranteed by any provider; the point is that the comparison is possible and the inputs are exact.

## Backups

`deploy/backup.sh` writes a compressed `pg_dump`, a tarball of the data volume, and a copy of the env file into a dated directory, keeps the last fourteen, and syncs them off-box when `BACKUP_REMOTE` is set. `deploy/restore.sh <set>` puts a set back. Cron line for the host:

```
0 3 * * * /root/chart-er/deploy/backup.sh >> /var/log/charter-backup.log 2>&1
```

Losing `FERNET_KEY` makes every stored API key unreadable; the env copy in each backup set is there for that reason and must be kept as private as the database.

## Tests

```sh
docker compose -f deploy/compose.yml run --rm api pytest
docker compose -f deploy/compose.yml run --rm api ruff check .
cd frontend && npm ci && npm run check && npm test
```

Continuous integration runs the same on every push: ruff, pytest against PostgreSQL, the migration check, svelte-check, vitest, the frontend build, and a compose build.

## Limits

Per user: 20 uploads and 60 revisions per hour. No email verification until an SMTP relay is configured (`EMAIL_URL`); registration is otherwise open. The server refuses `http://` and private-network model endpoints unless `ALLOW_PRIVATE_ENDPOINTS=true`.

## Status

All six build steps of SPEC.md §12 are done. Visual design is deliberately plain until decided separately.

## License

MIT.
