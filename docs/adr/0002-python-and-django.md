# ADR 0002: Python 3.12 and Django 5.2 LTS

Date: 2026-09-08. Status: accepted.

The owner and the reviewers read Python, and the data-handling libraries archaeologists already know live there. Django brings auth, sessions, migrations, ORM, admin, file storage, and a test client as first-party pieces, so the backend has one framework and no glue. Django 5.2 is supported until April 2028, which outlives the conference and the paper.

Rejected: FastAPI, the current default for generated Python services, which would need SQLAlchemy, Alembic, an auth library, and an admin bolted on. TypeScript on Deno only made sense inside Supabase's edge runtime, which is gone.
