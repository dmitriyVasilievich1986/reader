"""Catch-all HTTP routes that serve the single-page application shell."""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.responses import FileResponse

from reader.config import AppConfig
from reader.modules.middlewares.dependencies import get_config

router = APIRouter()


@router.get("/{_path:path}", include_in_schema=False, status_code=status.HTTP_200_OK)
async def spa_fallback(
    _path: Annotated[
        str,
        Path(
            ...,
            description="Request path segment (unused; accepted for catch-all routing)",
        ),
    ],
    app_config: Annotated[AppConfig, Depends(get_config)],
) -> FileResponse:
    """Return ``index.html`` for any path so the client router can handle URLs.

    Args:
        _path (str): Matched path; not read, only satisfies routing.
        app_config (AppConfig): Application configuration (resolved static paths).

    Returns:
        FileResponse: The SPA entry HTML file from configured ``paths_info``.

    """
    if not (index_html := app_config.info.paths_info.index_html).exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Index HTML file not found")

    return FileResponse(index_html)
