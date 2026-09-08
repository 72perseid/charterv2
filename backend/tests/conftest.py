import pytest
from django.test import Client


class CsrfClient(Client):
    """Test client that behaves like the browser: every request carries the
    current csrftoken cookie as the X-CSRFToken header. Django rotates the
    token on login, so the header must be read per request, not once."""

    def request(self, **environ):
        token = self.cookies.get("csrftoken")
        if token is not None:
            environ.setdefault("HTTP_X_CSRFTOKEN", token.value)
        return super().request(**environ)


@pytest.fixture
def client() -> Client:
    # enforce_csrf_checks=True so tests exercise the same path the browser does.
    return Client(enforce_csrf_checks=True)


@pytest.fixture
def csrf_client() -> CsrfClient:
    """A client that has fetched the CSRF cookie and sends it with every request."""
    client = CsrfClient(enforce_csrf_checks=True)
    client.get("/api/auth/csrf")
    return client


def register(client: Client, email: str = "ada@example.org", password: str = "correct-horse-9"):
    return client.post(
        "/api/auth/register",
        {"email": email, "password": password, "display_name": "Ada"},
        content_type="application/json",
    )


@pytest.fixture
def user_client(csrf_client: CsrfClient) -> CsrfClient:
    response = register(csrf_client)
    assert response.status_code == 201, response.content
    return csrf_client
