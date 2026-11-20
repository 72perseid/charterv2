# Architecture

Chart-er is four processes behind one reverse proxy. See `SPEC.md` for the reasoning behind each choice; this page is the map.

```
Browser ── HTTPS ──> Caddy (compose)          ┐ published on 127.0.0.1:8080;
                      ├── /            static SvelteKit build      │ the host's own proxy
                      ├── /api/*       gunicorn (Django + ninja)    │ terminates TLS in front
                      ├── /admin/*     gunicorn                     │
                      └── /static/*    Django admin assets          ┘

gunicorn ──── PostgreSQL 16 ◄──── worker (manage.py runworker)
    │                                  │
    └── DATA_DIR (disk volume) ◄───────┘
                                       └── httpx ──> the user's model endpoint
```

## Request paths

**Upload.** `POST /api/datasets` stores the original file under `DATA_DIR/{user}/{dataset}/` and inserts a row with status `pending`. The worker claims it with `SELECT … FOR UPDATE SKIP LOCKED`, parses it (`datasets/ingest.py`), marks period columns and works out their chronological order from the vendored PeriodO snapshot (`datasets/chronology.py`, `datasets/periodo.py`), writes `parsed.parquet`, computes the profile (`datasets/profile.py`), and sets `done` or `failed` with a message.

**Chart.** `POST /api/charts` inserts a chart and its revision 1 (`pending`). The worker claims the revision, builds the prompt from `backend/prompts/{version}.md` and the profile at the dataset's privacy level (`generation/prompt.py`), calls `{base_url}/chat/completions` once (`generation/provider.py`), validates the answer and applies what the user chose in the form (`generation/validate.py`, `generation/intent.py`), retries once with the error appended, and stores the full record. The browser polls `GET /api/revisions/{id}` every two seconds.

**Render.** The stored spec has `data: {name: "main"}` and no values. The browser fetches rows from `GET /api/datasets/{id}/rows` and hands both to vega-embed.

## Where things live

| Concern | Backend | Frontend |
|---|---|---|
| Accounts, model config, key encryption | `accounts/` | `routes/login`, `routes/register`, `routes/settings` |
| Datasets, ingest, period order, profile, rows | `datasets/` | `routes/datasets` |
| Charts, revisions, export bundle | `charts/` | `routes/charts` |
| Prompt, provider call, validation, worker | `generation/`, `prompts/` | — |
| Strings | — | `lib/i18n/` (`en.ts`, `tr.ts`) |
| Documentation on the site | — | `routes/docs`, `lib/docs.ts`; the text is `docs/guide/` and `docs/maintain/` |
| The one HTTP client | — | `lib/api.ts` |

## Access rules

Every queryset is filtered by the session user in the API layer. There is no row-level security to configure because there is no shared database client. Files are served only through authenticated Django views.

## What leaves the box

The dataset profile, filtered by privacy level, and only to the endpoint the user configured with their own key. One more thing on an explicit click: the distinct values of a single period column, to the same endpoint, when the user asks the model to place them (`generation/periods.py`). See `README.md`.
