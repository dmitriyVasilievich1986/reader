"""DAO for the Page model."""

__all__ = ("PageDAO",)

from reader.services.database.models.page import Page

from .base import BaseDAO


class PageDAO(BaseDAO[Page]):
    """DAO for the Page model."""

    database_model = Page
    get_all_columns = (Page.id, Page.position, Page.cover, Page.book_id)
    select_in_options_single = (Page.book,)
