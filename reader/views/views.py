from typing import override

from flask_appbuilder import BaseView, expose, IndexView
from flask_appbuilder.security.decorators import has_access


class ReaderIndexView(IndexView):
    index_template = "index.html"

    @expose("/")
    @has_access
    @override
    def index(self) -> str:
        return self.render_template(self.index_template, appbuilder=self.appbuilder)


class BookView(BaseView):
    default_view = "book_view"
    route_base = "/book"

    @expose("/")
    @expose("/<string:pk>/")
    @has_access
    def book_view(
        self,
        pk: str | int | None = None,  # pylint: disable=unused-argument
    ) -> str:
        """
        Renders the index.html template with the given appbuilder object.

        Args:
            pk (str | int | None): The primary key of the password (optional).

        Returns:
            str: The rendered template as a string.
        """

        return self.render_template("index.html", appbuilder=self.appbuilder)
