import pytest
from django.test import Client

from accounts.models import User
from tests.conftest import register

pytestmark = pytest.mark.django_db


def test_register_creates_user_and_logs_in(csrf_client: Client):
    response = register(csrf_client)
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "ada@example.org"
    assert body["display_name"] == "Ada"
    assert User.objects.get(email="ada@example.org").check_password("correct-horse-9")
    assert csrf_client.get("/api/auth/me").status_code == 200


def test_register_rejects_duplicate_email(csrf_client: Client):
    assert register(csrf_client).status_code == 201
    csrf_client.post("/api/auth/logout")
    response = register(csrf_client)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_register_rejects_weak_password(csrf_client: Client):
    response = register(csrf_client, password="password")
    assert response.status_code == 400


def test_post_without_csrf_header_is_rejected(client: Client):
    response = register(client)
    assert response.status_code == 403


def test_login_logout_cycle(csrf_client: Client):
    register(csrf_client)
    csrf_client.post("/api/auth/logout")
    assert csrf_client.get("/api/auth/me").status_code == 401

    bad = csrf_client.post(
        "/api/auth/login",
        {"email": "ada@example.org", "password": "wrong"},
        content_type="application/json",
    )
    assert bad.status_code == 401

    good = csrf_client.post(
        "/api/auth/login",
        {"email": "ada@example.org", "password": "correct-horse-9"},
        content_type="application/json",
    )
    assert good.status_code == 200
    assert csrf_client.get("/api/auth/me").json()["email"] == "ada@example.org"


def test_me_requires_session(client: Client):
    assert client.get("/api/auth/me").status_code == 401
