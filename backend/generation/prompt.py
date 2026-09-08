"""
Builds the messages array from the template in prompts/ (SPEC §6.3 step 2).
The rendered prompt for each privacy level is snapshot-tested per version.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from django.conf import settings


@dataclass(frozen=True)
class Template:
    version: str
    system: str
    user: str


@lru_cache
def load_template(version: str) -> Template:
    text = (Path(settings.PROMPTS_DIR) / f"{version}.md").read_text(encoding="utf-8")
    system = _section(text, "## System")
    user = _section(text, "## User message template")
    return Template(version=version, system=system, user=user)


def _section(text: str, heading: str) -> str:
    start = text.index(heading) + len(heading)
    rest = text[start:]
    end = rest.find("\n## ")
    return (rest if end == -1 else rest[:end]).strip()


def build_messages(
    *,
    profile_for_model: dict,
    x_field: str,
    y_field: str,
    color_field: str | None,
    prompt: str,
    parent_spec: dict | None = None,
    parent_prompt: str | None = None,
    retry_error: str | None = None,
    version: str | None = None,
) -> list[dict]:
    template = load_template(version or settings.PROMPT_VERSION)
    revision_block = ""
    if parent_spec is not None:
        revision_block = (
            "Previous request: "
            + (parent_prompt or "")
            + "\nPrevious specification (JSON):\n"
            + json.dumps(parent_spec, ensure_ascii=False, indent=1)
            + "\n\n"
        )
    user = template.user.format(
        profile=json.dumps(profile_for_model, ensure_ascii=False, indent=1),
        x_field=x_field,
        y_field=y_field,
        color_field=color_field or "(none)",
        revision_block=revision_block,
        prompt=prompt.strip(),
    )
    messages = [
        {"role": "system", "content": template.system},
        {"role": "user", "content": user},
    ]
    if retry_error:
        messages.append(
            {
                "role": "user",
                "content": "Your previous answer was rejected: "
                + retry_error
                + "\nAnswer again with one corrected JSON object.",
            }
        )
    return messages
