"""CLI command that imports a book from a filesystem folder into the database."""

__all__ = ("AddBookCommand",)

import json
import re
from pathlib import Path

from loguru import logger

from reader.config import AppConfig
from reader.services.daos import AuthorDAO, BookDAO, PageDAO
from reader.services.database import AsyncDatabaseClient

from ..base import BaseCommand


class AddBookCommand(BaseCommand):
    """Load book images under ``book_path`` and persist author, book, and pages.

    The parent directory name optionally encodes ``author_first_name``
    ``author_last_name`` as ``first_last`` segments separated by underscores.
    """

    author_first_name: str | None = None
    author_last_name: str | None = None
    book_name: str | None = None
    file_extensions: tuple[str, ...] = (".jpg", ".jpeg", ".png")

    def __init__(self, book_path: Path | str, app_config: AppConfig | None = None, static_url: str = "/static/images"):
        """Create an import command for the given book folder.

        Args:
            book_path (Path | str): Directory containing page images (.jpg/.jpeg/.png).
            app_config (AppConfig, optional): Database and app configuration.
                Defaults to ``AppConfig.get_or_create()`` when omitted.
            static_url (str, optional): The URL prefix for static files.
                Defaults to ``/static/images``.

        Returns:
            None

        """
        self.book_path = Path(book_path)
        self.app_config = app_config or AppConfig.get_or_create()
        self.static_url = static_url

    def _book_structure(
        self, book_cover: str | None = None, pages: list[str] | None = None
    ) -> dict[str, Path | str | list[str]]:
        """Build a JSON-serializable summary of detected book metadata.

        Args:
            book_cover (str, optional): Representative cover URL or path fragment.
                Defaults to None (omitted from the payload).
            pages (list[str], optional): Sorted page identifiers. Defaults to None
                (omitted from the payload).

        Returns:
            dict[str, Path | str | list[str]]: Keys such as ``Book path``, names, and optional ``Book cover``
            / ``Pages``. Values may include non-string objects coerced via ``json.dumps``.

        """
        payload = {
            "Book path": self.book_path,
            "Author first name": self.author_first_name,
            "Author last name": self.author_last_name,
            "Author full name": self.author_full_name,
            "Book name": self.book_name,
        }
        if book_cover is not None:
            payload["Book cover"] = book_cover
        if pages is not None:
            payload["Pages"] = pages  # type: ignore[assignment]

        return payload  # type: ignore[return-value]

    def __str__(self) -> str:
        """Return indented JSON describing the command state.

        Returns:
            str: JSON text for the default book-structure payload without cover/pages.

        """
        return json.dumps(self._book_structure(), indent=2, default=str)

    @property
    def author_full_name(self) -> str:
        """Compose a display name from first and optional last author name.

        Returns:
            str: ``first_only`` when last name is absent, otherwise ``first last``.

        """
        if self.author_last_name is None:
            return self.author_first_name  # type: ignore[return-value]

        return f"{self.author_first_name} {self.author_last_name}"

    async def initialize(self, **kwargs):
        """Initialize the command.

        Args:
            **kwargs: Unused keyword arguments retained for ``BaseCommand`` compatibility.

        Returns:
            None

        """
        pass

    async def validate(self):
        """Ensure ``book_path`` layout and derive ``book_name`` and author fields.

        Returns:
            None

        Raises:
            ValueError: If ``book_path`` or its parent is missing or not a directory,
                if no image pages exist inside ``book_path``, or if the parent folder
                name has more than two underscore-separated segments.

        """
        if not self.book_path.exists():
            raise ValueError(f"Book path {self.book_path} does not exist")
        if not self.book_path.is_dir():
            raise ValueError(f"Book path {self.book_path} is not a directory")
        if not (parent_folder := self.book_path.parent).is_dir():
            raise ValueError(f"Parent folder {parent_folder} is not a directory")
        for item in self.book_path.iterdir():
            if item.is_file() and item.suffix in self.file_extensions:
                break
        else:
            raise ValueError(f"Book path {self.book_path} does not contain any image files")

        self.book_name = re.sub(r"_|\s+", " ", self.book_path.name.capitalize())

        if len(parent_splited := parent_folder.name.split("_")) > 2:
            raise ValueError(f"Parent folder {parent_folder} has more than 2 parts")

        if len(parent_splited) == 2:
            self.author_first_name = parent_splited[0]
            self.author_last_name = parent_splited[1]
        elif len(parent_splited) == 1:
            self.author_first_name = parent_splited[0]

    async def execute(self):
        """Create author, book, and page rows and print a JSON summary to stdout.

        Page paths are stored as ``{self.static_url}/{grandparent}/{parent}/{filename}`` relative-style
        strings derived from the image files in ``book_path``.

        Returns:
            None

        """
        logger.info(f"Adding book {self.book_path}...")
        db_client = AsyncDatabaseClient(self.app_config)
        pages: list[str] = []

        for item in self.book_path.iterdir():
            if item.is_file() and item.suffix in self.file_extensions:
                pages.append(f"{self.static_url}/{item.parent.parent.name}/{item.parent.name}/{item.name}")

        pages.sort()

        async with db_client.session_factory() as session:
            book_dao = BookDAO(database_client=None, session=session)
            author_dao = AuthorDAO(database_client=None, session=session)
            page_dao = PageDAO(database_client=None, session=session)

            author = await author_dao.create(
                first_name=self.author_first_name, last_name=self.author_last_name, cover=None
            )
            book = await book_dao.create(name=self.book_name, author_id=author.id, cover=pages[0])
            for index, page in enumerate(pages, start=1):
                await page_dao.create(book_id=book.id, position=index, cover=page)

        logger.info(json.dumps(self._book_structure(book_cover=pages[0], pages=pages), indent=2, default=str))
