# ADR 0004: PostgreSQL 16, also as the job queue

Date: 2026-09-08. Status: accepted.

JSONB holds specs, profiles, and request records; one database is one backup target. The worker claims work with `SELECT … FOR UPDATE SKIP LOCKED`, which is about eighty readable lines and avoids Redis and Celery entirely. If priorities or scheduling are ever needed, django-q2 with the ORM broker is the drop-in upgrade.

Rejected: SQLite, because the app is multi-user and the worker and web processes write concurrently.
