"""API server configuration model.

This module defines the configuration model for API server settings, including
port, debug mode, and logging level.
"""

__all__ = ("APIInfo",)

from pydantic import BaseModel, Field


class APIInfo(BaseModel):
    """Configuration model for API server settings.

    This model defines the core settings for the API server, including the
    port on which the server listens, debug mode for development, and the
    logging level for application logs.

    Attributes:
        host: The host of the application. Defaults to "0.0.0.0".
        app_port: The TCP port number on which the API server listens for
            incoming connections. This is a required field.
        debug: Whether to run the application in debug mode. Debug mode
            provides more verbose error messages and may enable additional
            development features. Defaults to False for production safety.
        log_level: The logging level for the application. Valid values
            include "DEBUG", "INFO", "WARNING", "ERROR", and "CRITICAL".
            Defaults to "INFO".

    Example:
        >>> api_info = APIInfo(
        ...     app_port=8000,
        ...     debug=True,
        ...     log_level="DEBUG"
        ... )

    """

    host: str = Field("0.0.0.0", description="The host of the application")
    app_port: int = Field(8000, description="The port of the application")
    debug: bool = Field(False, description="The debug mode of the application")
    log_level: str = Field("INFO", description="The log level of the application")
