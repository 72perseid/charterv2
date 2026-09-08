from django.http import HttpRequest
from ninja import Router

from datasets.models import Dataset
from datasets.schemas import DatasetOut

router = Router(tags=["datasets"])


@router.get("", response=list[DatasetOut])
def list_datasets(request: HttpRequest):
    return Dataset.objects.filter(user=request.user)
