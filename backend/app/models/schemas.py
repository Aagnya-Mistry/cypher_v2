"""Shapes of data going in and out of the API."""

from datetime import datetime

from pydantic import BaseModel

# Which financial years a report can be tagged with. The rulebook picks rule versions by this.
FISCAL_YEARS = ("FY2024-25", "FY2025-26")


class DocumentOut(BaseModel):
    id: str
    company_name: str
    fiscal_year: str
    original_filename: str
    size_bytes: int
    page_count: int
    status: str
    created_at: datetime
