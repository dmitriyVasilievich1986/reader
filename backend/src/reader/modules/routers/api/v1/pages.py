"""HTTP API routes for page CRUD operations."""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from loguru import logger
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError

from reader.modules.middlewares.dependencies import get_db
from reader.modules.routers.models.base.metadata import PaginationMetadata
from reader.modules.routers.models.requests.pages import GetAllPagesQuery, PatchPageBody, PostPageBody
from reader.modules.routers.models.responses.pages import (
    GetAllPagesResponse,
    GetSinglePageResponse,
    SimplePageResponse,
)
from reader.services.daos.page_dao import PageDAO
from reader.services.database import AsyncDatabaseClient

router = APIRouter(prefix="/page", tags=["Pages"])


@router.get("", response_model=GetAllPagesResponse, status_code=status.HTTP_200_OK, summary="Get all pages")
async def get_all_pages(
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
    query: Annotated[GetAllPagesQuery, Query(description="Pagination and sorting parameters")],
) -> GetAllPagesResponse:
    """Return a paginated list of pages with optional filters.

    Args:
        db (AsyncDatabaseClient): Database session from dependency injection.
        query (GetAllPagesQuery): Pagination and filter parameters.

    Returns:
        GetAllPagesResponse: Page rows and pagination metadata.

    Raises:
        HTTPException: If a related entity is missing (400) or listing fails (500).

    """
    pages_dao = PageDAO(database_client=db)

    try:
        payload, total = await pages_dao.get_all(**query.model_dump())
    except IntegrityError as e:
        logger.exception("Related object not found", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related object not found") from e
    except SQLAlchemyError as e:
        logger.exception("Error getting all pages", exc_info=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error getting all pages") from e

    data = [SimplePageResponse.model_validate(page) for page in payload]
    metadata = PaginationMetadata(total=total, **query.model_dump())

    return GetAllPagesResponse(data=data, metadata=metadata)


@router.get(
    "/{page_id}",
    response_model=GetSinglePageResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single page",
)
async def get_single_page(
    page_id: Annotated[int, Path(..., description="The ID of the page")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSinglePageResponse:
    """Return one page by primary key.

    Args:
        page_id (int): Identifier of the page to load.
        db (AsyncDatabaseClient): Database session from dependency injection.

    Returns:
        GetSinglePageResponse: Serialized page.

    Raises:
        HTTPException: If the page does not exist (404), a related entity is
            missing (400), or loading fails (500).

    """
    pages_dao = PageDAO(database_client=db)

    try:
        payload = await pages_dao.get_by_pk(page_id)
    except NoResultFound as e:
        logger.error(f"Page with ID {page_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found") from e
    except IntegrityError as e:
        logger.exception("Related object not found", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related object not found") from e
    except SQLAlchemyError as e:
        logger.exception("Error getting single page", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error getting single page"
        ) from e

    return GetSinglePageResponse.model_validate(payload)


@router.post("", response_model=GetSinglePageResponse, status_code=status.HTTP_201_CREATED, summary="Create a new page")
async def create_page(
    body: Annotated[PostPageBody, Body(..., description="The body of the page")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSinglePageResponse:
    """Create a page and return the persisted row.

    Args:
        body (PostPageBody): Fields for the new page.
        db (AsyncDatabaseClient): Database session from dependency injection.

    Returns:
        GetSinglePageResponse: Serialized created page.

    Raises:
        HTTPException: If a related entity is missing (400) or creation fails (500).

    """
    pages_dao = PageDAO(database_client=db)

    try:
        payload = await pages_dao.create(**body.model_dump())
    except IntegrityError as e:
        logger.exception("Related object not found", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related object not found") from e
    except SQLAlchemyError as e:
        logger.exception("Error creating page", exc_info=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating page") from e

    return GetSinglePageResponse.model_validate(payload)


@router.patch(
    "/{page_id}",
    response_model=GetSinglePageResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a page",
)
async def update_page(
    page_id: Annotated[int, Path(..., description="The ID of the page")],
    body: Annotated[PatchPageBody, Body(..., description="The body of the page")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSinglePageResponse:
    """Apply a partial update to an existing page.

    Args:
        page_id (int): Identifier of the page to update.
        body (PatchPageBody): Fields to change; omitted fields stay unchanged.
        db (AsyncDatabaseClient): Database session from dependency injection.

    Returns:
        GetSinglePageResponse: Serialized page after update.

    Raises:
        HTTPException: If the page does not exist (404), a related entity is
            missing (400), or the update fails (500).

    """
    pages_dao = PageDAO(database_client=db)

    try:
        payload = await pages_dao.update(page_id, **body.model_dump(exclude_unset=True))
    except NoResultFound as e:
        logger.error(f"Page with ID {page_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found") from e
    except IntegrityError as e:
        logger.exception("Related object not found", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related object not found") from e
    except SQLAlchemyError as e:
        logger.exception("Error updating page", exc_info=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating page") from e

    return GetSinglePageResponse.model_validate(payload)


@router.delete("/{page_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT, summary="Delete a page")
async def delete_page(
    page_id: Annotated[int, Path(..., description="The ID of the page")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> None:
    """Delete a page by primary key.

    Args:
        page_id (int): Identifier of the page to remove.
        db (AsyncDatabaseClient): Database session from dependency injection.

    Returns:
        None

    Raises:
        HTTPException: If the page does not exist (404) or deletion fails (500).

    """
    pages_dao = PageDAO(database_client=db)

    try:
        await pages_dao.delete(page_id)
    except NoResultFound as e:
        logger.error(f"Page with ID {page_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found") from e
    except SQLAlchemyError as e:
        logger.exception("Error deleting page", exc_info=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting page") from e
