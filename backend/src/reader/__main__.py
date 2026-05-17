"""CLI entry point: load config, construct the app, and serve it with uvicorn."""

import uvicorn

from reader.config.app_config import AppConfig
from reader.modules.app import get_app


def main() -> None:
    """Load application configuration, build the ASGI app, and run uvicorn.

    Returns:
        None

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
