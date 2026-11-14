# Architecture decision records

One short record per decision in SPEC.md §2, so the reasoning survives the person who made it. Anything not in the dependency tables of §3 needs a record here before it is added.

- [0001](0001-pyarrow-for-parquet.md) pyarrow for the parsed-rows file
- [0002](0002-python-and-django.md) Python 3.12 and Django 5.2 LTS
- [0003](0003-django-ninja.md) django-ninja for the API layer
- [0004](0004-postgresql-queue.md) PostgreSQL 16, also as the job queue
- [0005](0005-pandas-openpyxl.md) pandas and openpyxl for tabular parsing
- [0006](0006-bring-your-own-key.md) Bring-your-own-key model access over one HTTP call
- [0007](0007-profile-not-rows.md) The model sees a profile, not rows
- [0008](0008-vega-lite-json-only.md) Charts are Vega-Lite v6 JSON with data supplied at render time
- [0009](0009-sveltekit-static.md) SvelteKit with the static adapter and hand-written CSS
- [0010](0010-session-auth.md) Django session auth with email as the username
- [0011](0011-fernet-keys.md) User API keys encrypted at rest with Fernet
- [0012](0012-local-files.md) Files on local disk, served only through authenticated views
- [0013](0013-docker-compose.md) One compose file, one env file
- [0014](0014-polling.md) Status by polling
- [0015](0015-revision-not-fine-tune.md) "Revision", not "fine-tune"
- [0016](0016-private-endpoints-refused.md) Private and plain-http endpoints refused by default
- [0017](0017-cost-at-run-time.md) Cost estimated from user-entered prices, fixed at run time
- [0018](0018-period-columns.md) Period columns are ordered by the server, with PeriodO as the reference
