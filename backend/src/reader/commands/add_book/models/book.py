"""Pydantic model for a book and its page collection."""

__all__ = ("Book",)

from pathlib import Path

from colorama import Fore, Style
from pydantic import BaseModel, Field

from .page import Page


class Book(BaseModel):
    """Book model with metadata and an ordered list of pages."""

    path: Path = Field(..., description="The path to the book")
    name: str = Field(..., description="The name of the book")
    cover: str = Field(..., description="The cover of the book")
    pages: list[Page] = Field(..., description="The pages of the book")

    def add_page(self, page: Page) -> "Book":
        """Return a copy of the book with an additional page appended.

        Args:
            page (Page): Page to append to the book.

        Returns:
            Book: A new book instance including the added page.

        """
        return self.model_copy(update={"pages": [*self.pages, page]})

    def __add__(self, other: Page) -> "Book":
        """Append a page using the ``+`` operator.

        Args:
            other (Page): Page to add to the book.

        Returns:
            Book: This book instance after the page is added.

        Raises:
            NotImplementedError: If ``other`` is not a ``Page`` instance.

        """
        if not isinstance(other, Page):
            raise NotImplementedError("Can only add Page instance")

        return self.add_page(other)

    def __str__(self) -> str:
        """Return a colored, human-readable summary of the book.

        Returns:
            str: Formatted book name and JSON dump of the model.

        """
        return f"***{Fore.CYAN}{self.name}{Style.RESET_ALL}***\n{self.model_dump_json(indent=2)}"
