"""DAO for the Book model."""

__all__ = ("BookDAO",)

from reader.services.database.models.book import Book

from .base import BaseDAO


class BookDAO(BaseDAO[Book]):
    """DAO for the Book model."""

    database_model = Book
    get_all_columns = (Book.id, Book.name, Book.description, Book.cover, Book.author_id)
    select_in_options_single = (Book.author, Book.categories, Book.pages)
