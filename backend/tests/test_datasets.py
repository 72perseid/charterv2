import json
from pathlib import Path

import pytest
from django.test import Client

from accounts.models import User
from datasets.models import Dataset
from datasets.tasks import process_one_dataset
from tests.conftest import CsrfClient
from tests.fixtures import turkish_csv_bytes, workbook_with_title_row

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def data_dir(settings, tmp_path):
    settings.DATA_DIR = tmp_path / "data"
    return settings.DATA_DIR


def upload(client: Client, name: str, content: bytes, filename: str):
    from django.core.files.uploadedfile import SimpleUploadedFile

    return client.post(
        "/api/datasets", {"name": name, "file": SimpleUploadedFile(filename, content)}
    )


def test_list_requires_auth(client: Client):
    assert client.get("/api/datasets").status_code == 401


def test_list_is_empty_for_new_user(user_client: Client):
    response = user_client.get("/api/datasets")
    assert response.status_code == 200
    assert response.json() == []


def test_list_shows_only_own_datasets(user_client: Client):
    other = User.objects.create_user(email="other@example.org", password="correct-horse-9")
    Dataset.objects.create(
        user=other, name="theirs", original_filename="t.csv", original_path="/x/t.csv"
    )
    me = User.objects.get(email="ada@example.org")
    Dataset.objects.create(
        user=me, name="mine", original_filename="m.csv", original_path="/x/m.csv"
    )
    names = [d["name"] for d in user_client.get("/api/datasets").json()]
    assert names == ["mine"]


def test_upload_then_worker_parses_turkish_csv(user_client: CsrfClient, data_dir: Path):
    response = upload(user_client, "Kinet 2019", turkish_csv_bytes(), "kinet.csv")
    assert response.status_code == 201, response.content
    body = response.json()
    assert body["status"] == "pending"
    dataset_id = body["id"]
    user_id = User.objects.get(email="ada@example.org").id
    assert (data_dir / str(user_id) / str(dataset_id) / "original.csv").exists()

    assert process_one_dataset() is True
    assert process_one_dataset() is False  # nothing left

    detail = user_client.get(f"/api/datasets/{dataset_id}").json()
    assert detail["status"] == "done", detail["error_message"]
    assert detail["row_count"] == 6 and detail["column_count"] == 7
    assert detail["parse_options"]["encoding"] == "cp1254"
    types = {c["name"]: c["type"] for c in detail["profile"]["columns"]}
    assert types["Tarih"] == "date" and types["Sayı"] == "integer"

    rows = user_client.get(f"/api/datasets/{dataset_id}/rows?limit=2").json()
    assert rows["total"] == 6 and len(rows["rows"]) == 2
    assert rows["rows"][0]["Derinlik (m)"] == 1.25
    assert rows["rows"][0]["Tarih"].startswith("2019-05-03")


def test_upload_rejects_xls_and_oversize(user_client: CsrfClient, settings):
    assert upload(user_client, "old", b"x", "old.xls").status_code == 400
    settings.UPLOAD_MAX_BYTES = 10
    response = upload(user_client, "big", b"a,b\n" * 10, "big.csv")
    assert response.status_code == 413


def test_upload_rate_limit(user_client: CsrfClient, settings):
    settings.RATE_UPLOADS_PER_HOUR = 2
    assert upload(user_client, "1", b"a\n1\n", "a.csv").status_code == 201
    assert upload(user_client, "2", b"a\n1\n", "b.csv").status_code == 201
    assert upload(user_client, "3", b"a\n1\n", "c.csv").status_code == 429


def test_xlsx_sheet_override_reingests(user_client: CsrfClient, tmp_path: Path):
    content = workbook_with_title_row(tmp_path / "book.xlsx").read_bytes()
    dataset_id = upload(user_client, "book", content, "book.xlsx").json()["id"]
    process_one_dataset()
    detail = user_client.get(f"/api/datasets/{dataset_id}").json()
    assert detail["status"] == "done" and detail["sheet_name"] == "Veri"
    assert detail["parse_options"]["sheets"] == ["Notlar", "Veri"]

    response = user_client.patch(
        f"/api/datasets/{dataset_id}",
        json.dumps({"sheet": "Notlar"}),
        content_type="application/json",
    )
    assert response.status_code == 200 and response.json()["status"] == "pending"
    process_one_dataset()
    detail = user_client.get(f"/api/datasets/{dataset_id}").json()
    assert detail["status"] == "failed"
    assert "empty" in detail["error_message"]


def test_patch_privacy_and_name(user_client: CsrfClient):
    dataset_id = upload(user_client, "n", b"a\n1\n", "a.csv").json()["id"]
    response = user_client.patch(
        f"/api/datasets/{dataset_id}",
        json.dumps({"name": "Renamed", "privacy_level": "sample"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Renamed"
    assert response.json()["privacy_level"] == "sample"
    bad = user_client.patch(
        f"/api/datasets/{dataset_id}",
        json.dumps({"privacy_level": "everything"}),
        content_type="application/json",
    )
    assert bad.status_code == 400


def test_other_user_cannot_see_or_delete(user_client: CsrfClient):
    dataset_id = upload(user_client, "n", b"a\n1\n", "a.csv").json()["id"]
    other = CsrfClient(enforce_csrf_checks=True)
    other.get("/api/auth/csrf")
    other.post(
        "/api/auth/register",
        {"email": "other@example.org", "password": "correct-horse-9"},
        content_type="application/json",
    )
    assert other.get(f"/api/datasets/{dataset_id}").status_code == 404
    assert other.delete(f"/api/datasets/{dataset_id}").status_code == 404
    assert other.get(f"/api/datasets/{dataset_id}/rows").status_code == 404
    assert Dataset.objects.filter(pk=dataset_id).exists()


def test_delete_removes_row_and_directory(user_client: CsrfClient, data_dir: Path):
    dataset_id = upload(user_client, "n", b"a\n1\n", "a.csv").json()["id"]
    process_one_dataset()
    user_id = User.objects.get(email="ada@example.org").id
    directory = data_dir / str(user_id) / str(dataset_id)
    assert (directory / "parsed.parquet").exists()

    assert user_client.delete(f"/api/datasets/{dataset_id}").status_code == 204
    assert not Dataset.objects.filter(pk=dataset_id).exists()
    assert not directory.exists()


def test_rows_before_parse_is_409(user_client: CsrfClient):
    dataset_id = upload(user_client, "n", b"a\n1\n", "a.csv").json()["id"]
    assert user_client.get(f"/api/datasets/{dataset_id}/rows").status_code == 409


def test_download_returns_original(user_client: CsrfClient):
    dataset_id = upload(user_client, "n", turkish_csv_bytes(), "kinet.csv").json()["id"]
    response = user_client.get(f"/api/datasets/{dataset_id}/download")
    assert response.status_code == 200
    assert b"".join(response.streaming_content) == turkish_csv_bytes()
    assert 'filename="kinet.csv"' in response["Content-Disposition"]


PERIOD_CSV = (
    "Buluntu;Evre;Dönem;Sayı\n"
    "K1;Evre 2;Roma;4\n"
    "K2;Evre 10;Helenistik;2\n"
    "K3;Evre 1;Demir Çağı;7\n"
    "K4;Evre 2;Roma;1\n"
).encode()


def patch(client: Client, dataset_id: int, body: dict):
    return client.patch(
        f"/api/datasets/{dataset_id}", json.dumps(body), content_type="application/json"
    )


def test_period_column_and_its_overrides(user_client: CsrfClient):
    dataset_id = upload(user_client, "donem", PERIOD_CSV, "donem.csv").json()["id"]
    process_one_dataset()
    columns = {
        c["name"]: c
        for c in user_client.get(f"/api/datasets/{dataset_id}").json()["profile"]["columns"]
    }
    assert columns["Dönem"]["type"] == "period"
    assert columns["Dönem"]["order"] == ["Demir Çağı", "Helenistik", "Roma"]
    assert columns["Evre"]["type"] == "string"

    # Site phases mean nothing to the table of periods: the user gives the order.
    wanted = ["Evre 10", "Evre 2", "Evre 1"]
    response = patch(user_client, dataset_id, {"periods": {"Evre": wanted, "Dönem": False}})
    assert response.status_code == 200 and response.json()["status"] == "pending"
    process_one_dataset()
    detail = user_client.get(f"/api/datasets/{dataset_id}").json()
    columns = {c["name"]: c for c in detail["profile"]["columns"]}
    assert columns["Evre"]["type"] == "period"
    assert columns["Evre"]["order"] == wanted and columns["Evre"]["order_source"] == "user"
    assert columns["Dönem"]["type"] == "string" and "order" not in columns["Dönem"]
    assert detail["parse_options"]["overrides"]["periods"] == {"Evre": wanted, "Dönem": False}

    # null hands the column back to detection.
    patch(user_client, dataset_id, {"periods": {"Dönem": None}})
    process_one_dataset()
    detail = user_client.get(f"/api/datasets/{dataset_id}").json()
    columns = {c["name"]: c for c in detail["profile"]["columns"]}
    assert columns["Dönem"]["type"] == "period"
    assert detail["parse_options"]["overrides"]["periods"] == {"Evre": wanted}


def test_period_override_is_checked(user_client: CsrfClient):
    dataset_id = upload(user_client, "donem", PERIOD_CSV, "donem.csv").json()["id"]
    process_one_dataset()
    missing = patch(user_client, dataset_id, {"periods": {"Yok": True}})
    assert missing.status_code == 400 and "no column" in missing.json()["detail"]
    number = patch(user_client, dataset_id, {"periods": {"Sayı": True}})
    assert number.status_code == 400 and "not a text column" in number.json()["detail"]
    assert user_client.get(f"/api/datasets/{dataset_id}").json()["status"] == "done"


def test_period_values_can_be_mapped_by_hand(user_client: CsrfClient):
    content = "Buluntu;Dönem\nK1;Roma\nK2;Helenistik\nK3;Evre 7\nK4;Saray\nK5;Roma\n".encode()
    dataset_id = upload(user_client, "donem", content, "donem.csv").json()["id"]
    process_one_dataset()
    detail = user_client.get(f"/api/datasets/{dataset_id}").json()
    column = next(c for c in detail["profile"]["columns"] if c["name"] == "Dönem")
    assert column["type"] == "period"  # the header says so, two of four values are read
    assert column["unplaced"] == ["Evre 7", "Saray"]

    mappings = {"Dönem": {"Evre 7": "MÖ 720-650", "Saray": "Middle Minoan"}}
    response = patch(user_client, dataset_id, {"period_mappings": mappings})
    assert response.status_code == 200 and response.json()["status"] == "pending"
    process_one_dataset()
    detail = user_client.get(f"/api/datasets/{dataset_id}").json()
    column = next(c for c in detail["profile"]["columns"] if c["name"] == "Dönem")
    assert column["order"] == ["Saray", "Evre 7", "Helenistik", "Roma"]
    assert column["unplaced"] == []
    via = {m["value"]: m["via"] for m in column["matches"]}
    assert via["Evre 7"] == "user" and via["Saray"] == "user" and via["Roma"] == "translation"
    assert detail["parse_options"]["overrides"]["period_mappings"] == mappings

    # An empty meaning removes the mapping; an unknown column is refused.
    patch(user_client, dataset_id, {"period_mappings": {"Dönem": {"Saray": ""}}})
    process_one_dataset()
    detail = user_client.get(f"/api/datasets/{dataset_id}").json()
    assert detail["parse_options"]["overrides"]["period_mappings"] == {
        "Dönem": {"Evre 7": "MÖ 720-650"}
    }
    assert (
        patch(user_client, dataset_id, {"period_mappings": {"Yok": {"a": "b"}}}).status_code == 400
    )


DATED_CSV = (
    "Kod;Birim;Alan;Başlangıç;Bitiş;Uzunluk\n"
    "K1;Saray;A;-1900;-1370;4,5\n"
    "K2;Evre 7;A;-720;-650;3,1\n"
    "K3;Roma;B;-30;300;2,2\n"
    "K4;Evre 7;B;-700;-640;5,0\n"
    "K5;Yüzey;B;;;1,0\n"
    "K6;Helenistik;A;;;2,0\n"
).encode()


def test_period_column_dated_by_the_datasets_own_columns(user_client: CsrfClient):
    dataset_id = upload(user_client, "evre", DATED_CSV, "evre.csv").json()["id"]
    process_one_dataset()
    columns = {
        c["name"]: c
        for c in user_client.get(f"/api/datasets/{dataset_id}").json()["profile"]["columns"]
    }
    assert columns["Birim"]["type"] == "string"  # site phases: nothing to detect

    link = {"Birim": {"start": "Başlangıç", "end": "Bitiş"}}
    assert (
        patch(user_client, dataset_id, {"period_dates": {"Birim": {"start": "Alan"}}}).status_code
        == 400
    )
    assert (
        patch(
            user_client, dataset_id, {"period_dates": {"Uzunluk": {"start": "Bitiş"}}}
        ).status_code
        == 400
    )
    response = patch(user_client, dataset_id, {"period_dates": link})
    assert response.status_code == 200 and response.json()["status"] == "pending"
    process_one_dataset()

    detail = user_client.get(f"/api/datasets/{dataset_id}").json()
    column = next(c for c in detail["profile"]["columns"] if c["name"] == "Birim")
    assert column["type"] == "period"
    assert column["dated_by"] == {"start": "Başlangıç", "end": "Bitiş", "bc": False}
    # Helenistik has no dates in its rows, so PeriodO places it; Yüzey is undated.
    assert column["order"] == ["Saray", "Evre 7", "Helenistik", "Roma", "Yüzey"]
    by_value = {m["value"]: m for m in column["matches"]}
    assert (by_value["Saray"]["start"], by_value["Saray"]["stop"]) == (-1900, -1370)
    assert by_value["Saray"]["via"] == "data" and "varies" not in by_value["Saray"]
    # Two rows, two sets of dates: the widest span, and it says so.
    assert (by_value["Evre 7"]["start"], by_value["Evre 7"]["stop"]) == (-720, -640)
    assert by_value["Evre 7"]["varies"] is True
    assert by_value["Roma"]["via"] == "data"  # the data's own dates come before PeriodO's
    assert by_value["Helenistik"]["via"] == "translation"

    # Years counted backwards (700 = 700 BC), and a meaning still overrules the data.
    patch(
        user_client,
        dataset_id,
        {
            "period_dates": {"Birim": {"start": "Uzunluk", "bc": True}},
            "period_mappings": {"Birim": {"Saray": "9000 BC"}},
        },
    )
    process_one_dataset()
    column = next(
        c
        for c in user_client.get(f"/api/datasets/{dataset_id}").json()["profile"]["columns"]
        if c["name"] == "Birim"
    )
    by_value = {m["value"]: m for m in column["matches"]}
    assert by_value["Saray"]["via"] == "user" and by_value["Saray"]["start"] == -9000
    assert (by_value["Evre 7"]["start"], by_value["Evre 7"]["stop"]) == (-5, -3)

    # Removing the link returns the column to what it was.
    patch(
        user_client,
        dataset_id,
        {"period_dates": {"Birim": None}, "period_mappings": {"Birim": {"Saray": None}}},
    )
    process_one_dataset()
    detail = user_client.get(f"/api/datasets/{dataset_id}").json()
    column = next(c for c in detail["profile"]["columns"] if c["name"] == "Birim")
    assert column["type"] == "string" and "dated_by" not in column
