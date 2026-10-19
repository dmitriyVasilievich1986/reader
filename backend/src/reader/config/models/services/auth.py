"""Auth configuration model."""

__all__ = ("Auth",)

from typing import Literal

from pydantic import BaseModel, Field, SecretStr


class Auth(BaseModel):
    """JWT service configuration.

    Attributes:
        jwt_secret_key (SecretStr): Secret key used to sign and verify JWTs.
        jwt_algorithm (Literal["HS256", "HS384", "HS512"]): HMAC algorithm used
            to sign JWTs. Defaults to ``"HS256"``.

    """

    jwt_secret_key: SecretStr = Field(..., description="The secret key for the JWT service")
    jwt_algorithm: Literal["HS256", "HS384", "HS512"] = Field("HS256", description="The algorithm for the auth service")
