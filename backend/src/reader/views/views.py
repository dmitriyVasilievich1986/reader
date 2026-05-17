"""Flask-AppBuilder markup views powering the Reader web UI."""

__all__ = ("BookView", "ReaderIndexView")

from typing import override

from flask_appbuilder import BaseView, expose, IndexView
from flask_appbuilder.security.decorators import has_access


class ReaderIndexView(IndexView):
    """FAB index route that emits the SPA shell."""

    index_template = "index.html"

    @expose("/")
    @has_access
    @override
    def index(self) -> str:
        """Render ``index_template`` registered on this ``IndexView``.

        Returns:
            str: HTML output passed through ``render_template``.

        """
        return self.render_template(self.index_template, appbuilder=self.appbuilder)


class BookView(BaseView):
    """Route bundle under ``/book`` that reuses the SPA shell markup."""

    default_view = "book_view"
    route_base = "/book"

    @expose("/")
    @expose("/<string:pk>/")
    @has_access
    def book_view(
        self,
        pk: str | int | None = None,  # pylint: disable=unused-argument # noqa: ARG002
    ) -> str:
        """Render ``index.html`` for list and detail-ish ``/book`` URLs.

        Args:
            pk (str | int | None, optional): Routed book identifier extracted
                from ``/<string:pk>/`` but ignored while the SPA renders.
                Defaults to ``None``.

        Returns:
            str: Rendered SPA shell identical to ``ReaderIndexView`` output.

        """
        return self.render_template("index.html", appbuilder=self.appbuilder)
