"""Access token model."""

__all__ = ("AccessToken",)

from datetime import datetime

from pydantic import BaseModel, Field


class AccessToken(BaseModel):
    """Signed JWT string and absolute expiry returned to API clients."""

    token: str = Field(..., description="The access token")
    expires_at: datetime = Field(..., description="The expiration date of the token")
