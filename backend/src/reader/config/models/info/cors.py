"""Cross-Origin Resource Sharing (CORS) settings for the application."""

__all__ = ("CORSInfo",)

from pydantic import BaseModel, Field


class CORSInfo(BaseModel):
    """HTTP CORS policy loaded from configuration.

    These values configure how browsers may call the API from other origins.

    Attributes:
        origins (str): Comma-separated allowed origins or "*" to allow any
            origin.
        allow_credentials (bool): Whether the server may expose cookies or HTTP
            authentication to cross-origin callers.
        allow_methods (list[str]): HTTP methods callers may use in cross-origin
            requests.
        allow_headers (list[str]): Request headers callers may send on
            cross-origin requests.

    """

    origins: str = Field(
        "*",
        description='Comma-separated allowed origins or "*" to allow any origin',
    )
    allow_credentials: bool = Field(
        True,
        description="Whether to allow credentials to cross-origin callers",
    )
    allow_methods: list[str] = Field(
        ["*"],
        description='List of allowed HTTP methods or "*" to allow any method',
    )
    allow_headers: list[str] = Field(
        ["*"],
        description='List of allowed HTTP headers or "*" to allow any header',
    )
