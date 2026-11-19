import pytest
from django.test import Client

pytestmark = pytest.mark.django_db


def test_health_is_open_and_names_the_build(client: Client, settings):
    settings.APP_VERSION = "abc1234"
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "abc1234"}
