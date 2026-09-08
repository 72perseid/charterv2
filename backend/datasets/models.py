from django.conf import settings
from django.db import models


class Dataset(models.Model):
    """One uploaded file and its parsed, profiled form. See SPEC §5."""

    class Privacy(models.TextChoices):
        MINIMAL = "minimal"
        STATISTICS = "statistics"
        SAMPLE = "sample"

    class Status(models.TextChoices):
        PENDING = "pending"
        RUNNING = "running"
        DONE = "done"
        FAILED = "failed"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    original_filename = models.CharField(max_length=255)
    original_path = models.CharField(max_length=500)
    parsed_path = models.CharField(max_length=500, blank=True)
    sheet_name = models.CharField(max_length=200, null=True, blank=True)
    parse_options = models.JSONField(default=dict)
    profile = models.JSONField(default=dict)
    row_count = models.IntegerField(default=0)
    column_count = models.IntegerField(default=0)
    size_bytes = models.IntegerField(default=0)
    privacy_level = models.CharField(
        max_length=16, choices=Privacy.choices, default=Privacy.STATISTICS
    )
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "datasets"
        indexes = [models.Index(fields=["user", "created_at"])]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name
