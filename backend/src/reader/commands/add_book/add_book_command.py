"""CLI command that imports a book from a filesystem folder into the database."""

__all__ = ("AddBookCommand",)

import re
from pathlib import Path

from loguru import logger
from sqlalchemy.exc import NoResultFound

from reader.config import AppConfig
from reader.services.daos import BookDAO
from reader.services.database import AsyncDatabaseClient

from ..base import BaseCommand
from .models import AddBookResponse, Author, Book, Page


class AddBookCommand(BaseCommand[AddBookResponse]):
    """Import books from an author folder on disk into the database."""

    file_extensions: tuple[str, ...] = (".jpg", ".jpeg", ".png")

    def __init__(
        self, author_path: Path | str, app_config: AppConfig | None = None, static_url: str = "/static/images"
    ):
        """Configure the command for a given author directory.

        Args:
            author_path (Path | str): Filesystem path to the author folder
                containing one subdirectory per book.
            app_config (AppConfig | None, optional): Application configuration
                used to create the database client. Defaults to a new or
                cached ``AppConfig`` instance.
            static_url (str, optional): Base URL prefix for page cover paths.
                Defaults to ``"/static/images"``.

        """
        self.author_path = Path(author_path)
        self.static_url = static_url.strip().rstrip("/")

        app_config = app_config or AppConfig.get_or_create()
        self.db_client = AsyncDatabaseClient(app_config)

    async def initialize(self, **kwargs):
        """Initialize the command.

        Args:
            **kwargs: Unused keyword arguments retained for ``BaseCommand`` compatibility.

        Returns:
            None

        """
        pass

    async def validate(self):
        """Verify the author folder layout and that books are not duplicates.

        Returns:
            None

        Raises:
            ValueError: If the author path is missing, malformed, contains
                non-directory entries, includes duplicate book names, has
                invalid page files, or contains a book with no pages.

        """
        if not self.author_path.exists():
            raise ValueError(f"Author path {self.author_path} does not exist")
        if len(self.author_path.name.split("_")) > 2:
            raise ValueError(f"Author path {self.author_path} has more than 2 parts")

        book_dao = BookDAO(database_client=self.db_client, session=None)
        for book_path in self.author_path.iterdir():
            if not book_path.is_dir():
                raise ValueError(f"Book path {book_path} is not a directory")
            try:
                book_name = book_path.name.replace("_", " ").capitalize()
                _ = await book_dao.get_by_pk(book_name, "name")
            except NoResultFound:
                pass
            else:
                raise ValueError(f"Book {book_name} already exists, path - {book_path}")

            if not book_path.is_dir():
                raise ValueError(f"Book path {book_path} is not a directory")

            count = 0
            for page_path in book_path.iterdir():
                count += 1
                if not page_path.is_file() or page_path.suffix not in self.file_extensions:
                    raise ValueError(f"Page path {page_path} is not a file or does not have a valid extension")
                if re.search(r"\d+", page_path.name) is None:
                    raise ValueError(f"Page path {page_path} does not have a valid number in the name")

            if count == 0:
                raise ValueError(f"Book path {book_path} does not contain any pages")

    async def execute(self) -> AddBookResponse:
        """Parse author and book folders into an ``AddBookResponse``.

        Returns:
            AddBookResponse: Parsed author metadata and books with ordered
                pages, ready to be persisted.

        """
        logger.info(f"Executing add book command for author: {self.author_path}")
        author_name_splited = self.author_path.name.split("_")
        if len(author_name_splited) == 1:
            author = Author(first_name=author_name_splited[0], last_name=None)
        elif len(author_name_splited) == 2:
            author = Author(first_name=author_name_splited[0], last_name=author_name_splited[1])

        response = AddBookResponse(db_client=self.db_client, author=author)
        for book_path in self.author_path.iterdir():
            pages_pathes: list[Path] = sorted(
                list(book_path.iterdir()),
                key=lambda x: int(re.search(r"\d+", x.name).group(0)),  # type: ignore[union-attr]
            )
            pages = [
                Page(
                    path=page_path,
                    position=index,
                    cover=f"{self.static_url}/{page_path.parent.parent.name}/{page_path.parent.name}/{page_path.name}",
                )
                for index, page_path in enumerate(pages_pathes, start=1)
            ]
            book = Book(
                path=book_path, name=book_path.name.replace("_", " ").capitalize(), cover=pages[0].cover, pages=pages
            )
            response += book

        logger.info(f"Add book command executed successfully for author: {self.author_path}")
        return response
