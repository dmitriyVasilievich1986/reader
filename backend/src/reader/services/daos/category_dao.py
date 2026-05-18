"""DAO for the Category model."""

__all__ = ("CategoryDAO",)

from reader.services.database.models.category import Category

from .base import BaseDAO


class CategoryDAO(BaseDAO[Category]):
    """DAO for the Category model."""

    database_model = Category
    get_all_columns = (
        Category.id,
        Category.name,
        Category.description,
        Category.cover,
        Category.created_at,
        Category.updated_at,
    )
    select_in_options_single = (Category.books,)
