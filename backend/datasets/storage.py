"""Where a dataset's files live: DATA_DIR/{user_id}/{dataset_id}/ (SPEC §2)."""

import shutil
from pathlib import Path

from django.conf import settings

ORIGINAL_STEM = "original"
PARSED_NAME = "parsed.parquet"


def dataset_dir(user_id, dataset_id: int) -> Path:
    return Path(settings.DATA_DIR) / str(user_id) / str(dataset_id)


def remove_dataset_dir(user_id, dataset_id: int) -> None:
    shutil.rmtree(dataset_dir(user_id, dataset_id), ignore_errors=True)
