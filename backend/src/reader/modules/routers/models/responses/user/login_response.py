"""Login response model."""

__all__ = ("LoginResponse",)

from datetime import datetime

from pydantic import Field

from reader.modules.routers.models.base import BaseResponseModel


class LoginResponse(BaseResponseModel):
    """Login response model."""

    access_token: str = Field(..., description="The access token of the user")
    expires_at: datetime = Field(..., description="The expiration date of the token")
