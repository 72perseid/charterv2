# ADR 0003: django-ninja for the API layer

Date: 2026-09-08. Status: accepted.

Typed request and response schemas and an OpenAPI document for free, in about a tenth of the code of Django REST Framework. The OpenAPI document is committed as `docs/openapi.json`.

Consequence found during build: ninja 1.7 has no CSRF switch on the API object. Session-authenticated routes get the check from `django_auth`; the two routes that run before a session exists (register, login) call `check_csrf` themselves.
