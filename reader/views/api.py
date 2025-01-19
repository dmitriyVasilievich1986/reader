from reader.models.main import Book, Author, Category, Page
from typing import Any
from reader import db
from flask_appbuilder.api import ModelRestApi, expose, BaseApi
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.models.sqla.filters import FilterRelationOneToManyEqual
from flask_appbuilder.const import API_RESULT_RES_KEY

class PageModelApi(ModelRestApi):
    resource_name = "Page"
    allow_browser_login = True
    datamodel = SQLAInterface(Page)
    
    show_columns = [
        Page.id.key,
        Page.cover.key,
        Page.position.key,
    ]

    @expose('/book/<pk>/')
    def pages(self, pk: str | int, **kwargs: Any):
        filters = self._base_filters + [FilterRelationOneToManyEqual(Page.book, Book.id, pk)]

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