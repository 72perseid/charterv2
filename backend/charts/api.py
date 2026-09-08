from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.db.models import Count, Max, Prefetch
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import Router

from accounts.models import ModelConfig
from charts.export import build_bundle
from charts.models import Chart, ChartRevision
from charts.schemas import (
    ChartDetail,
    ChartIn,
    ChartOut,
    ChartPatch,
    Detail,
    RevisionIn,
    RevisionOut,
)
from datasets.models import Dataset
from generation.tasks import estimate_cost

router = Router(tags=["charts"])
revisions_router = Router(tags=["revisions"])


def chart_queryset(user):
    return (
        Chart.objects.filter(user=user)
        .select_related("dataset", "current_revision")
        .annotate(revision_count=Count("revisions"), updated_at=Max("revisions__created_at"))
        .prefetch_related(
            Prefetch("revisions", queryset=ChartRevision.objects.order_by("revision_no"))
        )
    )


def chart_out(chart: Chart) -> dict:
    current = chart.current_revision
    return {
        "id": chart.pk,
        "dataset_id": chart.dataset_id,
        "dataset_name": chart.dataset.name,
        "title": chart.title,
        "current_revision_id": chart.current_revision_id,
        "current_status": current.status if current else None,
        "revision_count": chart.revision_count,
        "created_at": chart.created_at,
        "updated_at": chart.updated_at or chart.created_at,
        "revisions": list(chart.revisions.all()),
    }


def own_chart(request: HttpRequest, chart_id: int) -> Chart:
    return get_object_or_404(chart_queryset(request.user), pk=chart_id)


def check_fields(dataset: Dataset, data: RevisionIn) -> str | None:
    names = {c["name"] for c in dataset.profile.get("columns", [])}
    for label, value in (("x", data.x_field), ("y", data.y_field), ("color", data.color_field)):
        if value and value not in names:
            return f"{label} field '{value}' is not a column of this dataset."
    return None


def rate_limited(user) -> bool:
    since = timezone.now() - timedelta(hours=1)
    recent = ChartRevision.objects.filter(user=user, created_at__gte=since).count()
    return recent >= settings.RATE_REVISIONS_PER_HOUR


@router.get("", response=list[ChartOut])
def list_charts(request: HttpRequest):
    return [chart_out(c) for c in chart_queryset(request.user)]


@router.post("", response={201: ChartDetail, 400: Detail, 409: Detail, 429: Detail})
def create_chart(request: HttpRequest, data: ChartIn):
    """Creates the chart and its revision 1 in one request (SPEC §7)."""
    if not ModelConfig.objects.filter(user=request.user).exists():
        return 400, {"detail": "Configure a model under Settings before creating charts."}
    if rate_limited(request.user):
        return 429, {"detail": "Revision limit reached. Try again in an hour."}
    dataset = get_object_or_404(Dataset, pk=data.dataset_id, user=request.user)
    if dataset.status != Dataset.Status.DONE:
        return 409, {"detail": "The dataset has not been parsed yet."}
    if problem := check_fields(dataset, data):
        return 400, {"detail": problem}

    with transaction.atomic():
        chart = Chart.objects.create(
            user=request.user,
            dataset=dataset,
            title=(data.title or data.prompt[:80]).strip(),
        )
        ChartRevision.objects.create(
            chart=chart,
            user=request.user,
            revision_no=1,
            x_field=data.x_field,
            y_field=data.y_field,
            color_field=data.color_field or None,
            prompt=data.prompt.strip(),
        )
    return 201, chart_out(own_chart(request, chart.pk))


@router.get("/{chart_id}", response=ChartDetail)
def get_chart(request: HttpRequest, chart_id: int):
    return chart_out(own_chart(request, chart_id))


@router.patch("/{chart_id}", response={200: ChartDetail, 400: Detail})
def patch_chart(request: HttpRequest, chart_id: int, data: ChartPatch):
    chart = own_chart(request, chart_id)
    fields = []
    if data.title is not None:
        chart.title = data.title.strip()
        fields.append("title")
    if data.current_revision_id is not None:
        revision = chart.revisions.filter(pk=data.current_revision_id, status="done").first()
        if revision is None:
            return 400, {"detail": "current_revision must be a finished revision of this chart."}
        chart.current_revision = revision
        fields.append("current_revision")
    if fields:
        chart.save(update_fields=fields)
    return 200, chart_out(own_chart(request, chart_id))


@router.delete("/{chart_id}", response={204: None})
def delete_chart(request: HttpRequest, chart_id: int):
    own_chart(request, chart_id).delete()
    return 204, None


@router.get("/{chart_id}/export")
def export_chart(request: HttpRequest, chart_id: int):
    """Reproducibility bundle as a JSON download (SPEC §7)."""
    chart = own_chart(request, chart_id)
    response = JsonResponse(
        build_bundle(chart), json_dumps_params={"ensure_ascii": False, "indent": 1}
    )
    response["Content-Disposition"] = f'attachment; filename="charter-chart-{chart.pk}.json"'
    return response


@router.post("/{chart_id}/revisions", response={201: RevisionOut, 400: Detail, 429: Detail})
def create_revision(request: HttpRequest, chart_id: int, data: RevisionIn):
    chart = own_chart(request, chart_id)
    if not ModelConfig.objects.filter(user=request.user).exists():
        return 400, {"detail": "Configure a model under Settings before creating charts."}
    if rate_limited(request.user):
        return 429, {"detail": "Revision limit reached. Try again in an hour."}
    if problem := check_fields(chart.dataset, data):
        return 400, {"detail": problem}
    parent = None
    if data.parent_id is not None:
        parent = chart.revisions.filter(pk=data.parent_id).first()
        if parent is None:
            return 400, {"detail": "parent_id must be a revision of this chart."}
    with transaction.atomic():
        last = chart.revisions.select_for_update().aggregate(n=Max("revision_no"))["n"] or 0
        revision = ChartRevision.objects.create(
            chart=chart,
            user=request.user,
            revision_no=last + 1,
            parent=parent,
            x_field=data.x_field,
            y_field=data.y_field,
            color_field=data.color_field or None,
            prompt=data.prompt.strip(),
        )
    return 201, revision_out(revision, request.user)


def revision_out(revision: ChartRevision, user) -> dict:
    """Adds an estimate at today's prices for revisions that ran before any
    price was entered. Never written back: the stored cost stays authoritative."""
    out = {field.name: getattr(revision, field.name) for field in ChartRevision._meta.fields}
    out["chart_id"] = revision.chart_id
    out["parent_id"] = revision.parent_id
    out["cost_at_current_prices"] = None
    if revision.cost_usd is None and revision.usage:
        config = ModelConfig.objects.filter(user=user).first()
        if config is not None:
            out["cost_at_current_prices"] = estimate_cost(revision.usage, config)
    return out


@revisions_router.get("/{revision_id}", response=RevisionOut)
def get_revision(request: HttpRequest, revision_id: int):
    """The poll target while a revision is pending or running (SPEC §4)."""
    revision = get_object_or_404(ChartRevision, pk=revision_id, user=request.user)
    return revision_out(revision, request.user)
