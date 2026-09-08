from django.contrib import admin

from charts.models import Chart, ChartRevision


@admin.register(Chart)
class ChartAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "dataset", "created_at")
    search_fields = ("title", "user__email")


@admin.register(ChartRevision)
class ChartRevisionAdmin(admin.ModelAdmin):
    list_display = ("chart", "revision_no", "status", "model", "duration_ms", "created_at")
    list_filter = ("status",)
    readonly_fields = ("request", "response_text", "spec", "usage")
