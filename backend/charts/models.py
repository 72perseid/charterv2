from django.conf import settings
from django.db import models


class Chart(models.Model):
    """A chart is a dataset plus a series of revisions (SPEC §5)."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    dataset = models.ForeignKey("datasets.Dataset", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    current_revision = models.ForeignKey(
        "charts.ChartRevision", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "charts"
        indexes = [models.Index(fields=["user", "created_at"])]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


class ChartRevision(models.Model):
    """One attempt to produce a spec, with the full record of how (SPEC §5)."""

    class Status(models.TextChoices):
        PENDING = "pending"
        RUNNING = "running"
        DONE = "done"
        FAILED = "failed"

    chart = models.ForeignKey(Chart, on_delete=models.CASCADE, related_name="revisions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    revision_no = models.IntegerField()
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)
    x_field = models.CharField(max_length=200)
    y_field = models.CharField(max_length=200)
    color_field = models.CharField(max_length=200, null=True, blank=True)
    prompt = models.TextField(max_length=1000)
    # Chosen beside the request (generation/intent.py): what the chart shows,
    # and one optional "only rows where field = value".
    show = models.CharField(max_length=16, default="auto")
    filter_field = models.CharField(max_length=200, null=True, blank=True)
    filter_value = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    attempts = models.IntegerField(default=0)
    error_message = models.TextField(null=True, blank=True)
    spec = models.JSONField(null=True, blank=True)
    corrections = models.JSONField(default=list)  # what validation changed in the model's spec
    # Reproducibility record, written by the worker.
    request = models.JSONField(null=True, blank=True)
    response_text = models.TextField(null=True, blank=True)
    model = models.CharField(max_length=200, blank=True)
    endpoint_host = models.CharField(max_length=200, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    seed = models.IntegerField(null=True, blank=True)
    prompt_version = models.CharField(max_length=40, blank=True)
    app_version = models.CharField(max_length=40, blank=True)
    usage = models.JSONField(null=True, blank=True)  # summed over attempts
    cost_usd = models.FloatField(null=True, blank=True)  # at the prices in force at run time
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chart_revisions"
        constraints = [
            models.UniqueConstraint(fields=["chart", "revision_no"], name="unique_revision_no")
        ]
        indexes = [models.Index(fields=["status", "created_at"])]
        ordering = ["revision_no"]

    def __str__(self) -> str:
        return f"{self.chart_id} r{self.revision_no}"
