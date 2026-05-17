"""HTTP API routes for category CRUD operations."""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from loguru import logger
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError

from reader.modules.middlewares.dependencies import get_db
from reader.modules.routers.models.base.metadata import PaginationMetadata
from reader.modules.routers.models.requests.categories import GetAllCategoriesQuery, PatchCategoryBody, PostCategoryBody
from reader.modules.routers.models.responses.categories import (
    GetAllCategoriesResponse,
    GetSingleCategoryResponse,
    SimpleCategoryResponse,
)
from reader.services.daos.category_dao import CategoryDAO
from reader.services.database import AsyncDatabaseClient

router = APIRouter(prefix="/category", tags=["Categories"])


@router.get("", response_model=GetAllCategoriesResponse, status_code=status.HTTP_200_OK, summary="Get all categories")
async def get_all_categories(
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
    query: Annotated[GetAllCategoriesQuery, Query(description="Pagination and sorting parameters")],
) -> GetAllCategoriesResponse:
    """Return a paginated list of categories with optional filters.

    Args:
        db (AsyncDatabaseClient): Database session from dependency injection.
        query (GetAllCategoriesQuery): Pagination and filter parameters.

    Returns:
        GetAllCategoriesResponse: Category rows and pagination metadata.

    Raises:
        HTTPException: If a related entity is missing (400) or listing fails (500).

    """
    categories_dao = CategoryDAO(database_client=db)

    try:
        payload, total = await categories_dao.get_all(**query.model_dump())
    except IntegrityError as e:
        logger.exception("Related object not found", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related object not found") from e
    except SQLAlchemyError as e:
        logger.exception("Error getting all categories", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error getting all categories"
        ) from e

    data = [SimpleCategoryResponse.model_validate(category) for category in payload]
    metadata = PaginationMetadata(total=total, **query.model_dump())

    return GetAllCategoriesResponse(data=data, metadata=metadata)


@router.get(
    "/{category_id}",
    response_model=GetSingleCategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single category",
)
async def get_single_category(
    category_id: Annotated[int, Path(..., description="The ID of the category")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleCategoryResponse:
    """Return one category by primary key.

    Args:
        category_id (int): Identifier of the category to load.
        db (AsyncDatabaseClient): Database session from dependency injection.

    Returns:
        GetSingleCategoryResponse: Serialized category.

    Raises:
        HTTPException: If the category does not exist (404), a related entity is
            missing (400), or loading fails (500).

    """
    categories_dao = CategoryDAO(database_client=db)

    try:
        payload = await categories_dao.get_by_pk(category_id)
    except NoResultFound as e:
        logger.error(f"Category with ID {category_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found") from e
    except IntegrityError as e:
        logger.exception("Related object not found", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related object not found") from e
    except SQLAlchemyError as e:
        logger.exception("Error getting single category", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error getting single category"
        ) from e

    return GetSingleCategoryResponse.model_validate(payload)


@router.post(
    "", response_model=GetSingleCategoryResponse, status_code=status.HTTP_201_CREATED, summary="Create a new category"
)
async def create_category(
    body: Annotated[PostCategoryBody, Body(..., description="The body of the category")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleCategoryResponse:
    """Create a category and return the persisted row.

    Args:
        body (PostCategoryBody): Fields for the new category.
        db (AsyncDatabaseClient): Database session from dependency injection.

    Returns:
        GetSingleCategoryResponse: Serialized created category.

    Raises:
        HTTPException: If a related entity is missing (400) or creation fails (500).

    """
    categories_dao = CategoryDAO(database_client=db)

    try:
        payload = await categories_dao.create(**body.model_dump())
    except IntegrityError as e:
        logger.exception("Related object not found", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related object not found") from e
    except SQLAlchemyError as e:
        logger.exception("Error creating category", exc_info=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating category") from e

    return GetSingleCategoryResponse.model_validate(payload)


@router.patch(
    "/{category_id}",
    response_model=GetSingleCategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a category",
)
async def update_category(
    category_id: Annotated[int, Path(..., description="The ID of the category")],
    body: Annotated[PatchCategoryBody, Body(..., description="The body of the category")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleCategoryResponse:
    """Apply a partial update to an existing category.

    Args:
        category_id (int): Identifier of the category to update.
        body (PatchCategoryBody): Fields to change; omitted fields stay unchanged.
        db (AsyncDatabaseClient): Database session from dependency injection.

    Returns:
        GetSingleCategoryResponse: Serialized category after update.

    Raises:
        HTTPException: If the category does not exist (404), a related entity is
            missing (400), or the update fails (500).

    """
    categories_dao = CategoryDAO(database_client=db)

    try:
        payload = await categories_dao.update(category_id, **body.model_dump(exclude_unset=True))
    except NoResultFound as e:
        logger.error(f"Category with ID {category_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found") from e
    except IntegrityError as e:
        logger.exception("Related object not found", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related object not found") from e
    except SQLAlchemyError as e:
        logger.exception("Error updating category", exc_info=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating category") from e

    return GetSingleCategoryResponse.model_validate(payload)


@router.delete(
    "/{category_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT, summary="Delete a category"
)
async def delete_category(
    category_id: Annotated[int, Path(..., description="The ID of the category")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> None:
    """Delete a category by primary key.

    Args:
        category_id (int): Identifier of the category to remove.
        db (AsyncDatabaseClient): Database session from dependency injection.

    Returns:
        None

    Raises:
        HTTPException: If the category does not exist (404) or deletion fails (500).

    """
    categories_dao = CategoryDAO(database_client=db)

    try:
        await categories_dao.delete(category_id)
    except NoResultFound as e:
        logger.error(f"Category with ID {category_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found") from e
    except SQLAlchemyError as e:
        logger.exception("Error deleting category", exc_info=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting category") from e
