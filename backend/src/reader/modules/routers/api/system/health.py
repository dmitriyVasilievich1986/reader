"""Health check API router."""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from reader.modules.middlewares.dependencies import get_db
from reader.modules.routers.models.responses.system import (
    HealthResponse,
    UnhealthResponse,
)
from reader.services.database import AsyncDatabaseClient

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    responses={
        status.HTTP_200_OK: {
            "model": HealthResponse,
            "description": "Service is healthy and connected to dependencies.",
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": UnhealthResponse,
            "description": "Service is unavailable.",
        },
    },
)
async def health_check(
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> HealthResponse:
    """Perform a health check on the service by verifying connectivity to the database.

    Raises:
        HTTPException: If the database connection check fails, returns a 503 Service Unavailable error.

    Returns:
        HealthResponse: Indicates the service is healthy if all checks pass.

    """
    if not all((await db.healthcheck(),)):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service is unhealthy.",
        )

    return HealthResponse(
        status="ok",
    )
