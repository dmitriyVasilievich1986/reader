"""DAO for the Author model."""

__all__ = ("AuthorDAO",)

from reader.services.database.models.author import Author

from .base import BaseDAO


class AuthorDAO(BaseDAO[Author]):
    """DAO for the Author model."""

    database_model = Author
    get_all_columns = (
        Author.id,
        Author.first_name,
        Author.last_name,
        Author.cover,
        Author.created_at,
        Author.updated_at,
    )
    select_in_options_single = (Author.books,)
