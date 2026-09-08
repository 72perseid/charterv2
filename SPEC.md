# Chart-er — Specification v2

2026-09-07 · Supersedes `SPEC-v1-lovable.md` (kept as the record of the Lovable/Supabase/n8n prototype). Decisions are stated with their reasons. Assumptions are marked *assumed* and collected in §14.

---

## 1. What Chart-er is

Chart-er turns a tabular dataset and a sentence into a Vega-Lite chart, and keeps the full record of how each chart was produced.

A signed-in user uploads a CSV or Excel file. Chart-er profiles it (column names, inferred types, basic statistics), the user picks an x column, a y column, optionally a grouping column, and describes the chart in plain language. The server asks a language model, chosen and paid for by the user, for a Vega-Lite specification, validates it, stores it, and the browser renders it. The user revises the chart by changing the description; each revision is stored with the exact request that produced it, so any chart can be traced back to its inputs.

The intended audience is archaeologists and students in Turkey who work in Excel and have never written a plotting script. The intended venue is a conference presentation and a public GitHub repository. The design should also survive becoming a small hosted product for students and researchers, which is why accounts exist.

Out of scope for v2: the phytolith research module from v1, model fine-tuning of any kind, and in-country language-model hosting. The last one is planned as a later project; v2 must make it a configuration change rather than a rewrite.

---

## 2. Decisions and reasons

The v1 prototype was recognisable as generated code: React + Vite + shadcn, a Tailwind utility soup, a fifty-file UI kit, TanStack Query installed and unused, and a pipeline outsourced to a low-code tool. v2 has a rule: every dependency and every framework is there because we can say in one sentence why the alternative was worse. Those sentences are below.

| Area | Decision | Why, and what was rejected |
|---|---|---|
| Backend language | Python 3.12 | The owner and the reviewers read Python. The data-handling libraries archaeologists already know live here. TypeScript on Deno was rejected because it only made sense inside Supabase's edge runtime, which is gone. |
| Web framework | Django 5.2 LTS | Auth, sessions, migrations, ORM, admin, file storage, and test client are first-party, so the backend has one framework and no glue. LTS is supported until April 2028, which outlives the conference and the paper. FastAPI was rejected: it is the current default for generated Python services and would need SQLAlchemy, Alembic, an auth library, and an admin bolted on. |
| API layer | django-ninja | Typed request/response schemas and an OpenAPI document for free, in about a tenth of the code of Django REST Framework. The OpenAPI document goes in the repository as documentation. |
| Database | PostgreSQL 16 on the same VPS | JSONB for specs, profiles, and request records; `SKIP LOCKED` for the job queue; one backup target. SQLite was rejected because the app is multi-user and the worker and web processes write concurrently. |
| Background work | A Django management command (`runworker`) that claims rows from `chart_revisions` with `SELECT … FOR UPDATE SKIP LOCKED` | Model calls take 5–30 s and must not hold a web request. A Postgres-backed queue in ~80 readable lines avoids Redis and Celery entirely. If the queue ever needs priorities or scheduling, django-q2 with the ORM broker is the drop-in upgrade. |
| Tabular parsing | pandas 2 + openpyxl | Delimiter sniffing, decimal-comma handling, encoding fallbacks, Excel sheets, and type inference are solved problems in pandas, and every reviewer can read a `read_csv` call. Writing our own CSV parser (as the n8n flow effectively did) was rejected. |
| Model access | Bring your own key. Each user stores an OpenAI-compatible base URL, model name, and API key. The server calls `POST {base_url}/chat/completions` with `httpx`. | Removes Chart-er's cost exposure; lets a user point at OpenAI, Anthropic's compatibility endpoint, OpenRouter, a local Ollama or vLLM, or a Turkish provider later, with no code change. This is the seam for the in-country hosting project. Vendor SDKs were rejected: one HTTP call does not need one. |
| What the model sees | A dataset profile: column names, inferred types, null and distinct counts, numeric and date ranges, top categorical values. Raw sample rows are off by default and require an explicit per-dataset opt-in. | Vega-Lite generation needs field names, types, and cardinalities, not cell values. This lets the conference talk say precisely what leaves the machine. |
| Chart storage | Vega-Lite v6 spec as JSONB with `data: {name: "main"}`; the browser supplies the rows at render time. Never HTML. | Removes the v1 XSS surface, keeps specs portable, and makes revisions diffable. |
| Rendering | `vega-embed` in the browser | Same library v1 used, without an iframe. PNG/SVG export comes with it. |
| Frontend | SvelteKit (Svelte 5), `adapter-static`, TypeScript, hand-written CSS with custom properties. No component library, no Tailwind. | Small, readable, and not the generated-app default. Static output means one fewer server process; Caddy serves the files and proxies `/api`. Vite is present only as SvelteKit's build tool; the v1 objection was to the React/shadcn application layer, not to a bundler. Angular was rejected as heavier than the problem. |
| Auth | Django's `contrib.auth` with email as the username, session cookies, CSRF | Nothing to add. Email verification is a setting that switches on when SMTP is configured (*assumed off for the demo*). |
| Secrets at rest | User API keys encrypted with Fernet (`cryptography`) under a server key in the environment | Plaintext keys in a database on a rented VPS are not acceptable. The operator can still decrypt; the README says so. |
| File storage | Local disk under `DATA_DIR/{user_id}/{dataset_id}/`, served only through an authenticated Django view | The v1 public bucket was the shortcut n8n needed. Nothing here is public. |
| Deployment | Docker Compose: `postgres`, `api` (gunicorn), `worker`, `caddy`. One `compose.yml`, one `.env`. | A reviewer runs `docker compose up` and has the whole system. The same file runs on the VPS. |
| Status updates | Client polls the revision endpoint every 2 s while a revision is pending or running | Boring and sufficient. Server-sent events are a later refinement, not a requirement. |
| Naming | "Revision", not "fine-tune" | The v1 name described model fine-tuning, which this is not. Reviewers would flag it. |

---

## 3. Dependencies

Backend (`pyproject.toml`):

| Package | Role |
|---|---|
| django 5.2 | framework |
| django-ninja | API schemas and OpenAPI |
| psycopg[binary] 3 | Postgres driver |
| pandas, openpyxl | CSV/xlsx parsing and profiling |
| httpx | model API calls |
| jsonschema | Vega-Lite spec validation against the vendored v6 schema |
| cryptography | Fernet for API keys |
| gunicorn | WSGI server |
| pytest, pytest-django | tests |
| ruff | lint and format |

Frontend (`package.json`):

| Package | Role |
|---|---|
| svelte 5, @sveltejs/kit, @sveltejs/adapter-static | framework |
| vega, vega-lite, vega-embed | rendering |
| typescript, vite | tooling (Vite is SvelteKit's build tool) |
| vitest | tests |

Anything not in these tables needs a written reason in `docs/adr/` before it is added.

---

## 4. Architecture

```
Browser ── HTTPS ──> Caddy
                      ├── /            static SvelteKit build
                      ├── /api/*       gunicorn (Django + ninja)
                      └── /files/*     gunicorn (auth check, then X-Accel to DATA_DIR)

gunicorn ──── Postgres ◄──── worker (manage.py runworker)
    │                            │
    └── DATA_DIR (disk) ◄────────┘
                                 └── httpx ──> user's model endpoint
```

Chart-er's processes on the VPS: `postgres`, `api`, `worker`, `caddy`. Nothing else belongs to Chart-er; the host Caddy in front of them is described in §9.

Request path for a new chart: browser `POST /api/charts` → Django validates, inserts `charts` + `chart_revisions` (status `pending`) → returns `201` with ids → worker claims the revision, sets `running`, builds the prompt from the stored dataset profile, calls the model, validates the spec, sets `done` or `failed` → browser polls `GET /api/revisions/{id}` and renders when `done`.

---

## 5. Data model

Django models; the migration is generated from these. Column notes are the contract.

```
User (django.contrib.auth, custom model)
  id uuid PK · email unique (login) · display_name · is_active · date_joined

ModelConfig                       -- one row per user; the BYOK settings
  user 1:1 · base_url text · model text · api_key_encrypted bytea
  temperature float default 0 · created_at · updated_at

Dataset
  id bigint PK · user FK cascade · name text
  original_filename text · original_path text        -- DATA_DIR/{user}/{dataset}/original.{csv|xlsx}
  parsed_path text                                   -- .../parsed.parquet  (canonical rows)
  sheet_name text null                               -- xlsx only
  parse_options jsonb                                -- {delimiter, decimal, encoding, header_row, sheet}
  profile jsonb                                      -- see §6.2
  row_count int · column_count int · size_bytes int
  privacy_level text default 'statistics'            -- 'minimal' | 'statistics' | 'sample'
  status text default 'pending'                      -- pending | running | done | failed
  error_message text null · created_at

Chart
  id bigint PK · user FK cascade · dataset FK cascade
  title text · current_revision FK null (set null) · created_at

ChartRevision
  id bigint PK · chart FK cascade · user FK cascade
  revision_no int · parent FK null (set null)        -- unique (chart, revision_no)
  x_field text · y_field text · color_field text null
  prompt text (≤ 1000 chars)
  status text default 'pending'                      -- pending | running | done | failed
  attempts int default 0 · error_message text null
  spec jsonb null                                    -- validated Vega-Lite v6, data: {name: 'main'}
  -- reproducibility record, written by the worker:
  request jsonb null      -- exact messages array + parameters sent to the model
  response_text text null -- raw model output before any parsing
  model text · endpoint_host text · temperature float · seed int null
  prompt_version text     -- e.g. 'p2026-09-a'; the template id in prompts/
  app_version text        -- git sha at run time
  usage jsonb null        -- token counts if the provider returns them
  started_at · finished_at · duration_ms · created_at
```

Indexes: `chart_revisions (status, created_at)` for the worker claim; `datasets (user, created_at)`; `charts (user, created_at)`.

Access rules are enforced in the API layer: every queryset is filtered by `request.user`. There is no row-level security to configure because there is no shared database client.

---

## 6. Pipeline

### 6.1 Ingest (worker, on dataset upload)

1. Detect kind by extension and magic bytes: `.csv`, `.tsv`, `.txt` → text; `.xlsx` → Excel. `.xls` is rejected with a message asking for xlsx.
2. Text: try encodings in order `utf-8-sig`, `utf-8`, `cp1254` (Turkish Windows), `latin-1`. Sniff delimiter over the first 20 lines among `, ; \t |`. If the delimiter is `;`, default `decimal=','`; otherwise detect by checking whether numeric-looking columns parse better with `,` or `.` as decimal. Record every choice in `parse_options`.
3. Excel: list sheets; use the first non-empty sheet unless the user chose one. Header row is the first row with ≥ 50% non-null cells (*assumed*); record it.
4. Limits: 20 MB upload, 100 000 rows, 200 columns (*assumed*). Above the limit: `failed` with a user-readable message.
5. Normalise column names (strip, collapse whitespace, keep original in profile), coerce types (integer, number, date, boolean, string), write `parsed.parquet`, compute the profile, set `done`.

### 6.2 Profile

Per column: `name`, `original_name`, `type`, `null_count`, `distinct_count`; for numbers `min max mean median`; for dates `min max`; for strings `top_values` (≤ 5 values with counts) and `max_length`. Dataset-level: `row_count`, `column_count`, `parse_options`.

What reaches the model by `privacy_level`:

| level | sent |
|---|---|
| `minimal` | column names, types, row count, null and distinct counts |
| `statistics` (default) | minimal + numeric/date ranges + top categorical values |
| `sample` | statistics + 10 rows chosen with a fixed seed |

The level is shown next to the prompt box every time, with a one-line description of what it means.

### 6.3 Generation (worker, on revision)

1. Claim: `UPDATE chart_revisions SET status='running', attempts=attempts+1, started_at=now() WHERE id = (SELECT id FROM chart_revisions WHERE status='pending' ORDER BY created_at FOR UPDATE SKIP LOCKED LIMIT 1) RETURNING *`.
2. Build messages from the template in `prompts/{prompt_version}.md`: system rules (§13), the profile at the dataset's privacy level, x/y/color fields, the user's prompt, and for revisions > 1 the parent's spec JSON and prompt.
3. Call the user's endpoint with `temperature` from `ModelConfig`, `response_format: json_object` when the provider accepts it, `seed` when it accepts it. Timeout 90 s.
4. Parse: strip code fences, `json.loads`. Validate: object; `$schema` is Vega-Lite v6; has `mark` and `encoding`; every `encoding.*.field` exists in the profile (else replace with the user's selection and record the correction); force `data = {name: 'main'}`; delete `datasets`, `transform[].url`, any `values`; reject `layer`, `concat`, `repeat`, `facet` in v2. Then `jsonschema.validate` against the vendored schema.
5. On validation failure: one retry with the validation error appended to the conversation. On second failure or any provider error: `failed` with a message a user can act on (`"Model returned text that is not JSON"`, `"Endpoint returned 401: check your API key"`).
6. Persist the full record (§5), set `done`, set `chart.current_revision` if this is the newest.

Every outcome writes one structured log line: revision id, user id, endpoint host, model, duration, tokens, outcome.

### 6.4 Rate limits

Per user: 60 revisions per hour, 20 dataset uploads per hour (*assumed*), enforced in the API with a count on `created_at`. The key is the user's own, so the limit protects the VPS, not a budget.

---

## 7. API

All under `/api`, session-cookie auth, CSRF header on unsafe methods, JSON in and out. OpenAPI at `/api/docs` in debug and committed to `docs/openapi.json`.

| Method and path | Purpose |
|---|---|
| `POST /auth/register` `POST /auth/login` `POST /auth/logout` `GET /auth/me` | accounts |
| `GET/PUT /me/model-config` · `POST /me/model-config/test` | BYOK settings; test makes one tiny call and reports the result |
| `GET /datasets` · `POST /datasets` (multipart) · `GET /datasets/{id}` · `PATCH /datasets/{id}` (name, privacy_level, sheet) · `DELETE /datasets/{id}` | datasets; POST returns immediately with status `pending` |
| `GET /datasets/{id}/rows?limit&offset` | parsed rows for the table view and for vega |
| `GET /datasets/{id}/download` | original file |
| `GET /charts` · `POST /charts` `{dataset_id, title, x_field, y_field, color_field, prompt}` · `GET /charts/{id}` · `PATCH /charts/{id}` (title, current_revision) · `DELETE /charts/{id}` | charts; POST creates revision 1 |
| `POST /charts/{id}/revisions` `{parent_id, x_field, y_field, color_field, prompt}` · `GET /revisions/{id}` | revisions; GET is the poll target |
| `GET /charts/{id}/export` | reproducibility bundle: dataset profile, parse options, every revision with request and response |

Errors are `{"detail": "..."}` with the right status. Delete cascades in the database and removes the dataset directory on disk in the same request.

---

## 8. Frontend

SvelteKit, static adapter, all routes client-rendered behind a `+layout.ts` that fetches `/api/auth/me` and redirects to `/login` when needed.

| Route | Content |
|---|---|
| `/` | Landing: what it does, how to run it, link to sign in. Plain page, no feature tiles. |
| `/login` `/register` | forms |
| `/datasets` | Table of the user's datasets: name, rows, columns, status, created. Upload button opens the upload form. |
| `/datasets/[id]` | Profile table (one row per column with type and stats), first 100 rows, privacy level control, sheet picker for xlsx, "New chart" form |
| `/charts` | Table of charts with dataset, current revision status, updated |
| `/charts/[id]` | The chart viewer: canvas, revision list down the side with status and prompt, revision form pre-filled from the selected revision, tabs for data and for the stored request/response, export PNG/SVG/JSON/bundle |
| `/settings` | Model configuration (base URL, model, key, temperature, test button), account, sign out |

Components, all hand-written: `AppShell` (one nav definition), `DataTable`, `UploadForm`, `ProfileTable`, `ChartCanvas` (wraps vega-embed, receives spec and rows, sets `data.values`), `RevisionList`, `RevisionForm`, `StatusChip`, `PrivacyLevel`.

State: Svelte 5 runes and plain `fetch` wrappers in `src/lib/api.ts`. No client-side cache library; the pages are small and polling is explicit.

Strings: every user-visible string lives in `src/lib/i18n/en.ts`; `tr.ts` is added in build step 6. No i18n library (*assumed acceptable*).

Design: keep the v1 tokens (teal primary `hsl(174 72% 45%)`, accent `hsl(174 60% 92%)`, success `hsl(142 71% 45%)`, warning `hsl(38 92% 50%)`, destructive `hsl(0 84% 60%)`, ground `hsl(0 0% 98%)`, radius 0.5rem) as CSS custom properties in `app.css`. Visual direction is decided separately and later; the spec only requires tabular numerals in data tables and a visible running state.

---

## 9. Deployment

`deploy/compose.yml` services: `postgres:16` with a named volume; `api` built from `backend/Dockerfile`, runs migrations then gunicorn; `worker` same image, command `manage.py runworker`; `caddy` with `deploy/Caddyfile` serving `frontend/build` and proxying `/api` and `/files`. The compose file is a complete system: a reviewer runs it on a laptop and the compose Caddy answers on port 8080, plain HTTP.

The stack publishes exactly one port, the compose Caddy, bound to `127.0.0.1:8080`. Postgres, `api`, and `worker` sit on a compose-internal network and publish nothing. The `.env` value `CADDY_BIND` sets the published address; the example file uses `127.0.0.1:8080`, and an operator who wants the compose Caddy to own TLS directly sets it to `:80` and `:443` with a hostname in the Caddyfile.

On the project VPS a Caddy service already owns 80 and 443 for another stack (a self-hosted Supabase, unrelated to Chart-er). Chart-er does not touch it beyond one site block appended to `/etc/caddy/Caddyfile`:

```
charter.72perseids.com {
    reverse_proxy localhost:8080
}
```

The host Caddy terminates TLS with automatic certificates; the compose Caddy serves the static frontend and proxies the API. Two proxies in series cost nothing measurable and keep the compose file identical between the VPS and a reviewer's machine. Chart-er never uses the Supabase Postgres or any other container on the box; sharing the host is a hosting detail, sharing a database would be a dependency.

Environment (`deploy/.env.example`): `SECRET_KEY`, `POSTGRES_PASSWORD`, `FERNET_KEY` (from build step 3), `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `CADDY_BIND`, `SECURE_COOKIES` (true once the public origin is https), `EMAIL_URL` (optional; enables verification), `REQUIRE_EMAIL_VERIFICATION`. `DATABASE_URL` and `DATA_DIR` are set inside `compose.yml`, not by the operator.

Email: no mail server runs on the box. `EMAIL_URL` points at an existing SMTP relay if verification is wanted (institutional SMTP or a transactional provider); until then verification is off, per §14.

Backups: nightly `pg_dump` and an rsync of `DATA_DIR` to off-box storage, via a cron line documented in the README. Restore is tested once before the conference.

VPS (confirmed 2026-09-08): Contabo, EU region, Ubuntu 24.04.4, 4 vCPU, 7.8 GB RAM, 96 GB disk, Docker 29 and Compose v5 preinstalled, x86_64. Chart-er's four containers need well under 1 GB of it. Location is not Turkey; the README states this and states what leaves the box (only the profile, to the user's chosen endpoint). Deploys run from the maintainer's machine over key-based SSH; the README also documents the manual path.

---

## 10. Testing and quality

Backend, pytest:
- `ingest`: delimiter and decimal detection, cp1254 file, xlsx with a title row above the header, limits.
- `profile`: types and stats on a fixture with nulls, dates in Turkish format, mixed numerics.
- `prompt`: message construction at each privacy level; snapshot the rendered prompt per `prompt_version`.
- `validate`: bad JSON, missing encoding, unknown field, forbidden `layer`, schema violation, the retry path.
- `worker`: claim with two workers does not double-process; failure sets `failed` with message.
- `api`: auth required everywhere; a user cannot read another user's dataset or revision; delete removes the directory.
- A stub provider (`tests/stub_provider.py`, a tiny HTTP server returning a canned spec) for an end-to-end test from upload to `done`.

Frontend, vitest: `api.ts` error mapping, `ChartCanvas` sets `data.values`.

CI (GitHub Actions): ruff, pytest with a Postgres service, `npm run check`, vitest, `docker compose build`.

`docs/adr/` holds one short record per decision in §2 so the reasoning survives the person who made it.

---

## 11. Repository layout

```
chart-er/
  backend/
    charter/            settings, urls, asgi/wsgi
    accounts/           user model, auth endpoints, ModelConfig
    datasets/           models, ingest.py, profile.py, endpoints
    charts/             models, endpoints, export
    generation/         prompt.py, validate.py, provider.py, worker command
    prompts/            p2026-09-a.md and successors; vega-lite-v6.schema.json
    tests/
    pyproject.toml  Dockerfile  manage.py
  frontend/
    src/routes/  src/lib/  src/app.css
    package.json  svelte.config.js
  deploy/
    compose.yml  Caddyfile  .env.example
  docs/
    architecture.md  openapi.json  adr/
  README.md  LICENSE (MIT)  CITATION.cff
```

---

## 12. Build order

1. **Skeleton.** Django project, custom user, session auth endpoints, SvelteKit shell with login and register, compose with Postgres and Caddy. *Exit: register, log in, see an empty datasets page, all via `docker compose up`.*
2. **Datasets.** Upload endpoint, worker command, ingest and profile with the test fixtures above, dataset pages with profile table and rows. *Exit: upload a Turkish semicolon CSV and an xlsx, see correct types and stats.*
3. **Model config.** Settings page, Fernet storage, test button against the stub provider and against a real endpoint. *Exit: a green "connected" with the user's key.*
4. **Generation.** Prompt template, provider call, validation, retry, reproducibility record, chart creation form, polling. *Exit: create a chart, watch pending → running → done, see the spec and the stored request.*
5. **Viewer and revisions.** ChartCanvas, revision list and form, switch current revision, exports, bundle download. *Exit: three revisions, switch between them, download the bundle and re-read it.*
6. **Hardening.** Rate limits, delete paths, Turkish strings, README with the data-flow statement, CITATION.cff, backups on the VPS, CI green. *Exit: a stranger can clone, run, and reproduce a chart from a bundle.*

---

## 13. Carried over from v1

Prompt rules (they worked): output JSON only; use the provided types, do not guess from values; add a color encoding when the request says group, by, per, or color, or when a color field is given; temporal x gets `timeUnit` and an axis format; categorical x with quantitative y defaults to `aggregate: sum` unless the request asks for raw points; fallbacks: temporal → line, nominal → bar, both quantitative → point; no `layer`, `concat`, `repeat`, `facet`.

Findings from v1 and where v2 closes them: unauthenticated functions and caller-supplied user ids (§7, session auth on every route); public bucket (§2 file storage); HTML from the model (§2 chart storage); status case mismatch and stuck jobs (§5 status enum, `attempts`, `error_message`); revisions that never saw the data (§6.3 profile in every prompt); incomplete deletion (§7 delete); undocumented access rules (§5 last paragraph); free-text axes (§8 selects from the profile); two clients and duplicated shell (§8 one `api.ts`, one `AppShell`).

---

## 14. Open questions, answered by assumption

| # | Question | Assumed |
|---|---|---|
| 1 | Interface language at launch | English strings, centralised; Turkish translation in build step 6. |
| 2 | Email verification | Off until SMTP is configured; open registration with rate limits. |
| 3 | Upload limits | 20 MB, 100 000 rows, 200 columns. |
| 4 | Excel header detection | First row with ≥ 50% non-null cells; user can override the header row. |
| 5 | Default privacy level | `statistics`. |
| 6 | Which providers are tested against | OpenAI and a local Ollama, both through the same OpenAI-compatible path. |
| 7 | VPS size and provider | Confirmed: Contabo EU, 4 vCPU / 7.8 GB / 96 GB. Disclosed in the README. |
| 8 | Domain name and TLS | Confirmed: `charter.72perseids.com`, TLS by the existing host Caddy. The A record moves off the v1 prototype after build step 1 passes on the VPS. |
| 9 | Do old v1 users, uploads, or charts migrate | No. |
| 10 | License and citation | MIT and a `CITATION.cff` naming the owner and the conference. |
