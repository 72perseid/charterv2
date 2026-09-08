from datetime import datetime

from ninja import Schema


class DatasetOut(Schema):
    id: int
    name: str
    original_filename: str
    row_count: int
    column_count: int
    size_bytes: int
    privacy_level: str
    status: str
    error_message: str | None
    created_at: datetime
