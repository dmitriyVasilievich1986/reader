"""Tests specific to ``BookDAO`` (eager-loaded ``author``, ``categories``, ``pages``)."""

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
        """Write through one session, then read through a fresh one to bypass the identity map."""
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
        authors = AuthorDAO(session=session)
        books = BookDAO(session=session)

        author = await authors.create(first_name="George", last_name="Orwell")
        book = await books.create(name="1984", author_id=author.id)

        fetched = await books.get_by_pk(book.id)
        assert fetched.author_name == "George Orwell"

    async def test_get_all_returns_books_without_relations_loaded(
        self, session: AsyncSession,
    ) -> None:
        authors = AuthorDAO(session=session)
        books = BookDAO(session=session)

        author = await authors.create(first_name="A")
        await books.create(name="Alpha", author_id=author.id)
        await books.create(name="Beta", author_id=author.id)

        rows, total = await books.get_all(sort_by="name")
        assert total == 2
        assert [r.name for r in rows] == ["Alpha", "Beta"]
