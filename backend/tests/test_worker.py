import threading

import pytest
from django.db import connection

from accounts.models import User
from datasets.models import Dataset
from datasets.tasks import claim_dataset

pytestmark = pytest.mark.django_db(transaction=True)


def test_two_workers_never_claim_the_same_dataset():
    user = User.objects.create_user(email="w@example.org", password="correct-horse-9")
    for i in range(6):
        Dataset.objects.create(
            user=user, name=f"d{i}", original_filename="x.csv", original_path="/x"
        )

    claimed: list[int] = []
    lock = threading.Lock()

    def worker():
        try:
            while True:
                dataset = claim_dataset()
                if dataset is None:
                    break
                with lock:
                    claimed.append(dataset.pk)
        finally:
            connection.close()

    threads = [threading.Thread(target=worker) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert sorted(claimed) == sorted(Dataset.objects.values_list("pk", flat=True))
    assert len(claimed) == len(set(claimed))
    assert not Dataset.objects.filter(status="pending").exists()
