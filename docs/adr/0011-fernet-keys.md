# ADR 0011: User API keys encrypted at rest with Fernet

Date: 2026-09-08. Status: accepted.

Plaintext keys in a database on a rented VPS are not acceptable. Keys are encrypted with `cryptography`'s Fernet under `FERNET_KEY` from the environment. The operator can still decrypt; the README says so. Losing the key means every user re-enters theirs.
