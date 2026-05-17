"""Pydantic filter model and conversion to SQLAlchemy ``WHERE`` clauses."""

__all__ = ("Filter",)

from datetime import date, datetime
from typing import Any, Literal, Self

from pydantic import BaseModel, Field, model_validator
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import ColumnElement


class Filter[ColumnType: str](BaseModel):
    """Declarative filter triple for paginated or filtered list APIs.

    ``ColumnType`` is typically a string literal union of allowed ORM attribute
    names.

    Supported operators: null checks (``isnull``, ``notnull``); comparisons
    (``eq``, ``ge``, ``gt``, ``le``, ``lt``); membership (``in``); substring
    match (``like``, ``ilike``).
    """

    column: ColumnType = Field(..., description="The column to filter by")
    operator: Literal["isnull", "notnull", "eq", "ge", "gt", "le", "lt", "in", "like", "ilike"] = Field(
        ..., description="The operator to use for the filter"
    )
    value: str | int | list[str | int] | float | date | None = Field(..., description="The value to filter by")

    @model_validator(mode="before")
    @classmethod
    def coerce_iso_date_string_value(cls, data: Any) -> Any:
        """Coerce an ISO ``YYYY-MM-DD`` ``value`` string into a ``date`` before validation.

        Runs only for scalar string values under comparison operators
        (``eq``, ``ge``, ``gt``, ``le``, ``lt``). Pattern (``like``, ``ilike``),
        null (``isnull``, ``notnull``) and membership (``in``) operators keep
        their ``value`` untouched. Strings that do not match the ISO date
        pattern are passed through.

        Args:
            data (Any): Raw input passed to ``Filter(...)``; coercion only
                applies when this is a ``dict``.

        Returns:
            Any: The input (possibly with ``value`` replaced by a ``date``).

        """
        if not isinstance(data, dict):
            return data

        operator = data.get("operator")
        value = data.get("value")
        if operator not in ("eq", "ge", "gt", "le", "lt"):
            return data
        if not isinstance(value, str):
            return data

        try:
            data["value"] = datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            pass

        return data

    @model_validator(mode="after")
    def coerce_iso_date_strings_for_comparison(self) -> Self:
        """Coerce ISO date strings to ``date`` for numeric-style operators.

        Strings matching ``%Y-%m-%d`` become ``date`` objects for ``eq``,
        ``ge``, ``gt``, ``le``, ``lt``, and ``in``. Operators ``like``,
        ``ilike``, ``isnull``, and ``notnull`` leave ``value`` unchanged so
        patterns and null semantics stay intact. Strings that do not match the
        ISO date pattern are left unchanged.

        Returns:
            Self: A copy of the model with a coerced ``value``, or ``self`` if
                no coercion applies.

        Raises:
            ValueError: If ``operator`` is ``in`` but ``value`` is not a list;
                if ``operator`` is not ``in`` but ``value`` is a list; or if
                ``operator`` is ``isnull`` or ``notnull`` but ``value`` is not
                ``None``.

        """
        if self.operator == "in" and not isinstance(self.value, list):
            raise ValueError("Value for 'in' operator must be a list")

        if self.operator != "in" and isinstance(self.value, list):
            raise ValueError(f"Value for '{self.operator}' should not be a list")

        if self.operator in ("isnull", "notnull") and self.value is not None:
            raise ValueError(f"Value for '{self.operator}' should be None")

        if self.operator not in ("isnull", "notnull") and self.value is None:
            raise ValueError(f"Value for '{self.operator}' should not be None")

        if self.operator in ("like", "ilike", "isnull", "notnull"):
            return self

        return self

    def to_sqlalchemy_filter(self, cls: type[DeclarativeBase]) -> ColumnElement[bool]:
        """Build a boolean SQLAlchemy expression for this filter.

        Operators ``isnull`` and ``notnull`` ignore ``value``. Operators ``like``
        and ``ilike`` wrap ``value`` with ``%`` for substring matching.

        Args:
            cls (type[DeclarativeBase]): Declarative model class exposing the
                attribute named by ``column``.

        Returns:
            ColumnElement[bool]: A predicate for ``Query.where()`` or
                ``filter()``.

        Raises:
            ValueError: If ``operator`` is not a supported literal (should not
                occur after successful Pydantic validation).

        """
        column: ColumnElement[Any] = getattr(cls, self.column)

        match self.operator:
            case "isnull":
                return column.is_(None)
            case "notnull":
                return column.isnot(None)
            case "eq":
                return column == self.value
            case "ge":
                return column >= self.value
            case "gt":
                return column > self.value
            case "le":
                return column <= self.value
            case "lt":
                return column < self.value
            case "in":
                return column.in_(self.value)  # type: ignore[arg-type]
            case "like":
                return column.like(f"%{self.value}%")
            case "ilike":
                return column.ilike(f"%{self.value}%")
            case _:
                raise ValueError(f"Invalid operator: {self.operator}")
