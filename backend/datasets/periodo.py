"""
The PeriodO gazetteer of period definitions (https://perio.do, CC0), read from
a snapshot vendored next to this file (ADR 0018). PeriodO records what a named
period means *according to a source*: "Iron Age" has dozens of definitions with
different dates for different regions. This module only loads and indexes them;
choosing between them is `datasets/chronology.py`.

Nothing here talks to the network. `manage.py periodo_snapshot` rebuilds the file.
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from functools import cache, lru_cache
from pathlib import Path

SNAPSHOT_PATH = Path(__file__).with_name("periodo_snapshot.json")
PERMALINK = "http://n2t.net/ark:/99152/"

_DASHES = dict.fromkeys(map(ord, "–—−‒―"), "-")
_TURKISH_I = {ord("İ"): "i", ord("ı"): "i"}
_SPELLING = {"palaeolithic": "paleolithic", "epipalaeolithic": "epipaleolithic",
             "mediaeval": "medieval", "millenium": "millennium", "seljuk": "seljuq",
             "saljuq": "seljuq"}  # fmt: skip
_WORD = re.compile(r"\w+")
_BRACKETS = re.compile(r"\(([^()]*)\)")
_TRAILING_YEARS = re.compile(r",[^,]*\d[^,]*$")


def fold(value: str) -> str:
    """Lower case, Turkish letters flattened, accents removed, dashes unified."""
    text = str(value).translate(_DASHES).translate(_TURKISH_I).lower()
    text = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def key(value: str) -> str:
    """The form labels are compared in: folded words, one spelling, no punctuation."""
    return " ".join(_SPELLING.get(word, word) for word in _WORD.findall(fold(value)))


@dataclass(frozen=True, slots=True)
class Definition:
    id: str
    authority: str
    label: str
    start: int  # astronomical-style year: negative is BC
    stop: int
    regions: tuple[str, ...]
    labels: tuple[str, ...] = ()  # every label, the source's own first

    def called(self, keys: set[str]) -> str:
        """The label that matched one of `keys`, else the source's own."""
        return next((label for label in self.labels if label_keys(label) & keys), self.label)

    @property
    def url(self) -> str:
        return PERMALINK + self.id


@dataclass(frozen=True)
class Gazetteer:
    snapshot: str
    sources: dict[str, tuple[str, str]]  # authority id -> (title, year published)
    by_label: dict[str, tuple[Definition, ...]]

    def find(self, label_key: str) -> tuple[Definition, ...]:
        return self.by_label.get(label_key, ())

    def source(self, definition: Definition) -> str:
        title, year = self.sources.get(definition.authority, ("", ""))
        return f"{title} ({year})" if year else title


@cache
def label_keys(label: str) -> frozenset[str]:
    """A PeriodO label and its obvious short forms: 'Pre-Pottery Neolithic B
    (PPNB)' is also 'pre pottery neolithic b' and 'ppnb'; 'Tanzimat, 1839-1876'
    is also 'tanzimat'."""
    forms = {label, _BRACKETS.sub(" ", label), _TRAILING_YEARS.sub("", label)}
    forms |= {inner for inner in _BRACKETS.findall(label) if " " not in inner.strip()}
    return frozenset(k for k in map(key, forms) if k and not k.isdigit())


@lru_cache
def gazetteer() -> Gazetteer:
    data = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    by_label: dict[str, list[Definition]] = {}
    for period_id, authority, start, stop, labels, regions in data["periods"]:
        definition = Definition(
            period_id, authority, labels[0], start, stop, tuple(regions), tuple(labels)
        )
        for label_key in {k for label in labels for k in label_keys(label)}:
            by_label.setdefault(label_key, []).append(definition)
    return Gazetteer(
        snapshot=data["snapshot"],
        sources={a: (title, year) for a, (title, year) in data["authorities"].items()},
        by_label={k: tuple(v) for k, v in by_label.items()},
    )
