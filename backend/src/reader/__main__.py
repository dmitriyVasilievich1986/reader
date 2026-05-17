"""Main entry point for the reader application.

This module provides the main entry point that initializes the FastAPI application
and runs it using uvicorn ASGI server.
"""

import uvicorn

from reader.config.app_config import AppConfig
from reader.modules.app import get_app


def main():
    """Initialize and run the FastAPI application.

    This function retrieves the application configuration, creates the FastAPI
    app instance, and starts the uvicorn server with the configured host, port,
    and log level.
    """
    config = AppConfig.get_or_create()

    app = get_app(config=config)

    uvicorn.run(
        app,
        host=config.info.api_info.host,
        port=config.info.api_info.app_port,
        log_level=config.info.api_info.log_level.lower(),
    )


if __name__ == "__main__":
    main()
