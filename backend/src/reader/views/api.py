"""Flask-AppBuilder Model REST endpoints for Reader domain models."""

__all__ = ("AuthorModelApi", "BookModelApi", "CategoryModelApi", "PageModelApi")

from typing import Any

from flask_appbuilder.api import expose, ModelRestApi, Response
from flask_appbuilder.const import API_RESULT_RES_KEY
from flask_appbuilder.models.sqla.filters import FilterRelationOneToManyEqual
from flask_appbuilder.models.sqla.interface import SQLAInterface

from reader.models.main import Author, Book, Category, Page


class PageModelApi(ModelRestApi):
    """REST surface exposing ``Page`` rows with optional book-aware routing."""

    resource_name = "Page"
    allow_browser_login = True
    datamodel = SQLAInterface(Page)
    order_columns = ("position",)

    show_columns = (
        Page.id.key,
        Page.cover.key,
        Page.position.key,
    )

    @expose("/book/<pk>/")
    def pages(self, pk: str | int, **kwargs: Any) -> Response:  # noqa: ARG002
        """Respond to nested ``GET /book/<pk>/`` with serialized page payload.

        Args:
            pk (str | int): Identifier from the route, filtered against related
                ``Book`` rows before loading ``Page``.
            kwargs (Any): Additional keyword arguments passed by FAB without
                consuming them locally.

        Returns:
            Response: ``200`` JSON body when data exists or ``404`` otherwise.

        """
        filters = [*self._base_filters, FilterRelationOneToManyEqual(Page.book, Book.id, pk)]

        item = self.datamodel.get(
            pk,
            filters,
            self.show_select_columns,
            self.show_outer_default_load,
        )
        if not item:
            return self.response_404()

        response = {}
        response["id"] = pk
        response[API_RESULT_RES_KEY] = PageModelApi.show_model_schema.dump(item, many=False)

        return self.response(200, message="Hello")


class BookModelApi(ModelRestApi):
    """REST accessors for persisted ``Book`` rows and related presenters."""

    resource_name = "book"
    allow_browser_login = True
    datamodel = SQLAInterface(Book)

    show_columns = (
        Book.id.key,
        Book.name.key,
        Book.description.key,
        Book.author.key,
        Book.categories.key,
    )

    list_columns = (
        Book.id.key,
        Book.name.key,
        Book.cover.key,
        Book.description.key,
        "author_name",
    )


class CategoryModelApi(ModelRestApi):
    """FAB CRUD facade for tagging ``Category`` entries."""

    resource_name = "category"
    allow_browser_login = True
    datamodel = SQLAInterface(Category)

    show_columns = (
        Category.id.key,
        Category.name.key,
        Category.description.key,
    )


class AuthorModelApi(ModelRestApi):
    """FAB CRUD facade for ``Author`` records with readable list views."""

    resource_name = "author"
    allow_browser_login = True
    datamodel = SQLAInterface(Author)

    show_columns = (
        Author.id.key,
        Author.last_name.key,
        Author.first_name.key,
    )

    list_columns = (
        Author.id.key,
        Author.last_name.key,
        Author.first_name.key,
        "name",
    )
