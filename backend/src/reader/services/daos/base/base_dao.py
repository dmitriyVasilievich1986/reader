"""Base async DAO for SQLAlchemy models using a session or database client."""

__all__ = ("BaseDAO",)

from abc import ABC
from typing import Any, Literal, overload, Sequence

from sqlalchemy import asc, desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only, selectinload
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql import ColumnElement

from reader.services.database import AsyncDatabaseClient
from reader.services.database.models.base import Base
from reader.utils import Filter


class BaseDAO[DatabaseModel: Base](ABC):
    """Abstract async data-access layer for one SQLAlchemy declarative model."""

    pk_column_name: str = "id"
    database_model: type[DatabaseModel]

    get_all_columns: tuple[InstrumentedAttribute, ...] | None = None
    select_in_options_single: tuple[InstrumentedAttribute, ...] | None = None
    select_in_options_all: tuple[InstrumentedAttribute, ...] | None = None
    base_filters: list[ColumnElement[bool]] | None = None

    @overload
    def __init__(
        self,
        database_client: AsyncDatabaseClient,
        session: None = None,
        **_: Any,
    ) -> None: ...

    @overload
    def __init__(
        self,
        database_client: None,
        session: AsyncSession,
        **_: Any,
    ) -> None: ...

    def __init__(
        self,
        database_client: AsyncDatabaseClient | None = None,
        session: AsyncSession | None = None,
        **_: Any,
    ) -> None:
        """Initialize the DAO with either a shared session or a database client.

        Args:
            database_client (AsyncDatabaseClient | None, optional): Opens
                short-lived sessions when ``session`` is omitted. Defaults to
                None.
            session (AsyncSession | None, optional): Reused async session for
                all operations. Defaults to None.
            **_ (Any): Ignored keyword arguments for subclass constructors.

        Raises:
            ValueError: If both ``database_client`` and ``session`` are None.

        Returns:
            None

        """
        if database_client is None and session is None:
            raise ValueError("Either database_client or session must be provided")

        self.database_client = database_client
        self.session = session

    def concat_filters(
        self, filters: list[ColumnElement[bool]] | list[dict[str, Any]] | None
    ) -> list[ColumnElement[bool]]:
        """Return ``base_filters`` followed by optional caller filters.

        Args:
            filters (list[ColumnElement[bool]] | list[dict[str, Any]] | None, optional): Extra WHERE
                predicates. Defaults to None.

        Returns:
            list[ColumnElement[bool]]: Combined filter list, never None.

        """
        if filters is None:
            return [*(self.base_filters or [])]

        filters_: list[ColumnElement[bool]] = []
        for f in filters:
            if isinstance(f, dict):
                filter_: Filter[str] = Filter.model_validate(f)
                filters_.append(filter_.to_sqlalchemy_filter(self.database_model))
            else:
                filters_.append(f)

        return [*(self.base_filters or []), *filters_]

    async def _get_by_pk_raw(
        self,
        session: AsyncSession,
        pk: int | str,
        pk_column_name: str,
        filters: list[ColumnElement[bool]] | list[dict[str, Any]] | None = None,
    ) -> DatabaseModel:
        """Load one model row by primary key using the given session.

        Args:
            session (AsyncSession): Active async session.
            pk (int | str): Primary key value.
            pk_column_name (str): Attribute name of the PK column on the model.
            filters (list[ColumnElement[bool]] | list[dict[str, Any]] | None, optional): Extra WHERE
                clauses merged with ``base_filters``. Defaults to None.

        Returns:
            DatabaseModel: The matching ORM instance.

        """
        stmt = select(self.database_model).where(getattr(self.database_model, pk_column_name) == pk)

        if c_filters := self.concat_filters(filters):
            stmt = stmt.where(*c_filters)

        if self.select_in_options_single:
            stmt = stmt.options(*map(selectinload, self.select_in_options_single))

        result = await session.execute(stmt)
        return result.scalar_one()

    async def get_by_pk(
        self,
        pk: int | str,
        pk_column_name: str | None = None,
        filters: list[ColumnElement[bool]] | list[dict[str, Any]] | None = None,
    ) -> DatabaseModel:
        """Load one row by primary key using injected or factory-opened session.

        Args:
            pk (int | str): Primary key value.
            pk_column_name (str | None, optional): PK column attribute name.
                Defaults to ``self.pk_column_name``.
            filters (list[ColumnElement[bool]] | list[dict[str, Any]] | None, optional): Extra WHERE
                clauses. Defaults to None.

        Returns:
            DatabaseModel: The matching ORM instance.

        """
        pk_column_name = pk_column_name or self.pk_column_name

        if self.session is not None:
            return await self._get_by_pk_raw(self.session, pk, pk_column_name, filters)

        async with self.database_client.session_factory() as session:  # type: ignore[union-attr]
            return await self._get_by_pk_raw(session, pk, pk_column_name, filters)

    async def _get_total_raw(
        self, session: AsyncSession, filters: list[ColumnElement[bool]] | list[dict[str, Any]] | None = None
    ) -> int:
        """Count rows for this model with optional filters.

        Args:
            session (AsyncSession): Active async session.
            filters (list[ColumnElement[bool]] | list[dict[str, Any]] | None, optional): Extra WHERE
                clauses. Defaults to None.

        Returns:
            int: Number of matching rows.

        """
        stmt = select(func.count()).select_from(self.database_model)

        if c_filters := self.concat_filters(filters):
            stmt = stmt.where(*c_filters)

        result = await session.execute(stmt)
        return result.scalar_one()

    async def get_total(self, filters: list[ColumnElement[bool]] | list[dict[str, Any]] | None = None) -> int:
        """Return the row count for this model with optional filters.

        Args:
            filters (list[ColumnElement[bool]] | list[dict[str, Any]] | None, optional): Extra WHERE
                clauses. Defaults to None.

        Returns:
            int: Number of matching rows.

        """
        if self.session is not None:
            return await self._get_total_raw(self.session, filters)

        async with self.database_client.session_factory() as session:  # type: ignore[union-attr]
            return await self._get_total_raw(session, filters)

    async def _get_all_raw(
        self,
        session: AsyncSession,
        limit: int | None,
        offset: int | None,
        sort_by: str | None,
        sort_order: Literal["asc", "desc"],
        filters: list[ColumnElement[bool]] | list[dict[str, Any]] | None,
    ) -> tuple[Sequence[DatabaseModel], int]:
        """List rows with pagination, sorting, eager loads, and total count.

        Args:
            session (AsyncSession): Active async session.
            limit (int | None): Maximum rows to return.
            offset (int | None): Number of rows to skip.
            sort_by (str | None): Model attribute name to order by, or None.
            sort_order (Literal["asc", "desc"]): Sort direction.
            filters (list[ColumnElement[bool]] | list[dict[str, Any]] | None): Extra WHERE clauses.

        Returns:
            tuple[Sequence[DatabaseModel], int]: Page of instances and total count
                for the same filter set.

        """
        stmt = select(self.database_model)

        if sort_by:
            order_func = asc if sort_order == "asc" else desc
            stmt = stmt.order_by(order_func(getattr(self.database_model, sort_by)))

        if self.get_all_columns:
            stmt = stmt.options(load_only(*self.get_all_columns))

        if self.select_in_options_all:
            stmt = stmt.options(*map(selectinload, self.select_in_options_all))

        if limit:
            stmt = stmt.limit(limit)
        if offset:
            stmt = stmt.offset(offset)
        if c_filters := self.concat_filters(filters):
            stmt = stmt.where(*c_filters)

        total = await self._get_total_raw(session, filters)
        result = await session.execute(stmt)
        return result.scalars().all(), total

    async def get_all(
        self,
        limit: int | None = 100,
        offset: int | None = 0,
        sort_by: str = "id",
        sort_order: Literal["asc", "desc"] = "asc",
        filters: list[ColumnElement[bool]] | list[dict[str, Any]] | None = None,
    ) -> tuple[Sequence[DatabaseModel], int]:
        """List rows with pagination and return the filtered total count.

        Args:
            limit (int | None, optional): Max rows. Defaults to 100.
            offset (int | None, optional): Rows to skip. Defaults to 0.
            sort_by (str, optional): Model attribute for ORDER BY. Defaults to
                "id".
            sort_order (Literal["asc", "desc"], optional): Sort direction.
                Defaults to "asc".
            filters (list[ColumnElement[bool]] | list[dict[str, Any]] | None, optional): Extra WHERE
                clauses. Defaults to None.

        Returns:
            tuple[Sequence[DatabaseModel], int]: Page of instances and total count.

        """
        if self.session is not None:
            return await self._get_all_raw(self.session, limit, offset, sort_by, sort_order, filters)

        async with self.database_client.session_factory() as session:  # type: ignore[union-attr]
            return await self._get_all_raw(session, limit, offset, sort_by, sort_order, filters)

    async def _create_raw(self, session: AsyncSession, **kwargs) -> DatabaseModel:
        """Insert a row and return the persisted instance loaded by PK.

        Args:
            session (AsyncSession): Active async session.
            **kwargs: Column values accepted by ``database_model``.

        Returns:
            DatabaseModel: The created row after commit and reload.

        """
        obj = self.database_model(**kwargs)
        session.add(obj)
        await session.commit()
        return await self._get_by_pk_raw(session, getattr(obj, self.pk_column_name), self.pk_column_name)

    async def create(self, **kwargs) -> DatabaseModel:
        """Create a row from keyword arguments matching the model fields."""
        if self.session is not None:
            return await self._create_raw(self.session, **kwargs)

        async with self.database_client.session_factory() as session:  # type: ignore[union-attr]
            return await self._create_raw(session, **kwargs)

    async def _update_raw(
        self, session: AsyncSession, pk: int | str, pk_column_name: str, **kwargs: Any
    ) -> DatabaseModel:
        """Update columns for the row identified by primary key and reload it.

        Args:
            session (AsyncSession): Active async session.
            pk (int | str): Primary key value.
            pk_column_name (str): Attribute name of the PK column on the model.
            **kwargs (Any): Column names and new values to persist.

        Returns:
            DatabaseModel: The updated row after commit and reload.

        """
        if not kwargs:
            return await self._get_by_pk_raw(session, pk, pk_column_name)

        await session.execute(
            update(self.database_model).where(getattr(self.database_model, pk_column_name) == pk).values(**kwargs)
        )
        await session.commit()

        return await self._get_by_pk_raw(session, pk, pk_column_name)

    async def update(self, pk: int | str, pk_column_name: str | None = None, **kwargs: Any) -> DatabaseModel:
        """Update a row by primary key and return the reloaded instance.

        Args:
            pk (int | str): Primary key value.
            pk_column_name (str | None, optional): PK column attribute name.
                Defaults to ``self.pk_column_name``.
            **kwargs (Any): Column names and new values to persist.

        Returns:
            DatabaseModel: The updated row after commit and reload.

        """
        col = pk_column_name or self.pk_column_name
        if self.session is not None:
            return await self._update_raw(self.session, pk, col, **kwargs)

        async with self.database_client.session_factory() as session:  # type: ignore[union-attr]
            return await self._update_raw(session, pk, col, **kwargs)

    async def _delete_raw(
        self, session: AsyncSession, pk: int | str, pk_column_name: str, instance: DatabaseModel | None
    ) -> bool:
        """Delete a row by instance or by primary key lookup.

        Args:
            session (AsyncSession): Active async session.
            pk (int | str): Primary key value when ``instance`` is omitted.
            pk_column_name (str): Attribute name of the PK column on the model.
            instance (DatabaseModel | None, optional): Existing ORM instance to
                delete. Defaults to None.

        Returns:
            bool: True after successful commit.

        """
        instance = instance or await self._get_by_pk_raw(session, pk, pk_column_name)
        await session.delete(instance)
        await session.commit()
        return True

    async def delete(
        self, pk: int | str, pk_column_name: str | None = None, instance: DatabaseModel | None = None
    ) -> bool:
        """Delete a row by primary key or by passing a loaded instance.

        Args:
            pk (int | str): Primary key value when ``instance`` is omitted.
            pk_column_name (str | None, optional): PK column attribute name.
                Defaults to ``self.pk_column_name``.
            instance (DatabaseModel | None, optional): Row to delete without
                reloading. Defaults to None.

        Returns:
            bool: True after successful commit.

        """
        col = pk_column_name or self.pk_column_name
        if self.session is not None:
            return await self._delete_raw(self.session, pk, col, instance)

        async with self.database_client.session_factory() as session:  # type: ignore[union-attr]
            return await self._delete_raw(session, pk, col, instance)
