"""Base model for date fields."""

__all__ = ("BaseDateModel",)

from datetime import datetime

from pydantic import BaseModel, Field


class BaseDateModel(BaseModel):
    """Base model for date fields."""

    created_at: datetime = Field(..., description="The creation date of the model")
    updated_at: datetime = Field(..., description="The last update date of the model")
