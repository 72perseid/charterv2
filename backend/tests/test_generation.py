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


def test_show_and_filter_are_checked_stored_and_applied(ready, stub):
    client, dataset_id = ready
    bad = [
        ({"show": "histogram"}, "show must be one of"),
        ({"filter_field": "Alan"}, "both a column and a value"),
        ({"filter_field": "Yok", "filter_value": "x"}, "is not a column"),
        ({"filter_field": "Tarih", "filter_value": "2019"}, "is a date column"),
        ({"filter_field": "Sayı", "filter_value": "çok"}, "holds numbers"),
        ({"filter_field": "Alan", "filter_value": "Açma Z"}, "No row has Alan = Açma Z"),
    ]
    for fields, message in bad:
        response = create_chart(client, dataset_id, **fields)
        assert response.status_code == 400 and message in response.json()["detail"], fields

    chosen = {"show": "average", "filter_field": "Alan", "filter_value": " Açma A "}
    response = create_chart(client, dataset_id, **chosen)
    assert response.status_code == 201, response.content
    revision_id = response.json()["revisions"][0]["id"]
    process_one_revision()

    revision = client.get(f"/api/revisions/{revision_id}").json()
    assert revision["status"] == "done", revision["error_message"]
    assert (revision["show"], revision["filter_value"]) == ("average", "Açma A")
    # The stub answers with a sum and no filter; the choices win and are recorded.
    assert revision["spec"]["encoding"]["y"]["aggregate"] == "mean"
    assert revision["spec"]["transform"] == [{"filter": {"field": "Alan", "equal": "Açma A"}}]
    assert revision["corrections"] == [
        'y: aggregate set to "mean", as chosen (average)',
        'filter set to "Alan" = "Açma A", as chosen',
    ]
    message = revision["request"]["messages"][1]["content"]
    assert 'show: average: "aggregate": "mean" inside the y channel' in message
    assert 'only rows where: Alan = "Açma A"' in message

    # A number column is filtered with a number, not with its text.
    numeric = create_chart(client, dataset_id, filter_field="Sayı", filter_value="3")
    process_one_revision()
    spec = client.get(f"/api/revisions/{numeric.json()['revisions'][0]['id']}").json()["spec"]
    assert spec["transform"] == [{"filter": {"field": "Sayı", "equal": 3}}]


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
    assert revision["prompt_version"] == "p2026-11-b"
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
    assert revision["prompt_version"] == "p2026-11-b" and revision["duration_ms"] is not None


def test_charts_are_listed_with_the_one_worked_on_last_first(ready, stub):
    client, dataset_id = ready
    set_key(client, stub, "sk-order")
    first = create_chart(client, dataset_id, title="first").json()
    second = create_chart(client, dataset_id, title="second").json()
    titles = [c["title"] for c in client.get("/api/charts").json()]
    assert titles == ["second", "first"]

    # A new revision of the older chart brings it back to the top.
    response = client.post(
        f"/api/charts/{first['id']}/revisions",
        json.dumps(
            {
                "parent_id": first["current_revision_id"] or first["revisions"][0]["id"],
                "x_field": "Alan",
                "y_field": "Sayı",
                "color_field": None,
                "prompt": "yatay yap",
            }
        ),
        content_type="application/json",
    )
    assert response.status_code == 201, response.content
    titles = [c["title"] for c in client.get("/api/charts").json()]
    assert titles == ["first", "second"]
    assert second["id"] != first["id"]


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


def test_export_bundle_holds_the_whole_record(ready, stub):
    client, dataset_id = ready
    set_key(client, stub, "good-key", input_price_per_million=1.0, output_price_per_million=2.0)
    chart = create_chart(client, dataset_id).json()
    process_one_revision()
    first_id = chart["revisions"][0]["id"]
    client.post(
        f"/api/charts/{chart['id']}/revisions",
        json.dumps(
            {"parent_id": first_id, "x_field": "Alan", "y_field": "Sayı", "prompt": "çizgi"}
        ),
        content_type="application/json",
    )
    process_one_revision()

    response = client.get(f"/api/charts/{chart['id']}/export")
    assert response.status_code == 200
    assert (
        response["Content-Disposition"]
        == f'attachment; filename="charter-chart-{chart["id"]}.json"'
    )
    bundle = json.loads(response.content)  # re-read exactly as a stranger would
    assert bundle["format"] == "charter-bundle/1"
    assert bundle["chart"]["title"] == "Alanlara göre"
    assert bundle["dataset"]["parse_options"]["encoding"] == "cp1254"
    assert {c["name"] for c in bundle["dataset"]["profile"]["columns"]} >= {"Alan", "Sayı"}
    assert [r["revision_no"] for r in bundle["revisions"]] == [1, 2]
    second = bundle["revisions"][1]
    assert second["parent_id"] == first_id
    assert second["spec"]["mark"] == "bar"
    assert second["request"]["messages"][0]["role"] == "system"
    assert "Previous specification" in second["request"]["messages"][1]["content"]
    assert second["response_text"].startswith("{")
    assert second["cost_usd"] == pytest.approx(12 * 1e-6 + 7 * 2e-6)
    assert second["prompt_version"] == "p2026-11-b"

    other = CsrfClient(enforce_csrf_checks=True)
    other.get("/api/auth/csrf")
    other.post(
        "/api/auth/register",
        {"email": "other@example.org", "password": "correct-horse-9"},
        content_type="application/json",
    )
    assert other.get(f"/api/charts/{chart['id']}/export").status_code == 404


def test_period_column_is_charted_oldest_first(user_client: CsrfClient, stub):
    from django.core.files.uploadedfile import SimpleUploadedFile

    content = "Alan;Sayı\nRoma;4\nHelenistik;2\nDemir Çağı;7\nRoma;1\n".encode()
    dataset_id = user_client.post(
        "/api/datasets", {"name": "Dönemler", "file": SimpleUploadedFile("donem.csv", content)}
    ).json()["id"]
    process_one_dataset()
    set_key(user_client, stub, "good-key")

    revision_id = create_chart(user_client, dataset_id).json()["revisions"][0]["id"]
    process_one_revision()
    revision = user_client.get(f"/api/revisions/{revision_id}").json()
    assert revision["status"] == "done", revision["error_message"]
    # The stub answered with a plain nominal x; the order comes from the profile.
    assert revision["spec"]["encoding"]["x"] == {
        "field": "Alan",
        "type": "ordinal",
        "sort": ["Demir Çağı", "Helenistik", "Roma"],
    }
    assert revision["corrections"] == ['x: "Alan" put in chronological order, oldest first']
    sent = revision["request"]["messages"][1]["content"]
    assert '"type": "period"' in sent and '"order"' not in sent


ASK_CSV = (
    "Buluntu;Dönem\nK1;Roma\nK2;Helenistik\nK3;Erken Hristiyanlık\nK4;Evre 7\nK5;Açma B\nK6;Roma\n"
).encode()


def ask(client, dataset_id, column="Dönem"):
    return client.post(
        f"/api/datasets/{dataset_id}/periods/ask",
        json.dumps({"column": column}),
        content_type="application/json",
    )


def period_dataset(client):
    from django.core.files.uploadedfile import SimpleUploadedFile

    dataset_id = client.post(
        "/api/datasets", {"name": "Dönemler", "file": SimpleUploadedFile("d.csv", ASK_CSV)}
    ).json()["id"]
    process_one_dataset()
    # Two readable labels in five is too few to detect; the user says it is a period column.
    client.patch(
        f"/api/datasets/{dataset_id}",
        json.dumps({"periods": {"Dönem": True}}),
        content_type="application/json",
    )
    process_one_dataset()
    return dataset_id


def period_column(client, dataset_id):
    detail = client.get(f"/api/datasets/{dataset_id}").json()
    return detail, next(c for c in detail["profile"]["columns"] if c["name"] == "Dönem")


def test_model_is_asked_about_unplaced_periods_only_on_request(user_client: CsrfClient, stub):
    dataset_id = period_dataset(user_client)
    _, column = period_column(user_client, dataset_id)
    assert column["type"] == "period"
    assert column["unplaced"] == ["Açma B", "Erken Hristiyanlık", "Evre 7"]
    assert not any(
        "period labels" in json.dumps(r["body"]) for r in stub.requests
    )  # nothing sent yet

    assert ask(user_client, dataset_id).status_code == 400  # no model configured
    set_key(user_client, stub, "good-key")
    assert ask(user_client, dataset_id, "Buluntu").status_code == 400  # not a period column
    response = ask(user_client, dataset_id)
    assert response.status_code == 200 and response.json()["status"] == "pending"
    process_one_dataset()

    detail, column = period_column(user_client, dataset_id)
    assert detail["status"] == "done"
    assert column["order"] == ["Evre 7", "Helenistik", "Roma", "Erken Hristiyanlık", "Açma B"]
    assert column["unplaced"] == ["Açma B"]
    via = {m["value"]: m["via"] for m in column["matches"]}
    assert via == {
        "Evre 7": "model",
        "Helenistik": "translation",
        "Roma": "translation",  # the stub also "answered" Roma; it was never asked, so ignored
        "Erken Hristiyanlık": "model",
    }
    # The record: what was sent, what came back.
    record = detail["parse_options"]["period_requests"]["Dönem"]
    assert record["labels"] == ["Açma B", "Erken Hristiyanlık", "Evre 7"]
    assert record["answered"] == ["Erken Hristiyanlık", "Evre 7"]
    assert (
        record["prompt_version"] == "periods-2026-11-a" and record["endpoint_host"] == "127.0.0.1"
    )
    assert "Evre 7" in record["messages"][1]["content"] and record["response_text"].startswith("{")
    assert "period_questions" not in detail["parse_options"]["overrides"]

    # Answers survive a later re-read without another call.
    calls = len(stub.requests)
    user_client.patch(
        f"/api/datasets/{dataset_id}",
        json.dumps({"header_row": 0}),
        content_type="application/json",
    )
    user_client.patch(
        f"/api/datasets/{dataset_id}",
        json.dumps({"periods": {"Buluntu": False}}),
        content_type="application/json",
    )
    process_one_dataset()
    _, column = period_column(user_client, dataset_id)
    assert column["unplaced"] == ["Açma B"] and len(stub.requests) == calls


def test_a_failed_period_question_leaves_the_dataset_usable(user_client: CsrfClient, stub):
    dataset_id = period_dataset(user_client)
    set_key(user_client, stub, "text-key")  # the stub answers in prose
    ask(user_client, dataset_id)
    process_one_dataset()
    detail, column = period_column(user_client, dataset_id)
    assert detail["status"] == "done"
    assert column["unplaced"] == ["Açma B", "Erken Hristiyanlık", "Evre 7"]
    assert "not JSON" in detail["parse_options"]["period_requests"]["Dönem"]["error"]
