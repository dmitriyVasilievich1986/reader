"""Author model for the database."""

__all__ = ("Author",)

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, DateTimeMixin

if TYPE_CHECKING:
    from .book import Book


class Author(Base, DateTimeMixin):
    """A writer credited on one or more books."""

    __tablename__ = "author"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str | None] = mapped_column(String, nullable=True)
    cover: Mapped[str | None] = mapped_column(String, nullable=True)

    books: Mapped[list["Book"]] = relationship("Book", back_populates="author")

    @property
    def name(self) -> str:
        """Return ``first_name`` followed by ``last_name`` separated by one space.

        Returns:
            str: Full author name. If ``last_name`` is not provided, return ``first_name``.

        """
        if self.last_name is None:
            return self.first_name

        return f"{self.first_name} {self.last_name}"
