"""
Chronological order for a column of archaeological period labels (SPEC §6.1
step 6, ADR 0018). Text sorts alphabetically; this module puts the distinct
values of a column on a timeline so charts can draw them oldest first.

Dates for period names come from PeriodO (`datasets/periodo.py`), the gazetteer
of published period definitions, never from a table of our own. A label is
connected to PeriodO in this order, and the way it was connected is recorded:

  periodo        the label is a PeriodO label        Late Helladic IIIC
  abbreviation   after expanding an abbreviation     LB II, EIA
  translation    after translating its words         Geç Tunç Çağı, Frühbronzezeit
  derived        a part of a PeriodO period          the early third, phase III
  year           the label is itself a date          1500 BC, MÖ 5. yüzyıl, 9000 BP

PeriodO holds many definitions of one name ("Iron Age" starts anywhere between
1600 and 400 BC). `resolve` therefore reads the column as a whole: the region
most of its labels have a definition for wins, and within it the source that
defines the most labels. What still cannot be placed sorts last; the dataset
page lets the user ask their model about those labels or type the order.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field
from statistics import median

from datasets.periodo import Definition, gazetteer, key
from datasets.periodo import fold as _fold

BP_ZERO = 1950  # "before present" counts back from 1950 by convention
MAX_DISTINCT = 200  # a period column becomes an explicit sort list in the chart


@dataclass(frozen=True)
class Placed:
    start: float  # astronomical-style year: negative is BC
    end: float
    explicit: bool  # said BC/AD/century; a bare number did not


# --- text folding -------------------------------------------------------------

_ABBREVIATION_3 = re.compile(r"(?<![a-z])([a-z])\.\s?([a-z])\.\s?([a-z])(?![a-z])\.?")
_ABBREVIATION_2 = re.compile(r"(?<![a-z])([a-z])\.\s?([a-z])(?![a-z])\.?")
_GROUPED = re.compile(r"(?<=\d)[.,](?=\d{3}(?!\d))")


def fold(value: str) -> str:
    """Lower-case ASCII with Turkish letters flattened, 'M.Ö.' -> 'mo',
    '10.000' -> '10000'. Dates are read from this form."""
    text = _ABBREVIATION_3.sub(r"\1\2\3", _fold(value))
    text = _ABBREVIATION_2.sub(r"\1\2", text)
    text = _GROUPED.sub("", text)
    return " ".join(text.split())


# --- years, centuries, millennia ---------------------------------------------

_BC = {"bc", "bce", "mo", "io"}  # M.Ö. milattan önce, İ.Ö. İsa'dan önce
_AD = {"ad", "ce", "ms", "is"}  # M.S. milattan sonra, İ.S.
_BP = {"bp", "go"}  # G.Ö. günümüzden önce
_CENTURY = {"century", "centuries", "cent", "yy"}
_MILLENNIUM = {"millennium", "millennia", "mill", "bin"}
_RANGE_WORDS = {"to", "until", "ile", "and", "ve"}
_NUMBER_FILLER = {
    "ca", "circa", "approx", "around", "about", "yaklasik", "yak", "cal",
    "the", "of", "year", "years", "yil", "yili", "yillari", "arasi",
}  # fmt: skip
_EARLY = {"early", "erken", "ilk", "old", "eski", "lower", "alt", "baslari", "basi"}
_MIDDLE = {"middle", "mid", "orta", "ortasi", "ortalari"}
_LATE = {"late", "gec", "son", "neo", "new", "yeni", "upper", "ust", "sonu", "sonlari"}

# A minus sign is a sign only at the start or after a space, '(' or another '-';
# anywhere else ('1500-1200', '5.-4.') it separates the two ends of a range.
_TOKEN = re.compile(
    r"(?P<num>(?<![^\s(-])-?\d+|\d+)(?:st|nd|rd|th)?|(?P<word>[a-z]+)|(?P<sep>[-/])"
)
_PUNCTUATION = set(" .,()~?±'’:;")
_ROMAN = re.compile(r"^(x{0,3})(ix|iv|v?i{0,3})$")
_ROMAN_VALUES = {"": 0, "i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7,
                 "viii": 8, "ix": 9}  # fmt: skip


def _roman(word: str) -> int | None:
    match = _ROMAN.match(word)
    if not match or not word:
        return None
    return 10 * len(match.group(1)) + _ROMAN_VALUES[match.group(2)]


def _qualifier(word: str) -> str | None:
    if word in _EARLY:
        return "early"
    if word in _MIDDLE:
        return "middle"
    if word in _LATE:
        return "late"
    return None


def _third(start: float, end: float, qualifier: str | None) -> tuple[float, float]:
    if qualifier is None:
        return start, end
    step = (end - start) / 3
    index = ("early", "middle", "late").index(qualifier)
    return start + index * step, start + (index + 1) * step


def _span(number: int, era: str | None, unit: str | None, qualifier: str | None):
    """One number with its era and unit -> (start, end), or None."""
    before = era == "bc" or number < 0
    n = abs(number)
    if unit is None:
        if era == "bp":
            return BP_ZERO - n, BP_ZERO - n
        return (-n, -n) if before else (n, n)
    if n == 0 or era == "bp":
        return None
    size = 100 if unit == "century" else 1000
    start, end = (-size * n, -size * (n - 1) - 1) if before else (size * (n - 1) + 1, size * n)
    return _third(start, end, qualifier)


def _numeric(text: str) -> Placed | None:
    """'1500 bc', 'mo 5. yuzyil', '1500-1200 bc'. Every word must be understood:
    'trench 5' is not a year."""
    segments: list[dict] = [{}]
    position = 0
    for match in _TOKEN.finditer(text):
        if any(ch not in _PUNCTUATION for ch in text[position : match.start()]):
            return None
        position = match.end()
        segment = segments[-1]
        if match.group("num"):
            if "number" in segment:
                return None
            segment["number"] = int(match.group("num"))
        elif match.group("sep"):
            segments.append({})
        else:
            word = match.group("word")
            if word in _RANGE_WORDS:
                segments.append({})
            elif word in _BC or word in _AD or word in _BP:
                if "era" in segment:
                    return None
                segment["era"] = "bc" if word in _BC else "ad" if word in _AD else "bp"
            elif (
                word in _CENTURY
                or word.startswith("yuzyil")
                or (word == "c" and "number" in segment)
            ):
                segment["unit"] = "century"
            elif word in _MILLENNIUM or word.startswith("binyil"):
                segment["unit"] = "millennium"
            elif _qualifier(word):
                segment["qualifier"] = _qualifier(word)
            elif word in _NUMBER_FILLER or word == "c":
                continue
            elif _roman(word) and "number" not in segment:
                segment["number"] = _roman(word)
                segment["roman"] = True
            else:
                return None
    if any(ch not in _PUNCTUATION for ch in text[position:]):
        return None

    eras = {s["era"] for s in segments if "era" in s}
    units = {s["unit"] for s in segments if "unit" in s}
    numbered = [s for s in segments if "number" in s]
    if len(numbered) not in (1, 2) or len(units) > 1:
        return None
    unit = next(iter(units), None)
    spans = []
    for segment in numbered:
        era = segment.get("era") or (next(iter(eras)) if len(eras) == 1 else None)
        if unit is None and segment.get("roman"):
            return None  # 'II' alone is a phase number, not a year
        span = _span(segment["number"], era, unit, segment.get("qualifier"))
        if span is None:
            return None
        spans.append(span)
    return Placed(spans[0][0], spans[-1][1], explicit=bool(eras or units))


# --- words that connect a label to PeriodO -----------------------------------------

# Abbreviations PeriodO does not always list. Turkish ETÇ/İTÇ, OTÇ, GTÇ/STÇ fold to
# etc/itc, otc, gtc/stc.
_ABBREVIATIONS = {
    "eb": "early bronze age", "eba": "early bronze age", "mb": "middle bronze age",
    "mba": "middle bronze age", "lb": "late bronze age", "lba": "late bronze age",
    "ba": "bronze age", "ia": "iron age", "eia": "early iron age", "mia": "middle iron age",
    "lia": "late iron age", "eh": "early helladic", "mh": "middle helladic",
    "lh": "late helladic", "em": "early minoan", "mm": "middle minoan", "lm": "late minoan",
    "ppn": "pre pottery neolithic", "pn": "pottery neolithic",
    "in": "initial neolithic", "en": "early neolithic", "mn": "middle neolithic",
    "ln": "late neolithic", "fn": "final neolithic", "an": "aceramic neolithic",
    "lan": "late aceramic neolithic", "ech": "early chalcolithic",
    "mch": "middle chalcolithic", "lch": "late chalcolithic",
    "etc": "early bronze age", "itc": "early bronze age", "otc": "middle bronze age",
    "gtc": "late bronze age", "stc": "late bronze age", "edc": "early iron age",
    "odc": "middle iron age", "gdc": "late iron age",
}  # fmt: skip

# Not dates, only words: how a Turkish or German label reads in the English most
# PeriodO sources use. PeriodO itself has almost no Turkish period names.
_TURKISH = {
    "tunc cagi": "bronze age", "bronz cagi": "bronze age", "demir cagi": "iron age",
    "bakir cagi": "copper age", "tas cagi": "stone age", "bakir tas": "chalcolithic",
    "orta cag": "medieval", "ortacag": "medieval", "tarih oncesi": "prehistoric",
    "gec antik": "late antique", "gec antikcag": "late antique", "dogu roma": "byzantine",
    "gec hitit": "neo hittite", "yeni asur": "neo assyrian", "eski asur": "old assyrian",
    "orta asur": "middle assyrian", "yeni babil": "neo babylonian",
    "eski babil": "old babylonian", "asur ticaret kolonileri": "old assyrian",
    "akeramik neolitik": "pre pottery neolithic",
    "canak comleksiz neolitik": "pre pottery neolithic",
    "canak comlekli neolitik": "pottery neolithic",
    "paleolitik": "paleolithic", "epipaleolitik": "epipaleolithic", "mezolitik": "mesolithic",
    "neolitik": "neolithic", "kalkolitik": "chalcolithic", "hitit": "hittite",
    "asur": "assyrian", "babil": "babylonian", "frig": "phrygian", "urartu": "urartian",
    "lidya": "lydian", "pers": "persian", "akhaimenid": "achaemenid", "akamenid": "achaemenid",
    "geometrik": "geometric", "arkaik": "archaic", "klasik": "classical",
    "helenistik": "hellenistic", "hellenistik": "hellenistic", "roma": "roman",
    "bizans": "byzantine", "islami": "islamic", "islam": "islamic", "emevi": "umayyad",
    "abbasi": "abbasid", "selcuklu": "seljuq",
    "anadolu selcuklu": "seljuqs of rum", "eyyubi": "ayyubid", "memluk": "mamluk",
    "hacli": "crusader", "osmanli": "ottoman", "miken": "mycenaean", "minos": "minoan",
    "prehistorik": "prehistoric", "protohistorik": "protohistoric",
    "erken": "early", "ilk": "early", "orta": "middle", "gec": "late", "son": "late",
    "eski": "old", "yeni": "neo", "ust": "upper", "alt": "lower",
    "cagi": "age", "cag": "age", "donemi": "period", "donem": "period", "devri": "period",
    "devir": "period", "kulturu": "culture", "kultur": "culture",
    "imparatorluk": "empire", "imparatorlugu": "empire", "kralligi": "kingdom",
}  # fmt: skip
_GERMAN = {
    "bronzezeit": "bronze age", "eisenzeit": "iron age", "kupferzeit": "copper age",
    "steinzeit": "stone age", "jungsteinzeit": "neolithic", "neolithikum": "neolithic",
    "mittelsteinzeit": "mesolithic", "mesolithikum": "mesolithic",
    "altsteinzeit": "paleolithic", "palaolithikum": "paleolithic",
    "chalkolithikum": "chalcolithic", "hallstattzeit": "hallstatt", "latenezeit": "la tene",
    "kaiserzeit": "imperial period", "volkerwanderungszeit": "migration period",
    "mittelalter": "medieval", "neuzeit": "modern", "glockenbecherkultur": "bell beaker culture",
    "glockenbecher": "bell beaker", "schnurkeramik": "corded ware",
    "bandkeramik": "linear pottery", "linearbandkeramik": "linear pottery",
    "urnenfelderzeit": "urnfield", "urnenfelderkultur": "urnfield culture",
    "hellenistisch": "hellenistic", "hellenistische": "hellenistic", "romisch": "roman",
    "romische": "roman", "byzantinisch": "byzantine", "byzantinische": "byzantine",
    "klassisch": "classical", "klassische": "classical", "archaisch": "archaic",
    "archaische": "archaic", "fruh": "early", "fruhe": "early", "fruhes": "early",
    "mittlere": "middle", "mittleres": "middle", "spat": "late", "spate": "late",
    "spates": "late", "zeit": "period", "epoche": "period", "kultur": "culture",
}  # fmt: skip
_GERMAN_PREFIXES = {"fruh": "early", "mittel": "middle", "spat": "late", "hoch": "high"}
_LANGUAGES = (
    ("tr", _TURKISH, ("Turkey",)),
    ("de", _GERMAN, ("Germany", "Austria", "Switzerland")),
)
_LONGEST_PHRASE = 3

_FILLER = {"period", "periods", "era", "epoch", "times", "the", "of"}
_SUFFIXES = ("period", "age", "culture", "dynasty")
# PeriodO has entries called "Iron", "Late" and "I". Alone they are a material, a
# qualifier, a numeral: never enough to call a label a period.
_NOT_ALONE = _EARLY | _MIDDLE | _LATE | {
    "iron", "bronze", "copper", "stone", "modern",
    "demir", "bronz", "tunc", "bakir", "tas", "eisen", "kupfer", "stein",
}  # fmt: skip
_WORLD = {"Earth", "World"}
_PHASE = re.compile(r"^(x{0,3}(?:ix|iv|v?i{0,3}))([a-d]?)$")
_WORD = re.compile(r"\w+")


def _translate(tokens: list[str], glossary: dict[str, str]) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(tokens):
        for length in range(min(_LONGEST_PHRASE, len(tokens) - i), 0, -1):
            phrase = " ".join(tokens[i : i + length])
            if phrase in glossary:
                out += glossary[phrase].split()
                i += length
                break
        else:
            token = tokens[i]
            for prefix, meaning in _GERMAN_PREFIXES.items():  # Frühbronzezeit
                if (
                    glossary is _GERMAN
                    and token.startswith(prefix)
                    and token[len(prefix) :] in glossary
                ):
                    out += [meaning, *glossary[token[len(prefix) :]].split()]
                    break
            else:
                out.append(token)
            i += 1
    return out


def _forms(tokens: list[str]) -> list[str]:
    """The label as PeriodO might spell it: 'period', 'age' or 'culture' may be
    written or left out."""
    base = [t for t in tokens if t not in _FILLER]
    if not base or (len(base) == 1 and (base[0] in _NOT_ALONE or len(base[0]) < 3)):
        return []
    forms = [tokens, base, *([*base, suffix] for suffix in _SUFFIXES)]
    if base[-1] in _SUFFIXES and len(base) > 1:
        forms.append(base[:-1])
    return [" ".join(form) for form in forms]


def _lookup(tokens: list[str]) -> tuple[Definition, ...]:
    """Every PeriodO definition of the label."""
    found: dict[str, Definition] = {}
    for form in _forms(tokens):
        for definition in gazetteer().find(form):
            found.setdefault(definition.id, definition)
    return tuple(found.values())


def _expand(tokens: list[str]) -> list[str]:
    return [word for t in tokens for word in _ABBREVIATIONS.get(t, t).split()]


@dataclass
class _Part:
    """One period name inside a label, with every definition it could mean."""

    candidates: tuple[Definition, ...]
    via: str
    language: str | None = None
    tokens: tuple[str, ...] = ()  # what was looked up, to show the label that matched
    qualifier: str | None = None
    phase: int | None = None
    letter: int | None = None

    def span(self, definition: Definition) -> tuple[float, float]:
        start, end = _third(definition.start, definition.stop, self.qualifier)
        if self.phase is not None:  # EB I, II, III: equal slices, in order
            step = (end - start) / max(3, self.phase)
            start, end = start + (self.phase - 1) * step, start + self.phase * step
        if self.letter is not None:  # IIA, IIB
            step = (end - start) / 4
            start, end = start + self.letter * step, start + (self.letter + 1) * step
        return start, end


def _derive(tokens: list[str], language: str | None) -> _Part | None:
    """'Erken Kalkolitik', 'Iron III': a named part of a period PeriodO defines
    as a whole. Phase numbers are tried first, then the qualifier as well."""
    phase = letter = None
    rest: list[str] = []
    for token in tokens:
        match = _PHASE.match(token) if not token.isdigit() else None
        if token.isdigit() and phase is None and 1 <= int(token) <= 12:
            phase = int(token)
        elif match and rest and (phase is None or letter is None):
            numeral, suffix = match.groups()
            if (numeral and phase is not None) or (suffix and letter is not None):
                return None
            phase = _roman(numeral) if numeral else phase
            letter = "abcd".index(suffix) if suffix else letter
        else:
            rest.append(token)
    if phase is not None or letter is not None:
        hits = _lookup(rest)
        if hits:
            return _Part(hits, "derived", language, tuple(rest), None, phase, letter)
    qualifiers = [q for q in map(_qualifier, rest) if q]
    if len(qualifiers) == 1:
        plain = [t for t in rest if not _qualifier(t)]
        hits = _lookup(plain)
        if hits:
            return _Part(hits, "derived", language, tuple(plain), qualifiers[0], phase, letter)
    return None


def _name(text: str) -> list[_Part]:
    """Every way the label reads as a PeriodO period, most literal first. Several
    readings are kept because the literal one can be the wrong language:
    'Neolitik' is a Slovenian PeriodO label and also Turkish for Neolithic. The
    column decides (`resolve`)."""
    tokens = key(text).split()
    if not tokens or len(tokens) > 8:
        return []
    readings: list[_Part] = []
    if hits := _lookup(tokens):
        readings.append(_Part(hits, "periodo", None, tuple(tokens)))
    expanded = _expand(tokens)
    # "MM IA": the first word is the abbreviation, IA here is a phase, not Iron Age.
    for attempt in (expanded, _expand(tokens[:1]) + tokens[1:]):
        if attempt != tokens and (hits := _lookup(attempt)):
            readings.append(_Part(hits, "abbreviation", None, tuple(attempt)))
            break
    derived: list[_Part] = []
    for language, glossary, _regions in _LANGUAGES:
        translated = _expand(_translate(tokens, glossary))
        if translated != expanded:
            if hits := _lookup(translated):
                readings.append(_Part(hits, "translation", language, tuple(translated)))
            elif part := _derive(translated, language):
                derived.append(part)
    if not readings:
        fallback = _derive(expanded, None)
        readings = derived or ([fallback] if fallback else [])
    return readings


# --- one column ----------------------------------------------------------------

_PARENTHESES = re.compile(r"^(.*?)\((.*?)\)(.*)$")
_ALTERNATIVE = re.compile(r"\s*(?:\bor\b|\bveya\b|\boder\b|=)\s*")
_TRANSITION = re.compile(r"\s*(?:/|-|\bto\b|\band\b|\bve\b|\bile\b)\s*")
_UNDATED = {
    "unknown", "undated", "undetermined", "indeterminate", "uncertain", "unclear",
    "mixed", "unstratified", "topsoil", "surface", "none", "other",
    "belirsiz", "bilinmiyor", "bilinmeyen", "karisik", "yuzey", "yuzey topragi",
    "tanimsiz", "tarihsiz", "tarihlenemeyen", "diger", "yok",
    "unbekannt", "undatiert", "unbestimmt",
}  # fmt: skip


def is_undated(value: str) -> bool:
    """'Unknown', 'Karışık', '?': an honest gap, not a failure to read a label."""
    text = fold(value).strip(" .?-()")
    return not text or text in _UNDATED


@dataclass(frozen=True)
class Match:
    """Where one value was put, and on whose authority."""

    value: str
    start: float
    stop: float
    via: str  # periodo | abbreviation | translation | derived | year | model | user | data
    label: str | None = None  # the PeriodO label
    id: str | None = None  # the PeriodO id; its permalink is periodo.PERMALINK + id
    source: str | None = None
    varies: bool = False  # via data: the rows with this value do not all give the same dates

    def as_dict(self) -> dict:
        out = {"value": self.value, "start": round(self.start), "stop": round(self.stop)}
        out["via"] = self.via
        for name in ("label", "id", "source"):
            if getattr(self, name):
                out[name] = getattr(self, name)
        if self.varies:
            out["varies"] = True
        return out


@dataclass
class Resolution:
    order: list[str]  # every value, oldest first, the unplaced ones last
    unplaced: list[str]
    matches: list[Match]  # in the order of `order`
    region: str | None  # the region(s) PeriodO definitions were chosen for
    strong: bool = False  # something said outright that this is a chronology
    names: list[str] = field(default_factory=list)  # values that are names, placed or not


def _read(value: str) -> Placed | list[list[_Part]] | None:
    """A date, or the one or two period names in the label (each with its
    possible readings), or nothing."""
    text = fold(value)
    if not text:
        return None
    whole = _numeric(text) or _name(text)
    if whole:
        return whole if isinstance(whole, Placed) else [whole]
    match = _PARENTHESES.match(text)
    if match:  # "Hellenistic (330-30 BC)": the years say more than the name
        inner, outer = match.group(2), f"{match.group(1)} {match.group(3)}".strip()
        found = _numeric(inner) or _numeric(outer) or _name(outer) or _name(inner)
        if found:
            return found if isinstance(found, Placed) else [found]
    for piece in _ALTERNATIVE.split(text)[1:]:  # "Late Neolithic or LN": either will do
        found = _numeric(piece) or _name(piece)
        if found:
            return found if isinstance(found, Placed) else [found]
    pieces = [p for p in _TRANSITION.split(text) if p]
    if len(pieces) == 2:  # "Late Bronze Age / Early Iron Age", "Roma-Bizans", "LN-FN"
        first, second = _name(pieces[0]), _name(pieces[1])
        if first and not second:  # "EM I-III": the second end borrows the name
            name = [t for t in key(pieces[0]).split() if not (t.isdigit() or _PHASE.match(t))]
            lone_letter = len(pieces[1].strip()) == 1  # "LH IIIB-C": C of what is unclear
            second = _name(" ".join([*name, pieces[1]])) if name and not lone_letter else []
        if first and second:
            return [first, second]
        if first:  # "LH IIIB-C": where it starts is enough to order it
            return [first]
    return None


def _regions(names: list[list[_Part]]) -> set[str]:
    """The region most labels have a definition for; several when they tie.
    Labels written in Turkish or German lean towards where those are spoken.
    One name alone points nowhere, so it gets no region."""
    votes: Counter[str] = Counter()
    for readings in names:  # one vote per name, however many ways it reads
        votes.update({r for p in readings for d in p.candidates for r in d.regions} - _WORLD)
    languages = {p.language for readings in names for p in readings if p.language}
    bonus = max(1.0, len(names) / 4)
    for language, _glossary, regions in _LANGUAGES:
        if language in languages:
            for region in regions:
                votes[region] += bonus
    best = max(votes.values(), default=0)
    return {r for r, n in votes.items() if n == best} if best >= 2 else set()


def _choose(
    readings: list[_Part], regions: set[str], authorities: Counter[str]
) -> tuple[_Part, Definition]:
    """The first reading that has a definition for the region, and among those
    definitions the one nearest their middle: the consensus date, not the
    outlier. Ties go to the source that defines most of the column, then the
    narrower definition, then the more recent publication."""
    part, pool = readings[0], list(readings[0].candidates)
    for reading in readings:
        local = [d for d in reading.candidates if regions & set(d.regions)]
        if local:
            part, pool = reading, local
            break
    middle_start = median(d.start for d in pool)
    middle_stop = median(d.stop for d in pool)

    def rank(d: Definition):
        year = gazetteer().sources.get(d.authority, ("", ""))[1]
        return (
            abs(d.start - middle_start) + abs(d.stop - middle_stop),
            -authorities[d.authority],
            len(d.regions) if d.regions else 999,
            -int(year) if year.isdigit() else 0,
            d.id,
        )

    return part, min(pool, key=rank)


def _answered(answer: dict) -> Placed | list[list[_Part]] | None:
    """What the model said about one label (generation/periods.py): a period
    name to look up in PeriodO like any other, or failing that its own years."""
    name = answer.get("name")
    readings = _name(name) if isinstance(name, str) else []
    if readings:
        return [readings]
    start, end = answer.get("start"), answer.get("end")
    if isinstance(start, int) and isinstance(end, int):
        return Placed(min(start, end), max(start, end), explicit=False)
    return None


def resolve(
    values: Iterable[str],
    answers: dict[str, dict] | None = None,
    mappings: dict[str, str] | None = None,
    spans: dict[str, tuple[float, float, bool]] | None = None,
) -> Resolution:
    """Put the distinct values of one column on a timeline.

    `spans` are dates the dataset itself gives for a value, in start and end
    columns the user pointed at: (start, end, do the rows disagree). They come
    before PeriodO, because they are what the author of the data meant.

    `mappings` are the user's: "ECh" means "Early Chalcolithic", "Evre 7" means
    "720-650 BC". They are read like any label and come before everything else.
    `answers` are what the user's model said about labels nothing here could
    read; they are used only for those labels."""
    answers = answers or {}
    mappings = {v: text for v, text in (mappings or {}).items() if str(text).strip()}
    spans = {v: span for v, span in (spans or {}).items() if v not in mappings}
    distinct = list(dict.fromkeys(str(v) for v in values))
    read: dict[str, Placed | list[list[_Part]] | None] = {}
    asked: set[str] = set()
    for value in distinct:
        if value in mappings:
            read[value] = _read(mappings[value])
            continue
        if value in spans:
            read[value] = Placed(spans[value][0], spans[value][1], explicit=True)
            continue
        read[value] = None if is_undated(value) else _read(value)
        if read[value] is None and value in answers and not is_undated(value):
            read[value] = _answered(answers[value])
            asked.add(value)

    names = [readings for found in read.values() if isinstance(found, list) for readings in found]
    regions = _regions(names)
    authorities: Counter[str] = Counter()
    for readings in names:
        authorities.update(
            {
                d.authority
                for part in readings
                for d in part.candidates
                if not regions or regions & set(d.regions)
            }
        )

    matches: list[Match] = []
    unplaced: list[str] = []
    strong = False
    for value in distinct:
        found = read[value]
        if isinstance(found, Placed):
            if value in asked:  # the model's own estimate, no PeriodO definition behind it
                label = str(answers[value].get("name") or "") or None
                matches.append(Match(value, found.start, found.end, "model", label))
            else:
                via = "user" if value in mappings else "data" if value in spans else "year"
                varies = via == "data" and spans[value][2]
                matches.append(Match(value, found.start, found.end, via, varies=varies))
            strong = strong or found.explicit
        elif found:
            chosen = [_choose(readings, regions, authorities) for readings in found]
            ranges = [part.span(definition) for part, definition in chosen]
            start, stop = ranges[0][0], max(span[1] for span in ranges)
            if len(ranges) == 2:  # a transition starts where the two meet
                start = max(start, min(ranges[0][1], ranges[1][0]) - 0.5)
            first, definition = chosen[0]
            matches.append(
                Match(
                    value,
                    start,
                    stop,
                    "user" if value in mappings else "model" if value in asked else first.via,
                    " / ".join(d.called(set(_forms(list(p.tokens)))) for p, d in chosen),
                    definition.id,
                    gazetteer().source(definition),
                )
            )
            strong = strong or any(len(p.candidates) >= 3 and p.via != "derived" for p, _ in chosen)
        else:
            unplaced.append(value)

    matches.sort(key=lambda m: (m.start, m.stop, fold(m.value), m.value))
    unplaced.sort(key=lambda v: (fold(v), v))
    return Resolution(
        order=[m.value for m in matches] + unplaced,
        unplaced=unplaced,
        matches=matches,
        region=", ".join(sorted(regions)[:4]) or None,
        strong=strong,
        names=[v for v, found in read.items() if not isinstance(found, Placed)],
    )


def chronological(values: Iterable[str]) -> tuple[list[str], list[str]]:
    """(order, unplaced): oldest first, the unplaced values at the end."""
    resolution = resolve(values)
    return resolution.order, resolution.unplaced


_HEADER_HINTS = (
    "period", "phase", "epoch", "chronolog", "dating", "date",
    "donem", "evre", "cag", "kronoloji", "tarihlendirme", "epoche", "zeit", "datierung",
)  # fmt: skip


def looks_chronological(values: Iterable[str], column: str = "") -> bool:
    """Is this text column a period column? At least two values and four in five
    of the dated ones must be placed, and one must be beyond doubt: a year with
    its era, or a name that several PeriodO sources define. A column of bare
    numbers, or of one obscure name, is not enough.

    A header that says so ("Phase/Period", "Dönem") is context too: then one
    value in four is enough, because real period columns are full of site
    abbreviations nothing can read, and the user is shown what was not placed."""
    distinct = list(dict.fromkeys(str(v) for v in values))
    if len(distinct) > MAX_DISTINCT:
        return False
    resolution = resolve(distinct)
    dated = [v for v in distinct if not is_undated(v)]
    placed = len(resolution.matches)
    share = 0.25 if any(hint in key(column) for hint in _HEADER_HINTS) else 0.8
    return placed >= 2 and placed >= share * len(dated) and resolution.strong


def user_order(values: Iterable[str], wanted: list[str]) -> tuple[list[str], list[str]]:
    """The user's order, restricted to values that occur. Values the user did not
    list are unplaced and go last, in the order `chronological` would give them."""
    present = list(dict.fromkeys(str(v) for v in values))
    listed = [v for v in dict.fromkeys(wanted) if v in set(present)]
    rest, _ = chronological(v for v in present if v not in set(listed))
    return listed + rest, rest
