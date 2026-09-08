# ADR 0014: Status by polling

Date: 2026-09-08. Status: accepted.

The client polls the revision (or dataset) endpoint every two seconds while it is pending or running. Boring and sufficient. Server-sent events are a later refinement, not a requirement.
