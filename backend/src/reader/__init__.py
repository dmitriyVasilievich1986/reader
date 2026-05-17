"""Reader application package."""

__all__ = ("__version__", "appbuilder", "db", "migrate")

from flask_appbuilder import AppBuilder, SQLA
from flask_migrate import Migrate

__version__ = "0.1.1"

appbuilder = AppBuilder()
migrate = Migrate()
db = SQLA()
