# ADR 0016: Private and plain-http endpoints refused by default

Date: 2026-09-08. Status: accepted.

Users supply the base URL the server will call. Without a check, one user could make the server call PostgreSQL, the other stack on the box, or anything on the private network. The provider module refuses `http://` and any host that resolves to a non-global address unless the operator sets `ALLOW_PRIVATE_ENDPOINTS=true`, which is the switch for a local model.

Amended 2026-11-13: with the flag set, a model configuration may be saved without an API key, since Ollama and similar servers check none, and the provider module then sends no `Authorization` header at all; some local servers answer 401 to an empty bearer token. The compose file maps `host.docker.internal` to the host gateway so that a base URL of `http://host.docker.internal:11434/v1` reaches a model server running beside the containers. Without the flag a blank key is still refused.
