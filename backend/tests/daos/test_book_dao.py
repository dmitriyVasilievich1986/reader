"""Tests for ``BookDAO`` behaviours around relationship loading.

Covers eager loads on ``get_by_pk`` (``author``, ``categories``, ``pages``),
the ``author_name`` convenience accessor, and list queries that omit full graph
loads. Uses migrated SQLite fixtures from ``daos.conftest``.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from reader.services.daos import AuthorDAO, BookDAO, CategoryDAO, PageDAO
from reader.services.database import AsyncDatabaseClient
from reader.services.database.models.category_book_table import CategoryBookTable


class TestBookDAO:
    """The Book DAO eagerly loads author, categories, and pages on single-row reads."""

    async def test_get_by_pk_eagerly_loads_all_relations(
        self,
        session: AsyncSession,
        db_client: AsyncDatabaseClient,
    ) -> None:
        """Hydrate ``author``, ``categories``, and ``pages`` after a pk fetch in new session.

        Persist graph data in one ``AsyncSession``, then reload the book via a factory
        session so behaviour is observable outside the identity map.

        Args:
            session (AsyncSession): Write session from ``daos.session`` fixture.
            db_client (AsyncDatabaseClient): Factory for isolated read ``AsyncSession``.

        Returns:
            None

        """
        write_authors = AuthorDAO(session=session)
        write_categories = CategoryDAO(session=session)
        write_books = BookDAO(session=session)
        write_pages = PageDAO(session=session)

        author = await write_authors.create(first_name="Frank", last_name="Herbert")
        sci_fi = await write_categories.create(name="Sci-Fi")
        epic = await write_categories.create(name="Epic")
        book = await write_books.create(name="Dune", author_id=author.id)

        session.add(CategoryBookTable(book_id=book.id, category_id=sci_fi.id))
        session.add(CategoryBookTable(book_id=book.id, category_id=epic.id))
        await session.commit()

        await write_pages.create(position=1, book_id=book.id)
        await write_pages.create(position=2, book_id=book.id)

        async with db_client.session_factory() as read_session:
            read_books = BookDAO(session=read_session)
            fetched = await read_books.get_by_pk(book.id)
            assert fetched.author.id == author.id
            assert {c.name for c in fetched.categories} == {"Sci-Fi", "Epic"}
            assert sorted(p.position for p in fetched.pages) == [1, 2]

    async def test_author_name_property(self, session: AsyncSession) -> None:
        """Expose concatenated ``first_name`` / ``last_name`` from related author.

        Args:
            session (AsyncSession): Migrated-database session under test.

        Returns:
            None

        """
        authors = AuthorDAO(session=session)
        books = BookDAO(session=session)

        author = await authors.create(first_name="George", last_name="Orwell")
        book = await books.create(name="1984", author_id=author.id)

        fetched = await books.get_by_pk(book.id)
        assert fetched.author_name == "George Orwell"

    async def test_get_all_returns_books_without_relations_loaded(
        self,
        session: AsyncSession,
    ) -> None:
        """List books with stable sorting while avoiding heavy relationship payloads.

        Args:
            session (AsyncSession): Migrated-database session under test.

        Returns:
            None

        """
        authors = AuthorDAO(session=session)
        books = BookDAO(session=session)

        author = await authors.create(first_name="A")
        await books.create(name="Alpha", author_id=author.id)
        await books.create(name="Beta", author_id=author.id)

        rows, total = await books.get_all(sort_by="name")
        assert total == 2
        assert [r.name for r in rows] == ["Alpha", "Beta"]
