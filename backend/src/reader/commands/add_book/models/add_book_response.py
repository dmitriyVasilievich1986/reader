"""Response container for books added for an author, with database persistence."""

__all__ = ("AddBookResponse",)

import pydash
from loguru import logger

from reader.services.daos import AuthorDAO, BookDAO, PageDAO
from reader.services.database import AsyncDatabaseClient
from reader.services.database.models import Author as AuthorModel

from .author import Author
from .book import Book


class AddBookResponse:
    """Collects parsed books for an author and persists them to the database."""

    def __init__(self, db_client: AsyncDatabaseClient, author: Author) -> None:
        """Initialize the response with a database client and author.

        Args:
            db_client (AsyncDatabaseClient): Client used to open database sessions.
            author (Author): Author associated with the books in this response.

        Returns:
            None

        """
        self.db_client = db_client
        self.books: list[Book] = []
        self.author = author

    def add_book(self, book: Book) -> None:
        """Append a book to the in-memory collection.

        Args:
            book (Book): Parsed book to add.

        Returns:
            None

        """
        self.books.append(book)

    def __add__(self, other: Book) -> "AddBookResponse":
        """Append a book using the ``+`` operator.

        Args:
            other (Book): Book to add to the response.

        Returns:
            AddBookResponse: This response instance after the book is added.

        Raises:
            NotImplementedError: If ``other`` is not a ``Book`` instance.

        """
        if not isinstance(other, Book):
            raise NotImplementedError("Can only add Book instance")

        self.add_book(other)
        return self

    def __getitem__(self, name: str) -> Book:
        """Return a book by its name.

        Args:
            name (str): Name of the book to look up.

        Returns:
            Book: The book matching ``name``.

        Raises:
            KeyError: If no book with the given name exists.

        """
        payload = pydash.find(self.books, lambda book: book.name == name)
        if payload is None:
            raise KeyError(f"Book {name} not found")

        return payload

    def __str__(self) -> str:
        """Return a human-readable summary of the author and books.

        Returns:
            str: JSON dump of the author followed by each book's string form.

        """
        books = "\n".join(str(book) for book in self.books)
        return f"{self.author.model_dump_json(indent=2)}\n{books}"

    async def _save_book(self, book_to_save: Book, author: AuthorModel) -> None:
        """Persist a single book and its pages within a database session.

        Args:
            book_to_save (Book): Parsed book to write to the database.
            author (AuthorModel): Persisted author record owning the book.

        Returns:
            None

        """
        logger.info(f"Saving book: {book_to_save.name}")
        async with self.db_client.session_factory() as session:
            book_dao = BookDAO(database_client=None, session=session)
            page_dao = PageDAO(database_client=None, session=session)

            book = await book_dao.create(name=book_to_save.name, author_id=author.id, cover=book_to_save.cover)
            for page in book_to_save.pages:
                await page_dao.create(book_id=book.id, position=page.position, cover=page.cover)

    async def _save_author(self) -> AuthorModel:
        """Find an existing author or create a new one.

        Returns:
            AuthorModel: The matched or newly created author record.

        Raises:
            ValueError: If more than one author matches the configured name.

        """
        logger.info(f"Saving author: {self.author.first_name} {self.author.last_name}")
        author_filters = [
            AuthorModel.first_name == self.author.first_name,
            AuthorModel.last_name == self.author.last_name,
        ]
        author_dao = AuthorDAO(database_client=self.db_client, session=None)

        author, _ = await author_dao.get_all(filters=author_filters)
        if len(author) > 1:
            raise ValueError(f"Multiple authors found for {self.author.first_name} {self.author.last_name}")
        if len(author) == 0:
            return await author_dao.create(
                first_name=self.author.first_name, last_name=self.author.last_name, cover=None
            )

        return author[0]

    async def save(self) -> None:
        """Persist the author and all collected books to the database.

        Returns:
            None

        """
        logger.info("Starting to save author and books...")
        logger.debug(f"Data to save: {self}")
        author = await self._save_author()

        for book in self.books:
            await self._save_book(book, author)

        logger.info("Author and books saved successfully")
