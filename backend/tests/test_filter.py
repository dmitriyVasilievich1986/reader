"""Tests for ``reader.utils.filter.Filter``: validation rules, ISO-date coercion, SQL generation."""

from datetime import date
from typing import Literal

import pytest
from pydantic import ValidationError
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from reader.utils.filter import Filter


class _Base(DeclarativeBase):
    pass


class _Item(_Base):
    """Minimal ORM model used only as the column source for filter expressions."""

    __tablename__ = "_filter_test_item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[str | None] = mapped_column(String, nullable=True)


ItemFilter = Filter[Literal["id", "name", "description", "created_at"]]


def _compile(expr) -> str:
    """Render a SQLAlchemy expression as a SQL string with bound literals inlined."""
    return str(expr.compile(compile_kwargs={"literal_binds": True}))


class TestValidation:
    """Operator/value combination rules enforced by the model validator."""

    def test_in_requires_list_value(self) -> None:
        with pytest.raises(ValidationError, match="must be a list"):
            ItemFilter(column="id", operator="in", value=1)

    def test_non_in_rejects_list_value(self) -> None:
        with pytest.raises(ValidationError, match="should not be a list"):
            ItemFilter(column="id", operator="eq", value=[1, 2])

    @pytest.mark.parametrize("op", ["isnull", "notnull"])
    def test_null_operators_require_none_value(self, op: str) -> None:
        with pytest.raises(ValidationError, match="should be None"):
            ItemFilter(column="name", operator=op, value="x")

    @pytest.mark.parametrize(
        "op",
        ["eq", "ge", "gt", "le", "lt", "like", "ilike"],
    )
    def test_value_operators_reject_none(self, op: str) -> None:
        with pytest.raises(ValidationError, match="should not be None"):
            ItemFilter(column="name", operator=op, value=None)

    def test_in_with_empty_list_is_allowed(self) -> None:
        """An empty list is a valid (if useless) ``in`` value — not a None case."""
        f = ItemFilter(column="id", operator="in", value=[])
        assert f.value == []

    def test_invalid_operator_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ItemFilter(column="id", operator="nope", value=1)  # type: ignore[arg-type]

    def test_invalid_column_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ItemFilter(column="not_a_column", operator="eq", value=1)  # type: ignore[arg-type]


class TestIsoDateCoercion:
    """Strings shaped like ``YYYY-MM-DD`` become ``date`` for comparison operators."""

    @pytest.mark.parametrize("op", ["eq", "ge", "gt", "le", "lt"])
    def test_iso_string_is_coerced_for_comparison_operators(self, op: str) -> None:
        f = ItemFilter(column="created_at", operator=op, value="2025-01-18")
        assert f.value == date(2025, 1, 18)
        assert isinstance(f.value, date)

    def test_iso_strings_inside_in_list_are_not_coerced(self) -> None:
        """Coercion only inspects scalar string values, not list elements."""
        f = ItemFilter(column="created_at", operator="in", value=["2025-01-18", "2025-02-01"])
        assert f.value == ["2025-01-18", "2025-02-01"]

    @pytest.mark.parametrize("op", ["like", "ilike"])
    def test_pattern_operators_keep_string_value(self, op: str) -> None:
        """``like`` / ``ilike`` must preserve the raw pattern even if it looks like a date."""
        f = ItemFilter(column="name", operator=op, value="2025-01-18")
        assert f.value == "2025-01-18"

    def test_non_iso_string_is_left_untouched(self) -> None:
        f = ItemFilter(column="name", operator="eq", value="hello")
        assert f.value == "hello"

    def test_integer_value_is_left_untouched(self) -> None:
        f = ItemFilter(column="id", operator="eq", value=42)
        assert f.value == 42


class TestToSqlalchemyFilter:
    """Each operator branch produces the expected SQL fragment."""

    def test_isnull(self) -> None:
        f = ItemFilter(column="description", operator="isnull", value=None)
        assert _compile(f.to_sqlalchemy_filter(_Item)) == (
            "_filter_test_item.description IS NULL"
        )

    def test_notnull(self) -> None:
        f = ItemFilter(column="description", operator="notnull", value=None)
        assert _compile(f.to_sqlalchemy_filter(_Item)) == (
            "_filter_test_item.description IS NOT NULL"
        )

    def test_eq(self) -> None:
        f = ItemFilter(column="id", operator="eq", value=1)
        assert _compile(f.to_sqlalchemy_filter(_Item)) == "_filter_test_item.id = 1"

    def test_ge(self) -> None:
        f = ItemFilter(column="id", operator="ge", value=2)
        assert _compile(f.to_sqlalchemy_filter(_Item)) == "_filter_test_item.id >= 2"

    def test_gt(self) -> None:
        f = ItemFilter(column="id", operator="gt", value=3)
        assert _compile(f.to_sqlalchemy_filter(_Item)) == "_filter_test_item.id > 3"

    def test_le(self) -> None:
        f = ItemFilter(column="id", operator="le", value=4)
        assert _compile(f.to_sqlalchemy_filter(_Item)) == "_filter_test_item.id <= 4"

    def test_lt(self) -> None:
        f = ItemFilter(column="id", operator="lt", value=5)
        assert _compile(f.to_sqlalchemy_filter(_Item)) == "_filter_test_item.id < 5"

    def test_in(self) -> None:
        f = ItemFilter(column="id", operator="in", value=[1, 2, 3])
        sql = _compile(f.to_sqlalchemy_filter(_Item))
        assert sql == "_filter_test_item.id IN (1, 2, 3)"

    def test_like_wraps_value_with_percent_signs(self) -> None:
        f = ItemFilter(column="name", operator="like", value="foo")
        assert _compile(f.to_sqlalchemy_filter(_Item)) == (
            "_filter_test_item.name LIKE '%foo%'"
        )

    def test_ilike_wraps_value_with_percent_signs(self) -> None:
        f = ItemFilter(column="name", operator="ilike", value="bar")
        sql = _compile(f.to_sqlalchemy_filter(_Item))
        assert "'%bar%'" in sql
        assert "lower(_filter_test_item.name)" in sql.lower() or "ILIKE" in sql.upper()

    def test_eq_with_coerced_date_value(self) -> None:
        """ISO-date strings are coerced to ``date`` and render as date literals."""
        f = ItemFilter(column="created_at", operator="eq", value="2025-01-18")
        assert isinstance(f.value, date)
        assert _compile(f.to_sqlalchemy_filter(_Item)) == (
            "_filter_test_item.created_at = '2025-01-18'"
        )
