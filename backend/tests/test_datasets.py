import pytest
from django.test import Client

from accounts.models import User
from datasets.models import Dataset

pytestmark = pytest.mark.django_db


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
