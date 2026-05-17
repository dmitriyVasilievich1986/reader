"""Version response models."""

__all__ = ("VersionResponse",)

from pydantic import Field

from reader.modules.routers.models.base import BaseResponseModel


class VersionResponse(BaseResponseModel):
    """Response model for service version."""

    version: str = Field(
        ...,
        description="Service version",
    )
