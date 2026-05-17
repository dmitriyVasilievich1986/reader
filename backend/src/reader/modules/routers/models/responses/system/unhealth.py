"""Unhealth response models."""

__all__ = ("UnhealthResponse",)

from pydantic import Field

from reader.modules.routers.models.base import BaseResponseModel


class UnhealthResponse(BaseResponseModel):
    """Response model for unhealth messages."""

    detail: str = Field(
        ...,
        description="Unhealth detail message.",
    )
