import json

import pytest

from accounts.crypto import decrypt, encrypt
from accounts.models import ModelConfig
from tests.conftest import CsrfClient
from tests.stub_provider import start

pytestmark = pytest.mark.django_db


@pytest.fixture(scope="module")
def stub():
    server = start()
    yield server
    server.shutdown()


@pytest.fixture(autouse=True)
def allow_local(settings):
    settings.ALLOW_PRIVATE_ENDPOINTS = True


def put(client, **fields):
    return client.put("/api/me/model-config", json.dumps(fields), content_type="application/json")


def test_crypto_roundtrip():
    token = encrypt("sk-secret")
    assert token != b"sk-secret"
    assert decrypt(token) == "sk-secret"


def test_requires_auth(client):
    assert client.get("/api/me/model-config").status_code == 401


def test_empty_config(user_client: CsrfClient):
    body = user_client.get("/api/me/model-config").json()
    assert body == {
        "base_url": "",
        "model": "",
        "temperature": 0.0,
        "has_key": False,
        "key_hint": "",
        "input_price_per_million": None,
        "output_price_per_million": None,
        "updated_at": None,
    }


def test_save_encrypts_key_and_never_returns_it(user_client: CsrfClient, stub):
    response = put(
        user_client,
        base_url=stub.base_url + "/",
        model="m",
        api_key="sk-abcdef123456",
        temperature=0.2,
    )
    assert response.status_code == 200, response.content
    body = response.json()
    assert body["base_url"] == stub.base_url  # trailing slash stripped
    assert body["has_key"] is True and body["key_hint"] == "…3456"
    assert "sk-abcdef" not in response.content.decode()

    stored = ModelConfig.objects.get()
    assert bytes(stored.api_key_encrypted) != b"sk-abcdef123456"
    assert decrypt(stored.api_key_encrypted) == "sk-abcdef123456"

    # Blank key on a later save keeps the stored one.
    again = put(user_client, base_url=stub.base_url, model="m2", api_key="", temperature=0)
    assert again.json()["model"] == "m2" and again.json()["key_hint"] == "…3456"


def test_first_save_needs_a_key(user_client: CsrfClient, stub):
    response = put(user_client, base_url=stub.base_url, model="m", api_key="")
    assert response.status_code == 400
    assert "API key is required" in response.json()["detail"]


def test_bad_url_rejected(user_client: CsrfClient):
    assert put(user_client, base_url="not a url", model="m", api_key="k").status_code == 400


def test_connection_test_reports_outcome(user_client: CsrfClient, stub):
    assert user_client.post("/api/me/model-config/test").status_code == 400  # nothing saved

    put(user_client, base_url=stub.base_url, model="stub-model", api_key="good-key")
    body = user_client.post("/api/me/model-config/test").json()
    assert body["ok"] is True
    assert body["model"] == "stub-model"
    assert "ok" in body["message"]
    assert body["duration_ms"] >= 0

    put(user_client, base_url=stub.base_url, model="stub-model", api_key="bad-key")
    body = user_client.post("/api/me/model-config/test").json()
    assert body["ok"] is False
    assert "check your API key" in body["message"]


def test_list_models_endpoint(user_client: CsrfClient, stub):
    def ask(**fields):
        return user_client.post(
            "/api/me/model-config/models", json.dumps(fields), content_type="application/json"
        )

    assert ask(base_url=stub.base_url).status_code == 400  # no key anywhere yet
    ok = ask(base_url=stub.base_url, api_key="good-key")
    assert ok.status_code == 200
    assert ok.json()["models"] == ["Stub-Embed", "stub-large", "stub-small"]
    assert ok.json()["pricing"]["stub-large"] == {
        "input_per_million": 1.0,
        "output_per_million": 2.0,
    }

    put(user_client, base_url=stub.base_url, model="stub-small", api_key="good-key")
    stored = ask(base_url=stub.base_url)  # blank key -> stored key
    assert stored.status_code == 200 and len(stored.json()["models"]) == 3

    bad = ask(base_url=stub.base_url, api_key="bad-key")
    assert bad.status_code == 400 and "check your API key" in bad.json()["detail"]
