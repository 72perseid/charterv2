# Chart-er — Rebuild Specification

Version 1.0 · 2026-09-07 · Derived from the Lovable checkout at `~/chart-er/charterr`, the two n8n exports in `~/n8n-workflows/`, and the README. Decisions are stated as decisions; assumptions are marked. Open questions are collected at the end.

---

## 1. What Chart-er is

Chart-er is a small research web app with two halves that share one backend:

1. **AI chart generator.** A signed-in user uploads a CSV, names an x column, a y column, and describes the chart in plain language. The system asks an LLM for a Vega-Lite spec, renders it in the browser, and lets the user iterate ("fine-tune") until it is right.
2. **Phytolith research module.** A public, read-only browser for archaeological phytolith data from Kinet Höyük: excavation contexts, microscope slides, morphotype counts per slide, and slide photographs. From any context, a user can push the count data into the chart generator with one click.

The README positions it as reproducible, auditable, and JOSS-friendly. The rebuild keeps that framing and removes the piece that undermines it: the n8n dependency and the hardcoded service key inside it.

Audience: the owner and collaborators (archaeology / lab), plus reviewers who need to run it from source.

---

## 2. The system as it exists today

### 2.1 Stack

| Layer | Today |
|---|---|
| Frontend | Vite 5, React 18, TypeScript, Tailwind 3, shadcn/ui, react-router 6, TanStack Query (installed, unused), Recharts (phytolith chart), sonner toasts |
| Auth / DB / Storage | Supabase project `wuirlyjwzbrtctbjdlir`, bucket `publicbckt` (public) |
| Edge functions | `charter-job`, `fine-tune` (Deno, `verify_jwt = false`), retry wrapper, forward to n8n |
| Pipeline | n8n workflows `chart-er v2` and `chart-er Fine Tune`, OpenAI `gpt-4.1-mini`, Supabase REST via hardcoded service_role JWT |
| Hosting | Lovable preview |

### 2.2 Data model (from generated `types.ts` and migrations)

Chart tables:

| Table | Columns | Notes |
|---|---|---|
| `uploads` | id bigint PK, created_at, user_id uuid, upload text (public URL), file_name text | All nullable except id |
| `jobs` | id, created_at, upload_id → uploads, user_id, xaxis, yaxis, prompt, completed text, response text (full HTML page), json text (storage URL of converted dataset) | `completed` is free text: UI writes "Pending", n8n writes "done" |
| `fine_tuning` | id, created_at, job_id → jobs, user_id, xaxis, yaxis, prompt, result text (HTML) | Created by n8n, not by the client |

Phytolith tables (RLS enabled, public SELECT for anon + authenticated):

| Table | Columns |
|---|---|
| `contexts` | kinet_no bigint PK, period_name, phase, context, op, munsell, lot, locus, type |
| `slides` | slide_id PK, kinet_no → contexts, phy_per_slide, phy_in_pellets, weight_pellet, weight_on_slide, notes, starting_coord, photo_ids bigint[] |
| `morphotypes` | morphotype_id PK, name, category |
| `counts` | count_id PK, slide_id → slides, morphotype_id → morphotypes, count, column_no |
| `phyto_photos` | id identity PK, kinet_no → contexts, storage_path unique, url, folder_suffix, is_diagnostic, created_at |

Leftovers to drop: `chat_messages`, `chat_sessions`, `profile` (unused by any page; `brand_projects` was already dropped in a migration). These came from a different Lovable project sharing the Supabase instance.

Storage layout in `publicbckt`:
- `uploads/{user_id}/{ts}-{name}.csv` (UploadPanel and PhytolithChartModal) and `{user_id}/{ts}.csv` (UploadModal) — two inconsistent paths
- `uploads/{file_name}-{job_id}.json` — dataset converted to JSON by n8n
- `phytophotos/{kinet_no}[-suffix]/{n}.jpg`, with `diagnostic/` subfolders

### 2.3 Flows

**Upload.** Client uploads the CSV to the public bucket, inserts an `uploads` row with the public URL.

**Job.** Client inserts a `jobs` row (`completed = "Pending"`), then invokes `charter-job` with `{job_id, upload_id, xaxis, yaxis, prompt}`. The function forwards as a GET to `/webhook/charter1` with query params. n8n then: reads the upload and job rows; downloads the CSV twice (once as text to sniff the delimiter, once as a file to parse); converts all rows to a JSON array; base64-encodes it and uploads it to storage; takes the first 10 rows plus x, y, prompt and asks gpt-4.1-mini for a Vega-Lite v6 spec with a placeholder data URL; injects the storage URL into `spec.data.url`; writes `jobs.json` (URL), `jobs.response` (an HTML page embedding vega-embed from jsDelivr), `completed = "done"`.

**View.** `/job/:id` loads the job and renders `response` in an iframe with `sandbox="allow-scripts allow-same-origin"`, and fetches `json` to show the raw dataset in a side panel.

**Fine-tune.** Client invokes `fine-tune` with `{job_id, user_id, xaxis, yaxis, prompt}`. The function forwards as a GET to `/webhook/charterFineTune` with the values as HTTP headers. n8n reloads the job, fetches the dataset JSON, asks the model to revise the spec given the "previous spec" and new prompt, inserts a `fine_tuning` row with an HTML `result`, and overwrites `jobs.response`.

**Phytoliths.** `/phytoliths` lists contexts with search and period filter; `/phytoliths/:kinetNo` shows context metadata, expandable slides, a photo carousel with lightbox (regular vs diagnostic), and a horizontal bar chart of morphotype counts. "Generate Chart" assembles a CSV (`slide_id,kinet_no,morphotype,category,count`) from `counts` joined to `morphotypes`, uploads it, creates an upload row and a job row, and invokes `charter-job`.

### 2.4 Visual identity (keep)

Teal primary `hsl(174 72% 45%)`, accent tint `hsl(174 60% 92%)`, success `hsl(142 71% 45%)`, warning `hsl(38 92% 50%)`, destructive `hsl(0 84% 60%)`, near-white ground `hsl(0 0% 98%)`, radius 0.5rem. Left sidebar workspace shell with a gradient avatar dot; lucide icons; shadcn components.

---

## 3. Findings — what the grill-me surfaced

Severity: **S** security, **C** correctness, **D** design debt.

1. **S — Service-role key in workflow JSON.** Both chart-er workflows carry the Supabase service_role JWT in plaintext HTTP headers. Anyone with the export has full DB access. Rotate on the old project; never store keys outside Supabase secrets on the new one.
2. **S — Edge functions are unauthenticated.** `verify_jwt = false` on both. `charter-job` accepts any `job_id`; `fine-tune` accepts a caller-supplied `user_id`. Any visitor can burn LLM credit and write into other users' rows.
3. **S — Public bucket for user datasets.** Every uploaded CSV and converted JSON is world-readable by URL.
4. **S — LLM output rendered as trusted HTML.** `jobs.response` is model-generated HTML placed in an iframe with `allow-same-origin`. That is an XSS surface against the app origin.
5. **C — Status mismatch.** UI expects `"Done"`; n8n writes `"done"`. Status badges fall through to the muted default. Failures leave jobs at `"Pending"` forever; there is no error state.
6. **C — Fine-tune never sees data.** The Fine Tune workflow slices 5 sample rows but the prompt never references them. The "previous spec" it passes is the whole HTML page, not the spec.
7. **C — Deletion is incomplete.** Deleting an upload deletes jobs then the upload row, but not storage objects and not `fine_tuning` rows. Without `ON DELETE CASCADE` on `fine_tuning.job_id` the job delete fails once a fine-tune exists.
8. **C — RLS on chart tables is undocumented.** The migrations only cover phytolith tables. The client filters by `user_id` in the query, which is not a security boundary.
9. **C — Recharts per-bar colors don't apply.** `MorphotypeChart` renders bare `<rect>` children inside `<Bar>`; Recharts needs `<Cell>`.
10. **D — Two Supabase clients.** `lib/supabase.ts` (uses `VITE_SUPABASE_ANON_KEY`) and `integrations/supabase/client.ts` (uses `VITE_SUPABASE_PUBLISHABLE_KEY`). Pages mix them.
11. **D — Sidebar duplicated** in Dashboard, FineTuneHistory, and Settings, with drift (Settings lacks the Phytoliths entry). `TopBar` and `UploadPanel`/`UploadCard`/`JobCard` are dead code superseded by list-item variants.
12. **D — No push updates.** Users press a refresh button to see whether a job finished.
13. **D — Free-text axis fields.** x and y are typed by hand; the prompt then does fuzzy matching. The CSV header is known at upload time and should drive a dropdown.
14. **D — CSV parsed twice**, delimiter sniffed by counting characters on line one, dataset base64-encoded to pass between nodes. All artifacts of doing this in n8n.
15. **D — Fine-tune history is disconnected from the chart.** It lives on a separate page grouped by job id, with status inferred from whether the result string contains "error".

---

## 4. Target architecture

### 4.1 Decisions

| Area | Decision | Why |
|---|---|---|
| Frontend | Keep Vite + React 18 + TS + Tailwind + shadcn/ui + react-router. Adopt TanStack Query for all data. | Existing components port nearly 1:1; no reason to change the rendering stack. |
| Backend | Supabase only: Postgres + RLS, Auth, Storage, Edge Functions (Deno). **n8n removed.** | One vendor, one repo, everything reproducible from `supabase/`. |
| Pipeline | One edge function `generate-chart`, JWT-verified, does parse → summarize → LLM → validate → persist. | Replaces both n8n workflows and both forwarding functions. |
| LLM | Provider adapter with one interface (`generateSpec(input) → VegaLiteSpec`). Default Anthropic Claude (Haiku 4.5 for cost, Sonnet 5 when quality matters). OpenAI `gpt-4.1-mini` kept as the proven baseline adapter. | Swappable without touching the pipeline; documented in README for reviewers. *Assumption — see open questions.* |
| Chart storage | Store the **Vega-Lite spec as jsonb**. Never store HTML. | Removes the XSS surface; enables diffing versions; smaller rows. |
| Rendering | Client-side `vega-embed` inside the React app (no iframe). Export PNG/SVG comes free. | Same library the HTML used, without the sandbox. |
| Dataset access | Private bucket `datasets`, path `{user_id}/{upload_id}/data.csv` and `parsed.json`. Spec `data.url` is filled at render time with a signed URL. | Private by default; the persisted spec stays portable (`data.name = "main"`). |
| Versions | Replace `fine_tuning` with `chart_versions`. Version 1 is the initial generation; each fine-tune is version n+1 with `parent_version_id`. | The history *is* the chart's timeline. One viewer, one model. |
| Status | Enum `pending | running | done | failed` plus `error_message`. Client subscribes via Supabase Realtime. | Fixes the case bug and the stuck-pending bug; removes the refresh button. |
| Column selection | Parse the header client-side with PapaParse at upload; store `columns jsonb` on `uploads`; x/y become selects. | Eliminates fuzzy field matching in the prompt. |
| Phytolith module | Keep public read. Drop `phyto_photos.url`, compute from `storage_path`. Keep `slides.photo_ids`. Move photos to bucket `phytophotos` (public). | URLs must not embed the old project ref. |
| Auth | Supabase email + password, email confirmation on. `profiles` table populated by trigger on `auth.users`. | Same UX as today, with a proper profile row. |
| Hosting | Static build on Netlify or Vercel; Supabase for everything else. *Assumption.* | |

### 4.2 Schema (new project)

```sql
-- enums
create type job_status as enum ('pending','running','done','failed');

-- profiles
create table profiles (
  id uuid primary key references auth.users on delete cascade,
  email text,
  display_name text,
  created_at timestamptz default now()
);
-- trigger: insert into profiles on auth.users insert

-- uploads
create table uploads (
  id bigint generated always as identity primary key,
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  name text not null,
  storage_path text not null,           -- {user_id}/{upload_id}/data.csv
  parsed_path text,                     -- {user_id}/{upload_id}/parsed.json (set by pipeline)
  columns jsonb not null default '[]',  -- [{name, type: 'number'|'date'|'string', sample: [...]}]
  row_count int,
  size_bytes int,
  source text not null default 'upload', -- 'upload' | 'phytolith'
  created_at timestamptz default now()
);

-- jobs (a chart)
create table jobs (
  id bigint generated always as identity primary key,
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  upload_id bigint not null references uploads on delete cascade,
  title text,
  current_version_id bigint,            -- fk added after chart_versions exists
  created_at timestamptz default now()
);

-- chart_versions (v1 = initial generation; v2+ = fine-tunes)
create table chart_versions (
  id bigint generated always as identity primary key,
  job_id bigint not null references jobs on delete cascade,
  user_id uuid not null default auth.uid(),
  version_no int not null,
  parent_version_id bigint references chart_versions on delete set null,
  xaxis text not null,
  yaxis text not null,
  prompt text not null check (char_length(prompt) <= 1000),
  status job_status not null default 'pending',
  spec jsonb,                           -- Vega-Lite v6, data: {name:'main'}
  model text,                           -- e.g. 'claude-haiku-4-5-20251001'
  error_message text,
  started_at timestamptz,
  finished_at timestamptz,
  created_at timestamptz default now(),
  unique (job_id, version_no)
);
alter table jobs add foreign key (current_version_id) references chart_versions on delete set null;

-- phytolith tables: identical to today minus phyto_photos.url
```

RLS:
- `profiles`: owner read/update.
- `uploads`, `jobs`, `chart_versions`: `auth.uid() = user_id` for select/insert/update/delete. Pipeline writes with service role from inside the edge function only.
- `contexts`, `slides`, `counts`, `morphotypes`, `phyto_photos`: select for `anon, authenticated`; no client writes.
- Storage `datasets` (private): owner-only by first path segment `= auth.uid()::text`. Storage `phytophotos` (public read).

Realtime: enable on `chart_versions`.

### 4.3 Edge function `generate-chart`

- `POST /generate-chart` with `{ version_id }`. JWT verified; function loads the version with the caller's JWT so RLS enforces ownership. Returns `202` immediately after flipping status to `running`; work continues in the same invocation (a few seconds; well under limits).
- Steps:
  1. Download `data.csv` via service role. Parse with a real CSV parser (Deno std `csv` or PapaParse) with delimiter detection over the first 20 lines (`,` `;` `\t` `|`). Cap at 50 000 rows / 10 MB (*assumption*); reject above with `failed`.
  2. Infer column types (number / date / string / boolean) from a 200-row sample. Write `parsed.json` once per upload (skip if `parsed_path` already set). Update `uploads.columns`, `row_count`.
  3. Build the prompt: dataset schema (name, type, 3 sample values per column, row count), chosen x and y, the user prompt, and for fine-tunes the parent version's spec JSON and its prompt. Ten sample rows, as today.
  4. Call the provider adapter with a JSON-only instruction. Strip fences, parse.
  5. Validate: object; `$schema` is Vega-Lite v6; has `mark` and `encoding`; `encoding.x.field` and `encoding.y.field` exist in `columns` (else swap in the user's selection); force `data = {name: 'main'}`; strip `datasets`, `transform[].url`, and any `values`. One retry with the validation error fed back to the model.
  6. Persist `spec`, `model`, `status = done`, `finished_at`, set `jobs.current_version_id`. On any failure: `status = failed`, `error_message`.
- Secrets: `LLM_PROVIDER`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`. `SUPABASE_SERVICE_ROLE_KEY` is injected by the platform.

Prompt rules carried over from the n8n nodes (they were good): output JSON only; infer types from sample; add color encoding when the prompt says "group", "by", "per", or "color"; temporal x gets `timeUnit`/axis format; categorical x + quantitative y defaults to `aggregate: sum` unless scatter/raw is requested; fallbacks: temporal→line, nominal→bar, both quantitative→point; no `layer`/`concat`/`repeat`/`facet` in v1.

### 4.4 Frontend

Routes:

| Route | Page | Auth |
|---|---|---|
| `/` | Landing (hero, three feature cards, phytolith entry card) | public |
| `/auth` | Sign in / sign up | public |
| `/app` | Dashboard: uploads list with nested charts, New Upload | required |
| `/app/charts/:jobId` | Chart viewer: vega-embed canvas, version timeline sidebar, inline fine-tune form, dataset table tab, export PNG/SVG/JSON | required |
| `/app/settings` | Account (email, display name), sign out | required |
| `/phytoliths` | Contexts grid with search + period filter | public |
| `/phytoliths/:kinetNo` | Context detail: metadata, slides, photos, morphotype chart, Generate Chart | public; Generate Chart requires auth |

Structure:
- `AppShell` (sidebar nav + user footer) used by every `/app` page. One nav definition.
- One Supabase client (`src/lib/supabase.ts`, typed with generated `Database`). `supabase gen types` in `package.json`.
- TanStack Query hooks per resource: `useUploads`, `useJobs(uploadId)`, `useVersions(jobId)`. Realtime subscription on `chart_versions` invalidates the relevant queries.
- `ChartCanvas` wraps `vega-embed`; receives `spec` and a signed URL for `parsed.json`, injects `data.url` at render.
- `UploadDialog`: file input (CSV only), name, client-side header parse → column preview → upload to `datasets/{uid}/{tmp}` then insert row (or insert first, then move: pick insert-then-upload using the returned id as path segment).
- `NewChartDialog`: x select, y select (from `uploads.columns`), prompt textarea (1000 chars), Create → insert job + version 1 → invoke `generate-chart`.
- `FineTunePanel` inside the viewer: pre-filled with current version's x/y/prompt; submit creates version n+1 with `parent_version_id` and invokes the function. Timeline shows status chips (pending/running/done/failed with message) and lets the user select any version as current.
- Delete upload: remove storage folder `{uid}/{upload_id}/` then delete row (cascade handles jobs and versions). Confirm dialog stays.
- Phytolith components port as-is, with the `<Cell>` fix and photo URLs computed from `storage_path` via `supabase.storage.from('phytophotos').getPublicUrl`.

Design: keep the token set in §2.4. Add a `--running` pulse for status chips. Tabular numerals in the phytolith metadata grid.

### 4.5 Repo layout

```
chart-er/
  src/                 React app
  supabase/
    config.toml        verify_jwt = true for generate-chart
    migrations/        0001_schema, 0002_rls, 0003_storage, 0004_phytolith_seed
    functions/
      generate-chart/  index.ts, csv.ts, infer.ts, prompt.ts, validate.ts, providers/{anthropic,openai}.ts
    seed/              contexts.csv slides.csv morphotypes.csv counts.csv phyto_photos.csv
  scripts/
    migrate-photos.ts  copy phytophotos/ from old bucket to new
  tests/               vitest (csv, infer, validate, prompt); deno test for the function
  README.md  LICENSE (MIT)  CITATION.cff  CLAUDE.md
```

---

## 5. Data migration from the old project

1. **Phytolith tables.** Export `contexts`, `slides`, `morphotypes`, `counts`, `phyto_photos` as CSV from the old dashboard (or `pg_dump --data-only -t`). Commit them under `supabase/seed/` and load in migration 0004 with `\copy` or an `insert ... select from json`. Drop the `url` column on import. Re-derive `slides.photo_ids` with the same `array_agg` update the old migration used.
2. **Photos.** `scripts/migrate-photos.ts`: list `publicbckt/phytophotos/**` on the old project with the old anon key (bucket is public), download, upload to `phytophotos/` on the new project with the new service key. Idempotent by path.
3. **User uploads, jobs, fine-tunes.** Not migrated. *Assumption: this was test data.* If needed later, only `uploads` is worth carrying; charts would be regenerated.
4. **Old project.** Rotate the service_role key immediately, regardless of whether it stays online.

---

## 6. Non-functional requirements

- **Reproducible from clone.** `supabase start && supabase db reset && npm run dev` gives a working local instance with phytolith data. Documented in README.
- **Tests.** Unit tests for CSV parsing, type inference, spec validation, prompt building. One integration test that runs `generate-chart` against a stub provider. CI on GitHub Actions: lint, typecheck, tests, `supabase db lint`.
- **Limits.** 10 MB / 50 000 rows per upload; 1000-char prompts; 10 sample rows and 200-row inference sample to the model. Rate-limit chart generation per user (e.g. 30/hour) via a check in the function.
- **Accessibility.** Keyboard-reachable dialogs and timeline; chart canvas has an accessible description generated from the spec (mark, x, y).
- **Observability.** Function logs one structured line per version: version id, model, tokens, duration, outcome. `error_message` is user-readable; stack traces stay in logs.
- **Licensing / JOSS.** MIT, `CITATION.cff`, a paper-ready README with architecture diagram and a statement of need for the phytolith module.

---

## 7. Build order

1. **Foundation.** New Supabase project. Repo scaffold. Migrations 0001–0003, generated types, single client, `AppShell`, auth pages. *Exit: sign up, sign in, empty dashboard.*
2. **Uploads.** `UploadDialog` with client-side column parsing, private bucket, delete with storage cleanup. *Exit: upload, see columns, delete.*
3. **Generation.** `generate-chart` with the Anthropic adapter and stub provider for tests; `NewChartDialog`; realtime status. *Exit: create a chart, watch it go pending → running → done, see the spec.*
4. **Viewer.** `ChartCanvas`, dataset tab, exports, version timeline, `FineTunePanel`. *Exit: fine-tune twice, switch between versions.*
5. **Phytoliths.** Migration 0004 with seed data, photo copy script, port of the three pages and three components, Generate Chart bridge. *Exit: public browsing works logged out; Generate Chart works logged in.*
6. **Hardening.** Rate limit, OpenAI adapter, tests, CI, README, CITATION, deploy.

---

## 8. Open questions (answered by assumption until you say otherwise)

| # | Question | Assumed answer |
|---|---|---|
| 1 | Which LLM provider is the default? | Anthropic Claude via adapter; OpenAI adapter kept. |
| 2 | Should datasets be private? | Yes. The old public bucket was a shortcut for n8n. |
| 3 | Does the phytolith module stay public without login? | Yes, unchanged; JOSS reviewers need it. |
| 4 | File formats beyond CSV? | CSV only in v1. Old code half-allowed JSON. |
| 5 | Keep the name "Chart-er"? | Yes. |
| 6 | Migrate old users' uploads and charts? | No. |
| 7 | Where is the frontend hosted? | Netlify or Vercel static; Supabase for the rest. |
| 8 | Should a fine-tune fork from any version or only the current one? | Any version; the timeline lets you pick. |
| 9 | Max dataset size? | 10 MB / 50k rows. |
| 10 | Does "Generate Chart" on a phytolith context create a normal upload the user sees on their dashboard? | Yes, tagged `source = 'phytolith'` so it can be filtered. |
