import pytest

from generation.provider import ProviderError, chat_completion, list_models, normalise_base_url
from tests.stub_provider import start

MESSAGES = [{"role": "user", "content": "hi"}]


@pytest.fixture(scope="module")
def stub():
    server = start()
    yield server
    server.shutdown()


@pytest.fixture(autouse=True)
def allow_local(settings):
    settings.ALLOW_PRIVATE_ENDPOINTS = True


def call(stub, key, **kw):
    return chat_completion(
        base_url=stub.base_url, api_key=key, model="m", messages=MESSAGES, timeout=1, **kw
    )


def test_happy_path_sends_bearer_and_returns_text(stub):
    result = call(stub, "good-key", json_object=True, seed=7, max_tokens=50)
    assert '"mark": "bar"' in result.text
    assert result.model == "m"
    assert result.usage["total_tokens"] == 19
    sent = stub.requests[-1]
    assert sent["headers"]["Authorization"] == "Bearer good-key"
    assert sent["body"]["response_format"] == {"type": "json_object"}
    assert sent["body"]["seed"] == 7 and sent["body"]["max_tokens"] == 50


def test_401_becomes_actionable_message(stub):
    with pytest.raises(ProviderError, match="check your API key"):
        call(stub, "bad-key")


def test_timeout(stub):
    with pytest.raises(ProviderError, match="did not answer in time"):
        call(stub, "slow-key")


def test_non_json_body(stub):
    with pytest.raises(ProviderError, match="not in the chat completions format"):
        call(stub, "garbage-key")


def test_wrong_path_is_404(stub):
    with pytest.raises(ProviderError, match="404"):
        chat_completion(
            base_url=stub.base_url + "/nope", api_key="good-key", model="m", messages=MESSAGES
        )


def test_connection_refused():
    with pytest.raises(ProviderError, match="Could not connect"):
        chat_completion(
            base_url="http://127.0.0.1:9", api_key="k", model="m", messages=MESSAGES, timeout=1
        )


def test_normalise_base_url(settings):
    assert normalise_base_url(" https://api.example.com/v1/ ") == "https://api.example.com/v1"
    with pytest.raises(ProviderError, match="http"):
        normalise_base_url("ftp://x")
    settings.ALLOW_PRIVATE_ENDPOINTS = False
    with pytest.raises(ProviderError, match="https"):
        normalise_base_url("http://api.example.com/v1")


def test_private_hosts_refused_by_default(settings, stub):
    settings.ALLOW_PRIVATE_ENDPOINTS = False
    with pytest.raises(ProviderError, match="https"):
        call(stub, "good-key")


def test_list_models_sorted_case_insensitively(stub):
    assert list_models(base_url=stub.base_url, api_key="good-key") == [
        "Stub-Embed",
        "stub-large",
        "stub-small",
    ]


def test_list_models_bad_key(stub):
    with pytest.raises(ProviderError, match="check your API key"):
        list_models(base_url=stub.base_url, api_key="bad-key")
