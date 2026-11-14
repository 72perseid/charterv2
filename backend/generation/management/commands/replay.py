"""
Re-run a revision from a reproducibility bundle against an endpoint and say
whether the same specification comes back. This is the "reproduce a chart from
a bundle" check in SPEC §12 step 6, runnable by anyone holding a bundle and a
key; it needs no account and touches no database.

    manage.py replay charter-chart-12.json --revision 2 \
        --base-url https://api.openai.com/v1 --model gpt-4.1-mini --api-key sk-...
"""

from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from datasets.profile import period_orders
from generation.provider import ProviderError, chat_completion
from generation.validate import SpecError, validate_spec


class Command(BaseCommand):
    help = "Replay a bundled revision's exact request and compare the resulting spec."

    def add_arguments(self, parser):
        parser.add_argument("bundle", type=Path)
        parser.add_argument("--revision", type=int, help="revision_no; default: the last one")
        parser.add_argument("--base-url", required=True)
        parser.add_argument("--model", help="default: the model recorded in the bundle")
        parser.add_argument("--api-key", required=True)
        parser.add_argument("--out", type=Path, help="write the replayed spec here")

    def handle(self, *args, bundle: Path, revision, base_url, model, api_key, out, **opts):
        try:
            data = json.loads(bundle.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise CommandError(f"Cannot read bundle: {exc}") from exc
        if data.get("format") != "charter-bundle/1":
            raise CommandError("Not a charter-bundle/1 file.")

        revisions = data["revisions"]
        chosen = next(
            (r for r in revisions if revision is None or r["revision_no"] == revision), None
        )
        if revision is None:
            chosen = revisions[-1] if revisions else None
        if chosen is None or not chosen.get("request"):
            raise CommandError("That revision has no recorded request.")

        params = chosen["request"]["parameters"]
        self.stdout.write(
            f"Replaying revision {chosen['revision_no']} "
            f"(recorded model {chosen['model']!r} at {chosen['endpoint_host']!r}, "
            f"prompt {chosen['prompt_version']}, app {chosen['app_version']})"
        )
        try:
            result = chat_completion(
                base_url=base_url,
                api_key=api_key,
                model=model or chosen["model"],
                messages=chosen["request"]["messages"],
                temperature=params.get("temperature", 0.0),
                max_tokens=params.get("max_tokens") or params.get("max_completion_tokens"),
                json_object="response_format" in params,
                seed=params.get("seed"),
            )
        except ProviderError as exc:
            raise CommandError(str(exc)) from exc

        field_names = {c["name"] for c in data["dataset"]["profile"]["columns"]}
        try:
            validated = validate_spec(
                result.text,
                field_names=field_names,
                x_field=chosen["x_field"],
                y_field=chosen["y_field"],
                color_field=chosen.get("color_field"),
                period_orders=period_orders(data["dataset"]["profile"]),
            )
        except SpecError as exc:
            raise CommandError(f"Replayed answer failed validation: {exc}") from exc

        if out:
            out.write_text(json.dumps(validated.spec, ensure_ascii=False, indent=1))
        same = validated.spec == chosen["spec"]
        self.stdout.write(
            f"Model {result.model}, {result.duration_ms} ms"
            + (f", adjustments: {', '.join(result.adjustments)}" if result.adjustments else "")
        )
        if same:
            self.stdout.write(self.style.SUCCESS("Identical specification."))
        else:
            self.stdout.write(self.style.WARNING("Specification differs from the bundle."))
            for key in ("mark", "encoding", "title", "transform"):
                if validated.spec.get(key) != chosen["spec"].get(key):
                    self.stdout.write(f"  {key}: bundle={chosen['spec'].get(key)!r}")
                    self.stdout.write(f"  {key}: replay={validated.spec.get(key)!r}")
