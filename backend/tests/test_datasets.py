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
