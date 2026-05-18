"""Book model for the database."""

__all__ = ("Book",)

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, DateTimeMixin

if TYPE_CHECKING:
    from .author import Author
    from .category import Category
    from .page import Page


class Book(Base, DateTimeMixin):
    """A published work keyed by ``name`` with author, categories, and pages."""

    __tablename__ = "book"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    cover: Mapped[str | None] = mapped_column(String, nullable=True)
    watches_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("author.id"))
    author: Mapped["Author"] = relationship("Author", back_populates="books")

    categories: Mapped[list["Category"]] = relationship(
        "Category", secondary="category_book_table", back_populates="books"
    )
    pages: Mapped[list["Page"]] = relationship("Page", back_populates="book")

    @property
    def author_name(self) -> str:
        """Return ``Author.name`` for the owning author relation.

        Returns:
            str: Full author name from the linked ``Author``.

        """
        return self.author.name
