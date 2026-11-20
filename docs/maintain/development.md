# Development

How to run Chart-er from source, test it, and find your way around. For running it as a finished system, `docker compose` in the [README](../../README.md#running-it) is all you need.

## Two ways to run it

**Compose, everything built.** Closest to the server. Rebuild after every change.

```sh
cp deploy/.env.example deploy/.env      # set SECRET_KEY, POSTGRES_PASSWORD, FERNET_KEY
APP_VERSION=$(git rev-parse --short HEAD) docker compose -f deploy/compose.yml up --build -d
# http://localhost:8080
```

**From source, with reload.** Three processes and a database. This is the one to use while changing code.

```sh
# 1. A database. Any PostgreSQL 14 or newer; this one matches CI.
docker run -d --name charter-pg -p 5432:5432 \
  -e POSTGRES_DB=charter -e POSTGRES_USER=charter -e POSTGRES_PASSWORD=charter postgres:16

# 2. Backend. Python 3.11 or newer; the image and CI use 3.12.
python3 -m venv .venv && . .venv/bin/activate
pip install -e "backend[dev]"
export SECRET_KEY=dev
export FERNET_KEY=$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')
export DATABASE_URL=postgres://charter:charter@localhost:5432/charter
cd backend
python manage.py migrate
python manage.py runserver 127.0.0.1:8000      # terminal 1: the API
python manage.py runworker                     # terminal 2: parses uploads, calls the model

# 3. Frontend. Node 22.
cd frontend && npm ci
npm run dev                                    # terminal 3: http://localhost:5173
```

The Vite dev server proxies `/api` to `127.0.0.1:8000` (`frontend/vite.config.ts`), so the browser sees one origin, as it does behind Caddy.

Things that will catch you:

- **Keep `FERNET_KEY` the same between runs** (put the exports in a file you source). A new key makes the API key stored in Settings unreadable, and you have to enter it again.
- **Nothing happens after an upload or "Create chart"** means the worker is not running. The API only inserts a row with status `pending`; the worker does the work.
- **The worker does not reload.** Restart it after changing anything under `datasets/` or `generation/`.
- **A local model** (`http://127.0.0.1:11434/v1`) needs `export ALLOW_PRIVATE_ENDPOINTS=true`, for the API and the worker both.
- `pip install -e` leaves `backend/build/` and `backend/charter.egg-info/` behind. Both are ignored by git.

`python manage.py createsuperuser` gives you a login for `/admin`.

## Tests

```sh
cd backend && pytest -q                 # needs DATABASE_URL, SECRET_KEY, FERNET_KEY as above
ruff check backend && ruff format --check backend
python backend/manage.py makemigrations --check --dry-run
cd frontend && npm run check && npm test && npm run build
```

CI (`.github/workflows/ci.yml`) runs exactly these on every push to `main` and on pull requests, plus `docker compose build`. If they pass locally, CI passes.

What the backend tests cover, by file:

| File | Covers |
|---|---|
| `test_ingest.py`, `test_profile.py` | reading files: delimiters, decimal commas, cp1254, Excel header rows, limits, types |
| `test_chronology.py` | period names and dates, in three languages, by region; what must *not* be read as a period |
| `test_prompt.py` | the messages built for the model, compared with stored snapshots |
| `test_validate.py` | checking and correcting the model's answer |
| `test_generation.py`, `test_worker.py` | a whole revision from request to stored record; two workers never take the same job |
| `test_provider.py`, `test_model_config.py` | the HTTP call, error messages, refused endpoints, key storage |
| `test_datasets.py`, `test_auth.py`, `test_health.py` | the API; one user cannot read another's data |
| `test_replay.py` | replaying a bundle |

No test calls a real model. `tests/stub_provider.py` is a small HTTP server that answers like one.

**Prompt snapshots.** `tests/snapshots/{version}_{level}.txt` hold the exact text sent to the model. A test fails when the text changes by a single character, which is the point: a prompt never changes by accident. When you meant the change, see [Changing things](changing.md#the-prompt).

## Where things live

```
backend/
  charter/      settings.py (every tunable number is here), urls.py, api.py (router + /health)
  accounts/     users, login, the model settings, crypto.py (Fernet), validators.py
  datasets/     api.py, ingest.py (reading files), profile.py, chronology.py + periodo.py (periods),
                tasks.py (the worker's dataset job), examples/ (the "Try an example" files)
  charts/       models.py (Chart, ChartRevision), api.py, export.py (the bundle)
  generation/   prompt.py, provider.py (the one HTTP call), validate.py, intent.py,
                periods.py ("ask the model"), tasks.py (the worker's revision job),
                management/commands/runworker.py, replay.py
  prompts/      one Markdown file per prompt version; the Vega-Lite schema
  tests/
frontend/src/
  routes/       one folder per page; +layout.ts is the login guard
  lib/api.ts    every call to the backend, typed
  lib/i18n/     en.ts and tr.ts: every string on screen
  lib/components/
deploy/         compose.yml, Caddyfile, backup.sh, restore.sh, .env.example
docs/           this wiki, architecture.md, adr/, openapi.json
```

The request paths through these files are drawn in [architecture.md](../architecture.md).

## Conventions

- **Every dependency has a written reason.** SPEC §3 lists them. A new one needs a record in `docs/adr/` first.
- **The API layer owns access control.** Every queryset is filtered by `request.user`. A new endpoint that returns data needs a test that a second user gets a 404.
- **Messages a user sees are written for the user.** An exception that reaches the screen says what to do (`Endpoint returned 401: check your API key.`).
- **No string in a component.** Text goes in `en.ts` and `tr.ts`; `tr.ts` is typed against `en.ts`, so a missing translation is a type error.
- **Commits** are small and say what changed in the imperative. `main` is the only branch; CI must be green before a deploy.
