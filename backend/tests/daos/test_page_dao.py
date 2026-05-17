"""Tests specific to ``PageDAO`` (eager-loaded ``book`` on single-row reads)."""

from sqlalchemy.ext.asyncio import AsyncSession

from reader.services.daos import AuthorDAO, BookDAO, PageDAO


class TestPageDAO:
    """The Page DAO exposes the parent ``book`` as a single-row eager option."""

    async def test_get_by_pk_eagerly_loads_book(self, session: AsyncSession) -> None:
        authors = AuthorDAO(session=session)
        books = BookDAO(session=session)
        pages = PageDAO(session=session)

        author = await authors.create(first_name="Author")
        book = await books.create(name="The Book", author_id=author.id)
        page = await pages.create(position=42, book_id=book.id)

        fetched = await pages.get_by_pk(page.id)
        assert fetched.book.id == book.id
        assert fetched.book.name == "The Book"
        assert fetched.position == 42

    async def test_get_all_filters_by_book_id(self, session: AsyncSession) -> None:
        authors = AuthorDAO(session=session)
        books = BookDAO(session=session)
        pages = PageDAO(session=session)

        author = await authors.create(first_name="Author")
        book_a = await books.create(name="A", author_id=author.id)
        book_b = await books.create(name="B", author_id=author.id)

        await pages.create(position=1, book_id=book_a.id)
        await pages.create(position=2, book_id=book_a.id)
        await pages.create(position=1, book_id=book_b.id)

        rows, total = await pages.get_all(
            filters=[{"column": "book_id", "operator": "eq", "value": book_a.id}],
            sort_by="position",
        )
        assert total == 2
        assert [r.position for r in rows] == [1, 2]
        assert all(r.book_id == book_a.id for r in rows)
