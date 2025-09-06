from typing import Any

from flask import Response
from flask_appbuilder.api import expose, ModelRestApi
from flask_appbuilder.const import API_RESULT_RES_KEY
from flask_appbuilder.exceptions import (
    InvalidColumnArgsFABException,
)
from flask_appbuilder.models.sqla.interface import SQLAInterface

from reader.models.main import Author, Book, Category, Page
from reader.views.schemas import BookPageSchema


class PageModelApi(ModelRestApi):
    resource_name = "Page"
    allow_browser_login = True
    datamodel = SQLAInterface(Page)
    order_columns = ["position"]

    show_columns = [
        Page.id.key,
        Page.cover.key,
        Page.position.key,
    ]


class BookModelApi(ModelRestApi):
    resource_name = "book"
    allow_browser_login = True
    datamodel = SQLAInterface(Book)

    show_columns = [
        Book.id.key,
        Book.name.key,
        Book.description.key,
        Book.author.key,
        Book.categories.key,
    ]

    list_columns = [
        Book.id.key,
        Book.name.key,
        Book.cover.key,
        Book.description.key,
        "author_name",
    ]

    @expose("/<pk>/pages")
    def pages(self, pk: str, **kwargs: Any) -> Response:
        response: dict[str, Any] = {}
        args = kwargs.get("rison", {})
        try:
            select_columns, _ = self._handle_columns_args(
                args,
                self.show_select_columns,
                self.show_columns,
            )
        except InvalidColumnArgsFABException as e:
            return self.response_400(message=str(e))

        item: Book = self.datamodel.get(
            pk,
            self._base_filters,
            select_columns,
            self.show_outer_default_load,
        )
        if not item:
            return self.response_404()

        self.set_response_key_mappings(response, self.get, args)

        response["id"] = pk
        response[API_RESULT_RES_KEY] = BookPageSchema().dump(item.pages, many=True)
        return self.response(200, **response)


class CategoryModelApi(ModelRestApi):
    resource_name = "category"
    allow_browser_login = True
    datamodel = SQLAInterface(Category)

    show_columns = [
        Category.id.key,
        Category.name.key,
        Category.description.key,
    ]


class AuthorModelApi(ModelRestApi):
    resource_name = "author"
    allow_browser_login = True
    datamodel = SQLAInterface(Author)

    show_columns = [
        Author.id.key,
        Author.last_name.key,
        Author.first_name.key,
    ]

    list_columns = [
        Author.id.key,
        Author.last_name.key,
        Author.first_name.key,
        "name",
    ]
