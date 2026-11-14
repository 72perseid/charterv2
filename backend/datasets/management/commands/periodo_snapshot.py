"""
Rebuild the vendored PeriodO snapshot (ADR 0018) from the canonical dataset.

    curl -sL --compressed -H "Accept: application/json" https://data.perio.do/d.json -o d.json
    manage.py periodo_snapshot d.json

The snapshot keeps what ordering needs and nothing else: for each period
definition its id, authority, start and stop years, every label in every
language, and the regions it covers. One definition per line, so a refresh
shows up in a diff as the definitions that changed.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from datasets.periodo import SNAPSHOT_PATH


def _year(point: dict, key: str) -> int | None:
    inside = point.get("in") or {}
    value = inside.get("year") or inside.get(key)
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _title(authority: dict) -> tuple[str, str]:
    source = authority.get("source") or {}
    work = source.get("partOf") or source
    title = work.get("title") or source.get("title") or work.get("citation") or ""
    year = work.get("yearPublished") or source.get("yearPublished") or ""
    return " ".join(str(title).split()), str(year)


class Command(BaseCommand):
    help = "Write datasets/periodo_snapshot.json from a downloaded PeriodO d.json."

    def add_arguments(self, parser):
        parser.add_argument("dataset", type=Path)
        parser.add_argument("--date", default=date.today().isoformat(), help="snapshot date")

    def handle(self, *args, dataset: Path, date: str, **opts):
        try:
            data = json.loads(dataset.read_text(encoding="utf-8"))
            authorities = data["authorities"]
        except (OSError, ValueError, KeyError) as exc:
            raise CommandError(f"Cannot read a PeriodO dataset from {dataset}: {exc}") from exc

        sources: dict[str, list[str]] = {}
        lines: list[str] = []
        for authority_id in sorted(authorities):
            authority = authorities[authority_id]
            for period_id in sorted(authority.get("periods") or {}):
                period = authority["periods"][period_id]
                start = _year(period.get("start") or {}, "earliestYear")
                stop = _year(period.get("stop") or {}, "latestYear")
                if start is None:
                    continue
                labels = [period["label"]]
                for localized in (period.get("localizedLabels") or {}).values():
                    labels += [label for label in localized if label not in labels]
                regions = [
                    c["label"] for c in period.get("spatialCoverage") or [] if c.get("label")
                ]
                row = [
                    period_id,
                    authority_id,
                    start,
                    start if stop is None else stop,
                    labels,
                    regions,
                ]
                lines.append(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
                sources.setdefault(authority_id, list(_title(authority)))

        head = {
            "source": "https://data.perio.do/d.json",
            "license": "CC0 1.0",
            "snapshot": date,
            "authorities": sources,
        }
        text = (
            json.dumps(head, ensure_ascii=False, separators=(",", ":"))[:-1]
            + ',\n"periods":[\n'
            + ",\n".join(lines)
            + "\n]}\n"
        )
        SNAPSHOT_PATH.write_text(text, encoding="utf-8")
        self.stdout.write(
            f"{len(lines)} definitions from {len(sources)} authorities -> {SNAPSHOT_PATH}"
        )
