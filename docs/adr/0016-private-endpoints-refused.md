# ADR 0016: Private and plain-http endpoints refused by default

Date: 2026-09-08. Status: accepted.

Users supply the base URL the server will call. Without a check, one user could make the server call PostgreSQL, the other stack on the box, or anything on the private network. The provider module refuses `http://` and any host that resolves to a non-global address unless the operator sets `ALLOW_PRIVATE_ENDPOINTS=true`, which is the switch for a local model.
