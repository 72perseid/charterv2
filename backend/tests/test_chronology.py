"""The period matcher against the vendored PeriodO snapshot. Dates asserted here
are PeriodO's; when a snapshot refresh moves one, the test that fails says which."""

import pytest

from datasets.chronology import (
    chronological,
    is_undated,
    looks_chronological,
    resolve,
    user_order,
)
from datasets.periodo import gazetteer, key


def one(label: str):
    matches = resolve([label]).matches
    return matches[0] if matches else None


def test_snapshot_loads():
    g = gazetteer()
    assert len(g.by_label) > 10_000 and g.snapshot
    iron = g.find(key("Iron Age"))
    assert len(iron) > 50  # one name, many definitions: the reason for `resolve`
    assert g.find(key("Pre-Pottery Neolithic B")) and g.find(key("PPNB"))
    assert iron[0].url.startswith("http://n2t.net/ark:/99152/p0")


@pytest.mark.parametrize(
    ("label", "start", "end"),
    [
        ("-1500", -1500, -1500),
        ("1500 BC", -1500, -1500),
        ("1500 B.C.E.", -1500, -1500),
        ("MÖ 1500", -1500, -1500),
        ("M.Ö. 1500", -1500, -1500),
        ("İ.Ö. 300", -300, -300),
        ("M.S. 200", 200, 200),
        ("ca. 1500 BC", -1500, -1500),
        ("10.000 BC", -10000, -10000),
        ("9000 BP", -7050, -7050),
        ("1500-1200 BC", -1500, -1200),
        ("MÖ 1500–1200", -1500, -1200),
        ("100 BC - 100 AD", -100, 100),
        ("5th century BC", -500, -401),
        ("5th c. BC", -500, -401),
        ("MÖ 5. yüzyıl", -500, -401),
        ("MÖ IV. yüzyıl", -400, -301),
        ("MÖ 5.-4. yüzyıl", -500, -301),
        ("2nd century AD", 101, 200),
        ("MÖ 3. binyıl", -3000, -2001),
        ("Hellenistic (330-30 BC)", -330, -30),  # the years say more than the name
    ],
)
def test_dates_are_read_directly(label, start, end):
    match = one(label)
    assert match is not None, label
    assert (match.start, match.stop, match.via) == (start, end, "year")


@pytest.mark.parametrize(
    ("label", "via", "periodo_label"),
    [
        ("Late Helladic IIIC", "periodo", "Late Helladic IIIC"),
        ("LH IIIC", "abbreviation", "Late Helladic IIIC"),
        ("Bell Beaker", "periodo", None),  # found as "Bell Beaker culture"
        ("Geç Tunç Çağı", "translation", "Late Bronze Age"),
        ("Helenistik", "translation", None),
        ("Glockenbecherkultur", "translation", None),
        ("Frühbronzezeit", "translation", "Early Bronze Age"),
    ],
)
def test_names_are_connected_to_periodo(label, via, periodo_label):
    match = one(label)
    assert match is not None, label
    assert match.via == via and match.id and match.source
    if periodo_label:
        assert match.label == periodo_label


@pytest.mark.parametrize(
    "label",
    ["Trench 5", "Açma A", "II", "A", "12a", "KH-001", "Roman Red Slip", "Iron", "Bronz", "Late"],
)
def test_what_is_not_a_period(label):
    assert one(label) is None


def test_undated_words():
    assert is_undated("Unknown") and is_undated("Karışık") and is_undated("?")
    assert not is_undated("Roman")


def test_turkish_column_is_ordered_for_turkey():
    labels = [
        "Roma",
        "Helenistik",
        "Geç Tunç Çağı",
        "Bizans",
        "Karışık",
        "Demir Çağı",
        "Kalkolitik",
    ]
    labels += ["Neolitik", "Erken Tunç Çağı", "Osmanlı", "Selçuklu"]
    resolution = resolve(labels)
    assert resolution.region == "Turkey"
    assert resolution.order == [
        "Neolitik",  # also a Slovenian PeriodO label dated for the Balkans; Turkey wins
        "Kalkolitik",
        "Erken Tunç Çağı",
        "Geç Tunç Çağı",
        "Demir Çağı",
        "Helenistik",
        "Roma",
        "Bizans",
        "Selçuklu",
        "Osmanlı",
        "Karışık",
    ]
    assert resolution.unplaced == ["Karışık"]


def test_the_same_names_get_the_dates_of_their_region():
    britain = resolve(["Bronze Age", "Iron Age", "Roman", "Anglo-Saxon", "Medieval"])
    assert "England" in britain.region
    roman = next(m for m in britain.matches if m.value == "Roman")
    assert (roman.start, roman.stop) == (43, 410)  # not the Mediterranean's 30 BC

    anatolia = resolve(["Bronze Age", "Iron Age", "Roman", "Hittite", "Phrygian"])
    assert "Turkey" in anatolia.region
    iron = {
        r.region: next(m.start for m in r.matches if m.value == "Iron Age")
        for r in (britain, anatolia)
    }
    assert iron[britain.region] > -900 and iron[anatolia.region] < -1000


def test_european_and_german_columns():
    order, unplaced = chronological(
        ["Roman", "La Tène", "Bell Beaker", "Hallstatt", "Corded Ware", "Urnfield", "Neolithic"]
    )
    assert unplaced == []
    assert order == [
        "Neolithic", "Corded Ware", "Bell Beaker", "Urnfield", "Hallstatt", "La Tène", "Roman"
    ]  # fmt: skip
    german = ["Eisenzeit", "Mittelalter", "Jungsteinzeit", "Bronzezeit", "Römische Kaiserzeit"]
    assert chronological(german)[0] == [
        "Jungsteinzeit", "Bronzezeit", "Eisenzeit", "Römische Kaiserzeit", "Mittelalter"
    ]  # fmt: skip


def test_phases_and_transitions_fall_in_between():
    order, unplaced = chronological(
        [
            "LB IIB",
            "Iron II",
            "EB III",
            "LB I",
            "Late Bronze Age / Early Iron Age",
            "LB IIA",
            "EB I",
        ]
    )
    assert unplaced == []
    assert order[:5] == ["EB I", "EB III", "LB I", "LB IIA", "LB IIB"]
    assert set(order[5:]) == {"Late Bronze Age / Early Iron Age", "Iron II"}


def test_mixed_notations_share_one_timeline():
    order, _ = chronological(["200 AD", "1500 BC", "Roman", "MÖ 3000", "-800", "5th century BC"])
    assert order == ["MÖ 3000", "1500 BC", "-800", "5th century BC", "Roman", "200 AD"]


def test_detection():
    assert looks_chronological(["Roma", "Helenistik", "Karışık"])
    assert looks_chronological(["1500 BC", "1200 BC", "-800"])
    assert not looks_chronological(["Iron", "Bronze"])  # materials
    assert not looks_chronological(["Demir", "Bronz", "Kemik"])
    assert not looks_chronological(["1", "2", "3"])  # no era anywhere
    assert not looks_chronological(["Açma A", "Açma B"])
    assert not looks_chronological(["Roman"])  # one label is not a scale
    assert not looks_chronological(["Roman", "Byzantine", "Kiln", "Pit", "Wall"])
    # PeriodO lists sultans and words like "Early"; names alone must not make a period column.
    assert not looks_chronological(["İbrahim", "Abdülaziz", "Osman"])
    assert not looks_chronological(["Early", "Late", "Middle"])
    assert not looks_chronological(["Pottery", "Bone", "Glass", "Metal"])


def test_model_answers_fill_only_the_gaps():
    values = ["Roma", "Helenistik", "Erken Hristiyanlık", "Evre 7", "Açma B"]
    assert resolve(values).unplaced == ["Açma B", "Erken Hristiyanlık", "Evre 7"]
    answers = {
        "Erken Hristiyanlık": {"name": "Early Christian", "start": 100, "end": 600},
        "Evre 7": {"name": "Kinet Phase 7", "start": -700, "end": -650},
        "Roma": {"name": "Neolithic", "start": -9000, "end": -6000},  # not asked: ignored
    }
    resolution = resolve(values, answers)
    assert resolution.order == ["Evre 7", "Helenistik", "Roma", "Erken Hristiyanlık", "Açma B"]
    by_value = {m.value: m for m in resolution.matches}
    assert by_value["Roma"].via == "translation"
    # A name PeriodO knows is dated by PeriodO; one it does not know keeps the model's years.
    assert by_value["Erken Hristiyanlık"].via == "model" and by_value["Erken Hristiyanlık"].id
    assert by_value["Evre 7"].via == "model" and by_value["Evre 7"].id is None
    assert (by_value["Evre 7"].start, by_value["Evre 7"].stop) == (-700, -650)


def test_user_order_keeps_what_exists_and_appends_the_rest():
    values = ["Phase 3", "Phase 1", "Roman", "Phase 2"]
    order, unplaced = user_order(values, ["Phase 3", "Phase 2", "Phase 9", "Phase 1"])
    assert order == ["Phase 3", "Phase 2", "Phase 1", "Roman"]
    assert unplaced == ["Roman"]


def test_site_abbreviations_ranges_and_alternatives():
    # From a real Aegean zooarchaeology table: most of the column is shorthand.
    labels = ["LN", "FN", "EN", "MN", "ECh", "LN-FN", "MN-LN", "FN/ECh", "EM I-III", "MM IA-II"]
    labels += ["LH IIIA2-B1", "LH IIIB-C", "EH II", "Roman", "Palatial", "C-PPNA"]
    resolution = resolve(labels)
    assert resolution.unplaced == ["C-PPNA", "Palatial"]
    order = resolution.order
    assert order.index("EN") < order.index("MN") < order.index("LN") < order.index("FN")
    assert order.index("MN") < order.index("MN-LN") <= order.index("LN")
    assert order.index("EH II") < order.index("MM IA-II") < order.index("LH IIIA2-B1")
    assert order.index("LH IIIB-C") < order.index("Roman")
    by_value = {m.value: m for m in resolution.matches}
    assert by_value["LN"].label == "Late Neolithic"  # the label that matched, in English
    assert by_value["MM IA-II"].label.startswith("Middle Minoan IA")  # IA is a phase here
    assert [m.label for m in resolve(["Late Neolithic or LN"]).matches] == ["Late Neolithic"]
    assert [m.label for m in resolve(["Early Chalcolithic (ECh)"]).matches] == [
        "Early Chalcolithic"
    ]


def test_a_header_that_says_period_lowers_the_bar():
    labels = ["Roman", "Byzantine", "Kiln", "Pit", "Wall", "T1", "T2"]
    assert not looks_chronological(labels)
    assert not looks_chronological(labels, "Feature")
    assert looks_chronological(labels, "Phase/Period")
    assert looks_chronological(labels, "Dönem")
    assert not looks_chronological(["Kiln", "Pit", "Wall"], "Period")  # still needs periods


def test_user_mappings_come_first():
    values = ["Roman", "Palatial", "C-PPNA", "Evre 7", "LN"]
    mappings = {
        "Palatial": "Middle Minoan",  # a name: dated by PeriodO
        "C-PPNA": "9000-8500 BC",  # a date
        "Evre 7": "no such period",  # unreadable: stays unplaced
        "LN": "Late Bronze Age",  # overrules what the label would have meant
    }
    resolution = resolve(values, None, mappings)
    assert resolution.order == ["C-PPNA", "Palatial", "LN", "Roman", "Evre 7"]
    assert resolution.unplaced == ["Evre 7"]
    by_value = {m.value: m for m in resolution.matches}
    assert by_value["Palatial"].via == "user" and by_value["Palatial"].id
    assert (by_value["C-PPNA"].start, by_value["C-PPNA"].via) == (-9000, "user")
    assert by_value["LN"].label == "Late Bronze Age" and by_value["Roman"].via == "periodo"
