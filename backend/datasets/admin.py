from django.contrib import admin

from datasets.models import Dataset


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "status", "row_count", "column_count", "created_at")
    list_filter = ("status", "privacy_level")
    search_fields = ("name", "original_filename", "user__email")
