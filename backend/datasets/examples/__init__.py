"""The example dataset a user can add with one click, in each interface language."""

from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).parent


@dataclass(frozen=True)
class Example:
    name: str
    path: Path


EXAMPLES = {
    "en": Example("Example: finds by period (invented data)", HERE / "finds_en.csv"),
    "tr": Example("Örnek: dönemlere göre buluntular (uydurma veri)", HERE / "finds_tr.csv"),
}
