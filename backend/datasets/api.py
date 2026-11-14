from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.db import transaction
from django.http import FileResponse, HttpRequest
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import File, Form, Router, UploadedFile

from accounts.models import ModelConfig
from datasets.chronology import MAX_DISTINCT
from datasets.ingest import IngestError, kind_of
from datasets.models import Dataset
from datasets.profile import rows_as_records
from datasets.schemas import (
    DatasetDetail,
    DatasetOut,
    DatasetPatch,
    Detail,
    PeriodQuestion,
    RowsOut,
)
from datasets.storage import ORIGINAL_STEM, dataset_dir, remove_dataset_dir
from datasets.tasks import load_rows, mark_for_reingest

router = Router(tags=["datasets"])

MAPPING_MAX_LENGTH = 120
ROWS_MAX_LIMIT = 100_000  # the chart page needs every row; SPEC §6.1 caps datasets at this


def own(request: HttpRequest, dataset_id: int) -> Dataset:
    return get_object_or_404(Dataset, pk=dataset_id, user=request.user)


@router.get("", response=list[DatasetOut])
def list_datasets(request: HttpRequest):
    return Dataset.objects.filter(user=request.user)


@router.post("", response={201: DatasetDetail, 400: Detail, 413: Detail, 429: Detail})
def upload_dataset(request: HttpRequest, file: File[UploadedFile], name: Form[str] = ""):
    since = timezone.now() - timedelta(hours=1)
    recent = Dataset.objects.filter(user=request.user, created_at__gte=since).count()
    if recent >= settings.RATE_UPLOADS_PER_HOUR:
        return 429, {"detail": "Upload limit reached. Try again in an hour."}

    filename = Path(file.name or "upload").name
    try:
        kind_of(filename)
    except IngestError as exc:
        return 400, {"detail": str(exc)}
    if file.size > settings.UPLOAD_MAX_BYTES:
        limit_mb = settings.UPLOAD_MAX_BYTES // (1024 * 1024)
        return 413, {"detail": f"The file is larger than {limit_mb} MB."}

    extension = Path(filename).suffix.lower()
    with transaction.atomic():
        dataset = Dataset.objects.create(
            user=request.user,
            name=(name or Path(filename).stem).strip()[:200],
            original_filename=filename,
            original_path="",
            size_bytes=file.size,
        )
        directory = dataset_dir(request.user.id, dataset.pk)
        directory.mkdir(parents=True, exist_ok=True)
        original = directory / f"{ORIGINAL_STEM}{extension}"
        with original.open("wb") as out:
            for chunk in file.chunks():
                out.write(chunk)
        dataset.original_path = str(original)
        dataset.save(update_fields=["original_path"])
    return 201, dataset


@router.get("/{dataset_id}", response=DatasetDetail)
def get_dataset(request: HttpRequest, dataset_id: int):
    return own(request, dataset_id)


@router.patch("/{dataset_id}", response={200: DatasetDetail, 400: Detail})
def patch_dataset(request: HttpRequest, dataset_id: int, data: DatasetPatch):
    dataset = own(request, dataset_id)
    fields = []
    if data.name is not None:
        dataset.name = data.name.strip()
        fields.append("name")
    if data.privacy_level is not None:
        if data.privacy_level not in Dataset.Privacy.values:
            return 400, {"detail": "privacy_level must be minimal, statistics, or sample."}
        dataset.privacy_level = data.privacy_level
        fields.append("privacy_level")
    if fields:
        dataset.save(update_fields=fields)

    overrides = dict(dataset.parse_options.get("overrides", {}))
    changed = False
    if data.sheet is not None and data.sheet != overrides.get("sheet"):
        overrides["sheet"] = data.sheet
        changed = True
    if data.header_row is not None and data.header_row != overrides.get("header_row"):
        overrides["header_row"] = data.header_row
        changed = True
    if data.periods:
        columns = {c["name"]: c for c in dataset.profile.get("columns", [])}
        periods = dict(overrides.get("periods", {}))
        for name, choice in data.periods.items():
            column = columns.get(name)
            if column is None:
                return 400, {"detail": f"There is no column named '{name}'."}
            if column["type"] not in {"string", "period"}:
                return 400, {"detail": f"'{name}' is not a text column."}
            if (
                choice is not None
                and choice is not False
                and (column["distinct_count"] > MAX_DISTINCT)
            ):
                return 400, {
                    "detail": f"'{name}' has more than {MAX_DISTINCT} distinct values; "
                    "that is too many to order as periods."
                }
            if choice is None:
                periods.pop(name, None)
            else:
                periods[name] = choice
        if periods != overrides.get("periods", {}):
            overrides["periods"] = periods
            changed = True
    if data.period_dates:
        columns = {c["name"]: c for c in dataset.profile.get("columns", [])}
        dates = dict(overrides.get("period_dates", {}))
        for name, link in data.period_dates.items():
            if link is None:
                dates.pop(name, None)
                continue
            if name not in columns or columns[name]["type"] not in {"string", "period"}:
                return 400, {"detail": f"'{name}' is not a text column."}
            if columns[name]["distinct_count"] > MAX_DISTINCT:
                return 400, {
                    "detail": f"'{name}' has more than {MAX_DISTINCT} distinct values; "
                    "that is too many to order as periods."
                }
            for other in filter(None, (link.start, link.end)):
                if other not in columns or columns[other]["type"] not in {"integer", "number"}:
                    return 400, {"detail": f"'{other}' is not a number column."}
            dates[name] = {"start": link.start, "end": link.end or None, "bc": link.bc}
        if dates != overrides.get("period_dates", {}):
            overrides["period_dates"] = dates
            changed = True
    if data.period_mappings:
        columns = {c["name"]: c for c in dataset.profile.get("columns", [])}
        mappings = {k: dict(v) for k, v in overrides.get("period_mappings", {}).items()}
        for name, wanted in data.period_mappings.items():
            if name not in columns or columns[name]["type"] not in {"string", "period"}:
                return 400, {"detail": f"'{name}' is not a text column."}
            current = mappings.setdefault(name, {})
            for value, meaning in wanted.items():
                if meaning is None or not meaning.strip():
                    current.pop(value, None)
                else:
                    current[value] = meaning.strip()[:MAPPING_MAX_LENGTH]
            if not current:
                mappings.pop(name)
        if mappings != overrides.get("period_mappings", {}):
            overrides["period_mappings"] = mappings
            changed = True
    if changed:
        mark_for_reingest(dataset, overrides)
    return 200, dataset


@router.post("/{dataset_id}/periods/ask", response={200: DatasetDetail, 400: Detail, 409: Detail})
def ask_about_periods(request: HttpRequest, dataset_id: int, data: PeriodQuestion):
    """Send the labels of one period column that nothing here could place to the
    user's model (ADR 0018). The column's distinct values leave the server, so
    this runs only on this explicit request, never as part of an upload."""
    dataset = own(request, dataset_id)
    if dataset.status != Dataset.Status.DONE:
        return 409, {"detail": "The dataset has not been parsed yet."}
    column = next((c for c in dataset.profile.get("columns", []) if c["name"] == data.column), None)
    if column is None or column["type"] != "period":
        return 400, {"detail": f"'{data.column}' is not a period column."}
    if not column.get("unplaced"):
        return 400, {"detail": "Every value in this column is already placed."}
    if not ModelConfig.objects.filter(user=request.user).exists():
        return 400, {"detail": "Configure a model under Settings first."}
    overrides = dict(dataset.parse_options.get("overrides", {}))
    overrides["period_questions"] = [data.column]
    mark_for_reingest(dataset, overrides)
    return 200, dataset


@router.delete("/{dataset_id}", response={204: None})
def delete_dataset(request: HttpRequest, dataset_id: int):
    dataset = own(request, dataset_id)
    user_id = dataset.user_id
    with transaction.atomic():
        dataset.delete()
        remove_dataset_dir(user_id, dataset_id)
    return 204, None


@router.get("/{dataset_id}/rows", response={200: RowsOut, 409: Detail})
def dataset_rows(request: HttpRequest, dataset_id: int, limit: int = 100, offset: int = 0):
    dataset = own(request, dataset_id)
    if dataset.status != Dataset.Status.DONE:
        return 409, {"detail": "The dataset has not been parsed yet."}
    limit = max(1, min(limit, ROWS_MAX_LIMIT))
    offset = max(0, offset)
    frame = load_rows(dataset)
    page = frame.iloc[offset : offset + limit]
    return 200, {
        "total": int(len(frame)),
        "offset": offset,
        "limit": limit,
        "columns": list(frame.columns),
        "rows": rows_as_records(page),
    }


@router.get("/{dataset_id}/download")
def download_dataset(request: HttpRequest, dataset_id: int):
    dataset = own(request, dataset_id)
    return FileResponse(
        open(dataset.original_path, "rb"), as_attachment=True, filename=dataset.original_filename
    )
