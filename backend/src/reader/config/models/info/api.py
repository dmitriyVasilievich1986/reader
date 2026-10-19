"""API server configuration model.

This module defines the configuration model for API server settings, including
host, port, debug mode, logging level and URL prefix.
"""

__all__ = ("APIInfo",)

from pydantic import BaseModel, Field


class APIInfo(BaseModel):
    """Configuration model for API server settings.

    This model defines the core settings for the API server: the address and
    port it listens on, debug mode for development, the logging level and the
    URL prefix for the API.

    Attributes:
        host (str): Host address the API server binds to. Defaults to
            ``"0.0.0.0"``.
        app_port (int): TCP port the API server listens on. Defaults to
            ``8000``.
        debug (bool): Whether to run the application in debug mode, which gives
            more verbose error messages. Defaults to ``False``.
        log_level (str): Logging level of the application, e.g. ``"DEBUG"``,
            ``"INFO"``, ``"WARNING"``, ``"ERROR"`` or ``"CRITICAL"``. Defaults
            to ``"INFO"``.
        api_prefix (str): URL prefix of the API. Defaults to ``"/reader"``.

    Example:
        >>> api_info = APIInfo(
        ...     app_port=8000,
        ...     debug=True,
        ...     log_level="DEBUG",
        ... )

    """

    host: str = Field("0.0.0.0", description="The host of the application")
    app_port: int = Field(8000, description="The port of the application")
    debug: bool = Field(False, description="The debug mode of the application")
    log_level: str = Field("INFO", description="The log level of the application")
    api_prefix: str = Field("/reader", description="The URL prefix of the API")
