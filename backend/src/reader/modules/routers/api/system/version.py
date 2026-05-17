"""Version API router."""

__all__ = ("router",)


from fastapi import APIRouter, status

from reader import __version__ as app_version
from reader.modules.routers.models.responses.system import VersionResponse

router = APIRouter()


@router.get(
    "/version",
    response_model=VersionResponse,
    status_code=status.HTTP_200_OK,
    summary="Service Version",
)
async def get_version() -> VersionResponse:
    """Asynchronously retrieves the current service version.

    Returns:
        VersionResponse: An object containing the current version of the service.

    """
    return VersionResponse(version=app_version)
