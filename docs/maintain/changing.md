# Changing things

Recipes for the changes that come up. Each lists every file to touch, so nothing is left half done.

## The prompt

Prompts are versioned and never edited in place. Every stored revision names the version that produced it, and a bundle must stay replayable with the text it was made with.

1. Copy `backend/prompts/p2026-11-b.md` to a new name: `p` + year + month + a letter (`p2026-12-a.md`).
2. Edit the copy. The header paragraph says what changed and why; `## System` is sent verbatim; `## User message template` is filled in by `generation/prompt.py`. A new `{placeholder}` needs a matching argument there.
3. Set `PROMPT_VERSION` in `backend/charter/settings.py`.
4. Run `pytest tests/test_prompt.py`. The snapshot test finds no snapshot for the new version, writes `tests/snapshots/p2026-12-a_*.txt`, and reports itself skipped. **Read the two new files**: they are exactly what a model will receive. Run again; it passes.
5. Try it on a real model with a real dataset before deploying. The tests prove the text is what you wrote, not that a model does well with it. Small local models are the hardest case and the best test.
6. Note the change in SPEC §13 and commit the prompt, the setting and the snapshots together.

To change a snapshot of the *current* version on purpose, delete the file and run the test once.

Old prompt files stay. They are the record.

The period question ("ask the model about the unplaced values") has its own file and setting: `prompts/periods-…md`, `PERIODS_PROMPT_VERSION`.

## What the server does to the model's answer

`generation/validate.py`. Every correction appends a sentence to the list the user sees under the chart; a silent correction is a bug. Add a case to `tests/test_validate.py` for each new rule, and describe it in SPEC §6.3 step 4.

The rule of thumb that has held so far: **repair what the user unambiguously chose, reject what is not about their data.** An answer that is repaired into a chart nobody asked for is worse than a failure with a reason.

## Text on screen

Add the key to `frontend/src/lib/i18n/en.ts`, then to `tr.ts`. `npm run check` fails until both have it. The in-app help page is also there, under `help`; keep it in step with `docs/guide/` when behaviour changes.

## A field on a model

1. Edit `models.py`, then `python manage.py makemigrations` and read the generated file.
2. Add it to the schema in `schemas.py` and, for a revision field, to `charts/export.py` so that it reaches the bundle.
3. Add it to the type in `frontend/src/lib/api.ts`.
4. Regenerate the API description (next section).
5. Update the data model in SPEC §5.

Migrations run by themselves when the `api` container starts.

## The API description

`docs/openapi.json` is generated, in this exact format so that the diff shows only real changes:

```sh
cd backend && python -c "
import django, json, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'charter.settings'); django.setup()
from charter.api import api
open('../docs/openapi.json', 'w').write(json.dumps(api.get_openapi_schema(), indent=1, ensure_ascii=False))"
git diff --stat docs/openapi.json
```

## A limit or a timeout

All in `backend/charter/settings.py`: upload size, rows and columns, uploads and revisions per hour, the provider timeout, the output token limit, the seed. The numbers also appear in the README, the user guide, the help strings and (for the upload size) `deploy/Caddyfile`, which must allow a body slightly larger than `UPLOAD_MAX_BYTES`. Search for the old number.

## A dependency

Write `docs/adr/NNNN-name.md` first: what it is for, and why the alternative (including "write it ourselves" and "do without") was worse. Add it to `docs/adr/README.md` and the table in SPEC §3. Then add it to `backend/pyproject.toml` or `frontend/package.json`. The backend image installs from `pyproject.toml`, so the next deploy picks it up.

## The PeriodO snapshot

Period names are dated from `backend/datasets/periodo_snapshot.json`, a reduced copy of the PeriodO dataset. To refresh it:

```sh
curl -sL --compressed -H "Accept: application/json" https://data.perio.do/d.json -o /tmp/d.json
cd backend && python manage.py periodo_snapshot /tmp/d.json
pytest tests/test_chronology.py
git diff --stat datasets/periodo_snapshot.json
```

The snapshot has one definition per line, so the diff is the definitions that changed. A refresh can change the order of an existing user's period column the next time their dataset is read, which is why each profile records the snapshot it was dated with. Refresh deliberately, not routinely, and never just before a presentation.

Words that PeriodO does not carry (Turkish and German period terms, abbreviations) are in the glossaries in `datasets/chronology.py`. A period that should be recognised and is not usually needs a line there and a case in `test_chronology.py`.

## The example dataset

`backend/datasets/examples/`: one CSV per interface language, registered in `__init__.py`. The rows are invented and the README in that folder says so; keep it that way. Real excavation data does not belong in a public repository without its owner's word.

## A decision

When you choose between two reasonable ways of doing something, write the ADR while you still remember the losing option. Half a page: context, decision, consequences. The value of `docs/adr/` is that it answers "why not X?" a year later, in a thesis defence or to a new maintainer.
