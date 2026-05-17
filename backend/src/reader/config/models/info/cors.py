"""CORS (Cross-Origin Resource Sharing) configuration model.

This module defines the configuration model for CORS settings, which control
how the API handles cross-origin requests from web browsers.
"""

__all__ = ("CORSInfo",)

from pydantic import BaseModel, Field


class CORSInfo(BaseModel):
    """Configuration model for Cross-Origin Resource Sharing (CORS) settings.

    This model defines the CORS policy for the API, controlling which origins,
    methods, and headers are allowed for cross-origin requests. CORS is a
    security feature that restricts web pages from making requests to a
    different domain than the one serving the web page.

    Attributes:
        origins: Comma-separated list of allowed origins. Use "*" to allow
            all origins (not recommended for production). Defaults to "*".
        allow_credentials: Whether to allow credentials (cookies, authorization
            headers) in cross-origin requests. Defaults to True.
        allow_methods: List of HTTP methods allowed for CORS requests.
            Use ["*"] to allow all methods. Defaults to ["*"].
        allow_headers: List of HTTP headers allowed in CORS requests.
            Use ["*"] to allow all headers. Defaults to ["*"].

    Example:
        >>> cors = CORSInfo(
        ...     origins="https://example.com,https://app.example.com",
        ...     allow_credentials=True,
        ...     allow_methods=["GET", "POST", "PUT", "DELETE"],
        ...     allow_headers=["Content-Type", "Authorization"]
        ... )

    """

    origins: str = Field(
        "*",
        description="Comma-separated list of allowed CORS origins",
    )
    allow_credentials: bool = Field(
        True,
        description="Whether to allow credentials in CORS",
    )
    allow_methods: list[str] = Field(
        ["*"],
        description="Comma-separated list of allowed HTTP methods for CORS",
    )
    allow_headers: list[str] = Field(
        ["*"],
        description="Comma-separated list of allowed HTTP headers for CORS",
    )
