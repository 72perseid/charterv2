import json
import threading

import pytest
from django.db import connection

from accounts.models import User
from charts.models import Chart, ChartRevision
from datasets.tasks import process_one_dataset
from generation.tasks import claim_revision, process_one_revision
from tests.conftest import CsrfClient
from tests.fixtures import turkish_csv_bytes
from tests.stub_provider import start

pytestmark = pytest.mark.django_db


@pytest.fixture(scope="module")
def stub():
    server = start()
    yield server
    server.shutdown()


@pytest.fixture(autouse=True)
def env(settings, tmp_path):
    settings.ALLOW_PRIVATE_ENDPOINTS = True
    settings.DATA_DIR = tmp_path / "data"


@pytest.fixture
def ready(user_client: CsrfClient, stub):
    """A parsed Turkish dataset and a model config pointing at the stub."""
    from django.core.files.uploadedfile import SimpleUploadedFile

    dataset_id = user_client.post(
        "/api/datasets",
        {"name": "Kinet", "file": SimpleUploadedFile("kinet.csv", turkish_csv_bytes())},
    ).json()["id"]
    process_one_dataset()
    user_client.put(
        "/api/me/model-config",
        json.dumps({"base_url": stub.base_url, "model": "stub", "api_key": "good-key"}),
        content_type="application/json",
    )
    return user_client, dataset_id


def create_chart(client, dataset_id, **overrides):
    body = {
        "dataset_id": dataset_id,
        "title": "Alanlara göre",
        "x_field": "Alan",
        "y_field": "Sayı",
        "color_field": None,
        "prompt": "Alanlara göre toplam buluntu sayısı",
    }
    body.update(overrides)
    return client.post("/api/charts", json.dumps(body), content_type="application/json")


def set_key(client, stub, key, **extra):
    client.put(
        "/api/me/model-config",
        json.dumps({"base_url": stub.base_url, "model": "stub", "api_key": key, **extra}),
        content_type="application/json",
    )


def test_chart_needs_model_config(user_client: CsrfClient):
    response = create_chart(user_client, 1)
    assert response.status_code == 400
    assert "Configure a model" in response.json()["detail"]


def test_create_chart_makes_revision_1_and_worker_finishes_it(ready, stub):
    client, dataset_id = ready
    response = create_chart(client, dataset_id)
    assert response.status_code == 201, response.content
    chart = response.json()
    assert chart["revision_count"] == 1 and chart["current_revision_id"] is None
    revision_id = chart["revisions"][0]["id"]
    assert chart["revisions"][0]["status"] == "pending"

    assert process_one_revision() is True
    assert process_one_revision() is False

    revision = client.get(f"/api/revisions/{revision_id}").json()
    assert revision["status"] == "done", revision["error_message"]
    assert revision["spec"]["mark"] == "bar"
    assert revision["spec"]["data"] == {"name": "main"}
    assert revision["spec"]["encoding"]["x"]["field"] == "Alan"
    # The reproducibility record.
    assert revision["request"]["attempt"] == 1
    assert revision["request"]["messages"][0]["role"] == "system"
    assert "Alanlara göre toplam" in revision["request"]["messages"][1]["content"]
    assert '"row_count": 6' in revision["request"]["messages"][1]["content"]
    assert revision["request"]["parameters"]["response_format"] == {"type": "json_object"}
    assert revision["request"]["parameters"]["seed"] == 1
    assert revision["response_text"].startswith("{")
    assert revision["model"] == "stub" and revision["endpoint_host"] == "127.0.0.1"
    assert revision["prompt_version"] == "p2026-09-a"
    assert revision["usage"]["total_tokens"] == 19
    assert revision["usage"]["reasoning_tokens"] == 3
    assert revision["cost_usd"] is None  # no prices entered
    assert revision["cost_at_current_prices"] is None

    # Entering prices later gives old revisions an estimate at today's prices, unstored.
    set_key(client, stub, "good-key", input_price_per_million=1.0, output_price_per_million=2.0)
    revision = client.get(f"/api/revisions/{revision_id}").json()
    assert revision["cost_usd"] is None
    assert revision["cost_at_current_prices"] == pytest.approx(12 * 1e-6 + 7 * 2e-6)
    assert revision["duration_ms"] is not None and revision["duration_ms"] >= 0

    chart = client.get(f"/api/charts/{chart['id']}").json()
    assert chart["current_revision_id"] == revision_id
    assert chart["current_status"] == "done"


def test_statistics_level_sends_no_rows_but_sample_level_does(ready, stub):
    client, dataset_id = ready
    create_chart(client, dataset_id)
    process_one_revision()
    sent = stub.requests[-1]["body"]["messages"][1]["content"]
    assert "sample_rows" not in sent
    assert "KH-001" not in sent  # identifier values are never sent
    assert "Açma A" in sent  # a repeated category is, as a top value

    client.patch(
        f"/api/datasets/{dataset_id}",
        json.dumps({"privacy_level": "sample"}),
        content_type="application/json",
    )
    create_chart(client, dataset_id)
    process_one_revision()
    sent = stub.requests[-1]["body"]["messages"][1]["content"]
    assert "sample_rows" in sent and "KH-001" in sent


def test_prose_answer_is_retried_then_failed_with_record(ready, stub):
    client, dataset_id = ready
    set_key(client, stub, "text-key")
    revision_id = create_chart(client, dataset_id).json()["revisions"][0]["id"]
    before = len(stub.requests)
    process_one_revision()
    assert len(stub.requests) - before == 2  # the retry with the error appended
    retry_messages = stub.requests[-1]["body"]["messages"]
    assert retry_messages[-1]["content"].startswith("Your previous answer was rejected")

    revision = client.get(f"/api/revisions/{revision_id}").json()
    assert revision["status"] == "failed"
    assert revision["attempts"] == 1
    assert "not JSON" in revision["error_message"]
    assert revision["response_text"] == "Sure, here is prose."  # kept for the record
    assert revision["request"]["attempt"] == 2
    assert revision["usage"]["prompt_tokens"] == 24  # both attempts are paid for


def test_cost_uses_prices_in_force_at_run_time(ready, stub):
    client, dataset_id = ready
    set_key(client, stub, "good-key", input_price_per_million=1.0, output_price_per_million=2.0)
    revision_id = create_chart(client, dataset_id).json()["revisions"][0]["id"]
    process_one_revision()
    revision = client.get(f"/api/revisions/{revision_id}").json()
    assert revision["cost_usd"] == pytest.approx(12 * 1e-6 + 7 * 2e-6)
    assert revision["request"]["pricing"] == {"input_per_million": 1.0, "output_per_million": 2.0}

    # Changing the prices later does not rewrite the stored cost.
    set_key(client, stub, "good-key", input_price_per_million=100.0, output_price_per_million=100.0)
    assert client.get(f"/api/revisions/{revision_id}").json()["cost_usd"] == revision["cost_usd"]


def test_provider_401_fails_with_actionable_message(ready, stub):
    client, dataset_id = ready
    set_key(client, stub, "bad-key")
    revision_id = create_chart(client, dataset_id).json()["revisions"][0]["id"]
    process_one_revision()
    revision = client.get(f"/api/revisions/{revision_id}").json()
    assert revision["status"] == "failed"
    assert "check your API key" in revision["error_message"]
    # The record is kept even when the endpoint never answered usefully.
    assert revision["model"] == "stub" and revision["endpoint_host"] == "127.0.0.1"
    assert revision["prompt_version"] == "p2026-09-a" and revision["duration_ms"] is not None


def test_second_revision_gets_parent_spec_in_prompt(ready, stub):
    client, dataset_id = ready
    chart = create_chart(client, dataset_id).json()
    process_one_revision()
    first_id = chart["revisions"][0]["id"]
    response = client.post(
        f"/api/charts/{chart['id']}/revisions",
        json.dumps(
            {
                "parent_id": first_id,
                "x_field": "Alan",
                "y_field": "Sayı",
                "color_field": "Korunmuş",
                "prompt": "renklendir",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 201, response.content
    assert response.json()["revision_no"] == 2 and response.json()["parent_id"] == first_id
    process_one_revision()
    sent = stub.requests[-1]["body"]["messages"][1]["content"]
    assert "Previous request: Alanlara göre toplam" in sent
    assert '"mark": "bar"' in sent
    detail = client.get(f"/api/charts/{chart['id']}").json()
    assert detail["current_revision_id"] == response.json()["id"]
    assert detail["revision_count"] == 2


def test_field_and_ownership_checks(ready):
    client, dataset_id = ready
    bad = create_chart(client, dataset_id, x_field="Bölge")
    assert bad.status_code == 400 and "not a column" in bad.json()["detail"]

    chart_id = create_chart(client, dataset_id).json()["id"]
    other = CsrfClient(enforce_csrf_checks=True)
    other.get("/api/auth/csrf")
    other.post(
        "/api/auth/register",
        {"email": "other@example.org", "password": "correct-horse-9"},
        content_type="application/json",
    )
    assert other.get(f"/api/charts/{chart_id}").status_code == 404
    revision_id = Chart.objects.get(pk=chart_id).revisions.first().pk
    assert other.get(f"/api/revisions/{revision_id}").status_code == 404
    assert other.get("/api/charts").json() == []


def test_patch_current_revision_and_delete(ready):
    client, dataset_id = ready
    chart = create_chart(client, dataset_id).json()
    revision_id = chart["revisions"][0]["id"]
    not_done = client.patch(
        f"/api/charts/{chart['id']}",
        json.dumps({"current_revision_id": revision_id}),
        content_type="application/json",
    )
    assert not_done.status_code == 400
    process_one_revision()
    ok = client.patch(
        f"/api/charts/{chart['id']}",
        json.dumps({"title": "Yeni başlık", "current_revision_id": revision_id}),
        content_type="application/json",
    )
    assert ok.status_code == 200 and ok.json()["title"] == "Yeni başlık"
    assert client.delete(f"/api/charts/{chart['id']}").status_code == 204
    assert not ChartRevision.objects.filter(pk=revision_id).exists()


def test_rate_limit(ready, settings):
    client, dataset_id = ready
    settings.RATE_REVISIONS_PER_HOUR = 1
    assert create_chart(client, dataset_id).status_code == 201
    assert create_chart(client, dataset_id).status_code == 429


@pytest.mark.django_db(transaction=True)
def test_two_workers_never_claim_the_same_revision():
    user = User.objects.create_user(email="w@example.org", password="correct-horse-9")
    from datasets.models import Dataset

    dataset = Dataset.objects.create(
        user=user, name="d", original_filename="x.csv", original_path="/x"
    )
    chart = Chart.objects.create(user=user, dataset=dataset, title="t")
    for i in range(6):
        ChartRevision.objects.create(
            chart=chart, user=user, revision_no=i + 1, x_field="a", y_field="b", prompt="p"
        )
    claimed: list[int] = []
    lock = threading.Lock()

    def worker():
        try:
            while (revision := claim_revision()) is not None:
                with lock:
                    claimed.append(revision.pk)
        finally:
            connection.close()

    threads = [threading.Thread(target=worker) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(claimed) == 6 and len(set(claimed)) == 6
    assert ChartRevision.objects.filter(attempts=1).count() == 6
