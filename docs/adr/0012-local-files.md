# ADR 0012: Files on local disk, served only through authenticated views

Date: 2026-09-08. Status: accepted.

Originals and parsed parquet live under `DATA_DIR/{user_id}/{dataset_id}/` and are served only by Django views that check ownership. The v1 public bucket was the shortcut the low-code pipeline needed; nothing here is public. Deleting a dataset removes its directory in the same request.
