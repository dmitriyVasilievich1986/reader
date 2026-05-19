"""Base model for date fields."""

__all__ = ("DateModel",)

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class DateModel(BaseModel):
    """Base model for datetime fields."""

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
