"""Page model for the database."""

__all__ = ("Page",)

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .book import Book

class Page(Base):
    """An ordered image reference belonging to exactly one ``Book``."""

    __tablename__ = "page"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    cover: Mapped[str | None] = mapped_column(String, nullable=True)

    book_id: Mapped[int] = mapped_column(Integer, ForeignKey("book.id"))
    book: Mapped["Book"] = relationship("Book", backref="pages")