"""FastAPI application factory module.

This module provides the application factory function that creates and configures
the FastAPI application instance with all necessary middleware, routers, and settings.
"""

__all__ = ("get_app",)


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from reader import __version__ as app_version
from reader.config.app_config import AppConfig
from reader.modules.middlewares.app_lifespan import lifespan
from reader.utils import mount_static_files

from .routers import api_router


def get_app(config: AppConfig | None = None) -> FastAPI:
    """Create and configure a FastAPI application instance.

    This function initializes a FastAPI application with the provided configuration,
    sets up the application title, description, version, debug mode, and log level.
    It also includes the system router and sets up the application lifespan context.

    Args:
        config: Optional application configuration. If not provided, the default
            AppConfig instance will be retrieved or created.

    Returns:
        A fully configured FastAPI application instance ready to be run.

    """
    logger.info("Getting app...")
    app_config: AppConfig = config or AppConfig.get_or_create()
    logger.debug(f"Config: {app_config}")

    logger.debug("Creating FastAPI app...")
    app = FastAPI(
        title=app_config.info.name,
        description=app_config.info.description,
        version=app_version,
        debug=app_config.info.api_info.debug,
        lifespan=lifespan,
    )

    logger.debug(f"Adding CORS middleware with allowed origins: {app_config.info.cors_info.origins}")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_config.info.cors_info.origins,
        allow_credentials=app_config.info.cors_info.allow_credentials,
        allow_methods=app_config.info.cors_info.allow_methods,
        allow_headers=app_config.info.cors_info.allow_headers,
    )

    logger.debug("Mounting static assets from %s...", str(app_config.info.paths_info.static))
    mount_static_files(app, app_config)

    logger.debug("Adding API router...")
    app.include_router(api_router)

    logger.info("App created successfully.")
    return app
