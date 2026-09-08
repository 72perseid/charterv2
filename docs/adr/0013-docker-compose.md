# ADR 0013: One compose file, one env file

Date: 2026-09-08. Status: accepted.

A reviewer runs `docker compose up` and has the whole system: PostgreSQL, the API, the worker, and Caddy. The same file runs on the VPS, where the compose Caddy is published on `127.0.0.1:8080` and the host's own Caddy terminates TLS in front. Sharing the host with another stack is a hosting detail; sharing a database would be a dependency, so Chart-er never touches the other stack's containers.
