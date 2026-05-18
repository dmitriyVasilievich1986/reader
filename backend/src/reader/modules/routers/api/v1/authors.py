"""HTTP API routes for author CRUD operations."""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from loguru import logger
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError

from reader.modules.middlewares.dependencies import admin_required, get_db, user_authorized
from reader.modules.routers.models.base.metadata import PaginationMetadata
from reader.modules.routers.models.requests.authors import GetAllAuthorsQuery, PatchAuthorBody, PostAuthorBody
from reader.modules.routers.models.responses.authors import (
    GetAllAuthorsResponse,
    GetSingleAuthorResponse,
    SimpleAuthorResponse,
)
from reader.services.daos.author_dao import AuthorDAO
from reader.services.database import AsyncDatabaseClient

router = APIRouter(prefix="/author", tags=["Authors"])


@router.get(
    "",
    response_model=GetAllAuthorsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all authors",
    dependencies=[Depends(user_authorized)],
)
async def get_all_authors(
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
    query: Annotated[GetAllAuthorsQuery, Query(description="Pagination and sorting parameters")],
) -> GetAllAuthorsResponse:
    """Return a paginated list of authors with optional filters.

    Args:
        db (AsyncDatabaseClient): Database session from dependency injection.
        query (GetAllAuthorsQuery): Pagination and filter parameters.

    Returns:
        GetAllAuthorsResponse: Author rows and pagination metadata.

    Raises:
        HTTPException: If a related entity is missing (400) or listing fails (500).

    """
    authors_dao = AuthorDAO(database_client=db)

    try:
        payload, total = await authors_dao.get_all(**query.model_dump())
    except SQLAlchemyError as e:
        logger.exception("Error getting all authors", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error getting all authors"
        ) from e

    data = [SimpleAuthorResponse.model_validate(author) for author in payload]
    metadata = PaginationMetadata(total=total, **query.model_dump())

    return GetAllAuthorsResponse(data=data, metadata=metadata)


@router.get(
    "/{author_id}",
    response_model=GetSingleAuthorResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single author",
    dependencies=[Depends(user_authorized)],
)
async def get_single_author(
    author_id: Annotated[int, Path(..., description="The ID of the author")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleAuthorResponse:
    """Return one author by primary key.

    Args:
        author_id (int): Identifier of the author to load.
        db (AsyncDatabaseClient): Database session from dependency injection.

    Returns:
        GetSingleAuthorResponse: Serialized author.

    Raises:
        HTTPException: If the author does not exist (404), a related entity is
            missing (400), or loading fails (500).

    """
    authors_dao = AuthorDAO(database_client=db)

    try:
        payload = await authors_dao.get_by_pk(author_id)
    except NoResultFound as e:
        logger.error(f"Author with ID {author_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found") from e
    except SQLAlchemyError as e:
        logger.exception("Error getting single author", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error getting single author"
        ) from e

    return GetSingleAuthorResponse.model_validate(payload)


@router.post(
    "",
    response_model=GetSingleAuthorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new author",
    dependencies=[Depends(admin_required)],
)
async def create_author(
    body: Annotated[PostAuthorBody, Body(..., description="The body of the author")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleAuthorResponse:
    """Create an author and return the persisted row.

    Args:
        body (PostAuthorBody): Fields for the new author.
        db (AsyncDatabaseClient): Database session from dependency injection.

    Returns:
        GetSingleAuthorResponse: Serialized created author.

    Raises:
        HTTPException: If a related entity is missing (400) or creation fails (500).

    """
    authors_dao = AuthorDAO(database_client=db)

    try:
        payload = await authors_dao.create(**body.model_dump())
    except IntegrityError as e:
        logger.exception("Related object not found", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related object not found") from e
    except SQLAlchemyError as e:
        logger.exception("Error creating author", exc_info=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating author") from e

    return GetSingleAuthorResponse.model_validate(payload)


@router.patch(
    "/{author_id}",
    response_model=GetSingleAuthorResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an author",
    dependencies=[Depends(admin_required)],
)
async def update_author(
    author_id: Annotated[int, Path(..., description="The ID of the author")],
    body: Annotated[PatchAuthorBody, Body(..., description="The body of the author")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleAuthorResponse:
    """Apply a partial update to an existing author.

    Args:
        author_id (int): Identifier of the author to update.
        body (PatchAuthorBody): Fields to change; omitted fields stay unchanged.
        db (AsyncDatabaseClient): Database session from dependency injection.

    Returns:
        GetSingleAuthorResponse: Serialized author after update.

    Raises:
        HTTPException: If the author does not exist (404), a related entity is
            missing (400), or the update fails (500).

    """
    authors_dao = AuthorDAO(database_client=db)

    try:
        payload = await authors_dao.update(author_id, **body.model_dump(exclude_unset=True))
    except NoResultFound as e:
        logger.error(f"Author with ID {author_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found") from e
    except IntegrityError as e:
        logger.exception("Related object not found", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related object not found") from e
    except SQLAlchemyError as e:
        logger.exception("Error updating author", exc_info=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating author") from e

    return GetSingleAuthorResponse.model_validate(payload)


@router.delete(
    "/{author_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an author",
    dependencies=[Depends(admin_required)],
)
async def delete_author(
    author_id: Annotated[int, Path(..., description="The ID of the author")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> None:
    """Delete an author by primary key.

    Args:
        author_id (int): Identifier of the author to remove.
        db (AsyncDatabaseClient): Database session from dependency injection.

    Returns:
        None

    Raises:
        HTTPException: If the author does not exist (404) or deletion fails (500).

    """
    authors_dao = AuthorDAO(database_client=db)

    try:
        await authors_dao.delete(author_id)
    except NoResultFound as e:
        logger.error(f"Author with ID {author_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found") from e
    except SQLAlchemyError as e:
        logger.exception("Error deleting author", exc_info=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting author") from e
