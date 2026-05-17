"""Register default static file mounts on a FastAPI application.

Mounts ``/assets`` and ``/images`` when the paths from ``AppConfig`` exist.
"""

__all__ = ("mount_static_files",)

from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from loguru import logger

if TYPE_CHECKING:
    from reader.config import AppConfig


def mount_static_files(app: FastAPI, app_config: "AppConfig") -> None:
    """Mount bundled assets and images from configuration when directories exist.

    Args:
        app (FastAPI): Application instance to attach mounts to.
        app_config (AppConfig): Loaded configuration (paths from ``paths_info``).

    Returns:
        None

    """
    if (assets_path := app_config.info.paths_info.assets).exists():
        logger.debug("Mounting assets from %s...", str(assets_path))
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
    else:
        logger.info("Static directory %s does not exist, skipping mount.", str(assets_path))

    if (images_path := app_config.info.paths_info.images).exists():
        logger.debug("Mounting images from %s...", str(images_path))
        app.mount("/images", StaticFiles(directory=images_path), name="images")
    else:
        logger.info("Static directory %s does not exist, skipping mount.", str(images_path))
