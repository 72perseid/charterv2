import json
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from tests.stub_provider import CANNED_SPEC, start


@pytest.fixture(scope="module")
def stub():
    server = start()
    yield server
    server.shutdown()


@pytest.fixture(autouse=True)
def allow_local(settings):
    settings.ALLOW_PRIVATE_ENDPOINTS = True


def bundle(tmp_path, spec):
    data = {
        "format": "charter-bundle/1",
        "dataset": {"profile": {"columns": [{"name": "Alan"}, {"name": "Sayı"}]}},
        "revisions": [
            {
                "revision_no": 1,
                "x_field": "Alan",
                "y_field": "Sayı",
                "color_field": None,
                "model": "stub",
                "endpoint_host": "127.0.0.1",
                "prompt_version": "p2026-09-a",
                "app_version": "abc123",
                "spec": spec,
                "request": {
                    "messages": [{"role": "user", "content": "x"}],
                    "parameters": {
                        "temperature": 0.0,
                        "max_tokens": 100,
                        "seed": 1,
                        "response_format": {"type": "json_object"},
                    },
                },
            }
        ],
    }
    path = tmp_path / "bundle.json"
    path.write_text(json.dumps(data))
    return path


def test_replay_reports_identical(stub, tmp_path):
    path = bundle(tmp_path, CANNED_SPEC)
    out = StringIO()
    call_command(
        "replay",
        str(path),
        base_url=stub.base_url,
        api_key="good-key",
        stdout=out,
        out=tmp_path / "r.json",
    )
    assert "Identical specification." in out.getvalue()
    assert json.loads((tmp_path / "r.json").read_text())["mark"] == "bar"
    sent = stub.requests[-1]["body"]
    assert sent["seed"] == 1 and sent["response_format"] == {"type": "json_object"}


def test_replay_reports_difference(stub, tmp_path):
    changed = dict(CANNED_SPEC, mark="line")
    path = bundle(tmp_path, changed)
    out = StringIO()
    call_command("replay", str(path), base_url=stub.base_url, api_key="good-key", stdout=out)
    assert "differs" in out.getvalue()
    assert "mark: bundle='line'" in out.getvalue()


def test_replay_bad_key_is_a_command_error(stub, tmp_path):
    path = bundle(tmp_path, CANNED_SPEC)
    with pytest.raises(CommandError, match="check your API key"):
        call_command("replay", str(path), base_url=stub.base_url, api_key="bad-key")
