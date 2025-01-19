from pathlib import Path
from os import getenv

BASE_DIR = Path(__file__).parent
MIGRATIONS_DIR = BASE_DIR / "alembic"
ENV_FILE = BASE_DIR / ".env"

DB_NAME = getenv("DB_NAME", "reader")
DB_PATH = BASE_DIR / f"{DB_NAME}.sqlite"

SQLALCHEMY_TRACK_MODIFICATIONS = False

FAB_API_SWAGGER_UI = True
# FAB_API_SWAGGER_UI = getenv("FAB_API_SWAGGER_UI", "False").lower() == "true"
DEBUG = getenv("DEBUG", "False").lower() == "true"
SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
SECRET_KEY = getenv("SECRET_KEY", "secret")
LOG_LEVEL = getenv("LOG_LEVEL", "INFO")

STATIC_FOLDER = BASE_DIR.parent / "static"
TEMPLATE_FOLDER = BASE_DIR / "templates"
STATIC_URL_PATH = "/static"

APP_HOST = getenv("APP_HOST", "0.0.0.0")
APP_PORT = getenv("APP_PORT", "3000")
