"""HTTP API routes for book CRUD operations."""

__all__ = ("router",)

from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from loguru import logger
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError

from reader.modules.middlewares.dependencies import get_db
from reader.modules.middlewares.dependencies.user_authorized import user_authorized
from reader.modules.routers.models.base.metadata import PaginationMetadata
from reader.modules.routers.models.requests.books import GetAllBooksQuery, PatchBookBody, PostBookBody
from reader.modules.routers.models.responses.books import (
    GetAllBooksResponse,
    GetSingleBookResponse,
    SimpleBookResponse,
)
from reader.services.daos.book_dao import BookDAO
from reader.services.database import AsyncDatabaseClient

router = APIRouter(prefix="/book", tags=["Books"], dependencies=[Depends(user_authorized)])


@router.get("", response_model=GetAllBooksResponse, status_code=status.HTTP_200_OK, summary="Get all books")
async def get_all_books(
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
    query: Annotated[GetAllBooksQuery, Query(description="Pagination and sorting parameters")],
) -> GetAllBooksResponse:
    """Return a paginated list of books with optional filters.

    Args:
        db (AsyncDatabaseClient): Database session from dependency injection.
        query (GetAllBooksQuery): Pagination and filter parameters.

    Returns:
        GetAllBooksResponse: Book rows and pagination metadata.

    Raises:
        HTTPException: If a related entity is missing (400) or listing fails (500).

    """
    books_dao = BookDAO(database_client=db)

    try:
        payload, total = await books_dao.get_all(**query.model_dump())
    except SQLAlchemyError as e:
        logger.exception("Error getting all books", exc_info=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error getting all books") from e

    data = [SimpleBookResponse.model_validate(book) for book in payload]
    metadata = PaginationMetadata(total=total, **query.model_dump())

    return GetAllBooksResponse(data=data, metadata=metadata)


@router.get(
    "/{book_id}",
    response_model=GetSingleBookResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single book",
)
async def get_single_book(
    book_id: Annotated[int, Path(..., description="The ID of the book")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleBookResponse:
    """Return one book by primary key.

    Args:
        book_id (int): Identifier of the book to load.
        db (AsyncDatabaseClient): Database session from dependency injection.

    Returns:
        GetSingleBookResponse: Serialized book.

    Raises:
        HTTPException: If the book does not exist (404), a related entity is
            missing (400), or loading fails (500).

    """
    books_dao = BookDAO(database_client=db)

    try:
        payload = await books_dao.get_by_pk(book_id)
    except NoResultFound as e:
        logger.error(f"Book with ID {book_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found") from e
    except SQLAlchemyError as e:
        logger.exception("Error getting single book", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error getting single book"
        ) from e

    return GetSingleBookResponse.model_validate(payload)


@router.post("", response_model=GetSingleBookResponse, status_code=status.HTTP_201_CREATED, summary="Create a new book")
async def create_book(
    body: Annotated[PostBookBody, Body(..., description="The body of the book")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleBookResponse:
    """Create a book and return the persisted row.

    Args:
        body (PostBookBody): Fields for the new book.
        db (AsyncDatabaseClient): Database session from dependency injection.

    Returns:
        GetSingleBookResponse: Serialized created book.

    Raises:
        HTTPException: If a related entity is missing (400) or creation fails (500).

    """
    books_dao = BookDAO(database_client=db)

    try:
        payload = await books_dao.create(**body.model_dump())
    except IntegrityError as e:
        logger.exception("Related object not found", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related object not found") from e
    except SQLAlchemyError as e:
        logger.exception("Error creating book", exc_info=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating book") from e

    return GetSingleBookResponse.model_validate(payload)


@router.patch(
    "/{book_id}",
    response_model=GetSingleBookResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a book",
)
async def update_book(
    book_id: Annotated[int, Path(..., description="The ID of the book")],
    body: Annotated[PatchBookBody, Body(..., description="The body of the book")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> GetSingleBookResponse:
    """Apply a partial update to an existing book.

    Args:
        book_id (int): Identifier of the book to update.
        body (PatchBookBody): Fields to change; omitted fields stay unchanged.
        db (AsyncDatabaseClient): Database session from dependency injection.

    Returns:
        GetSingleBookResponse: Serialized book after update.

    Raises:
        HTTPException: If the book does not exist (404), a related entity is
            missing (400), or the update fails (500).

    """
    books_dao = BookDAO(database_client=db)

    try:
        payload = await books_dao.update(book_id, **body.model_dump(exclude_unset=True))
    except NoResultFound as e:
        logger.error(f"Book with ID {book_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found") from e
    except IntegrityError as e:
        logger.exception("Related object not found", exc_info=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Related object not found") from e
    except SQLAlchemyError as e:
        logger.exception("Error updating book", exc_info=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating book") from e

    return GetSingleBookResponse.model_validate(payload)


@router.delete("/{book_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT, summary="Delete a book")
async def delete_book(
    book_id: Annotated[int, Path(..., description="The ID of the book")],
    db: Annotated[AsyncDatabaseClient, Depends(get_db)],
) -> None:
    """Delete a book by primary key.

    Args:
        book_id (int): Identifier of the book to remove.
        db (AsyncDatabaseClient): Database session from dependency injection.

    Returns:
        None

    Raises:
        HTTPException: If the book does not exist (404) or deletion fails (500).

    """
    books_dao = BookDAO(database_client=db)

    try:
        await books_dao.delete(book_id)
    except NoResultFound as e:
        logger.error(f"Book with ID {book_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found") from e
    except SQLAlchemyError as e:
        logger.exception("Error deleting book", exc_info=e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting book") from e
