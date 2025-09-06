from flask import Flask

from reader import appbuilder, db, migrate
from reader.views.api import AuthorModelApi, BookModelApi, PageModelApi
from reader.views.views import BookView, ReaderIndexView


def create_app() -> Flask:
    app = Flask(__name__)

    app.config.from_object("reader.config")
    app.static_url_path = app.config["STATIC_URL_PATH"]
    app.static_folder = app.config["STATIC_FOLDER"]

    db.init_app(app)

    with app.app_context():
        appbuilder.indexview = ReaderIndexView
        appbuilder.init_app(app, db.session)
        appbuilder.add_view(BookView, "Book")
        appbuilder.add_api(AuthorModelApi)
        appbuilder.add_api(BookModelApi)
        appbuilder.add_api(PageModelApi)

        migrate.directory = app.config["MIGRATIONS_DIR"]
        migrate.init_app(app, db)

    return app
