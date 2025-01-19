from flask.cli import FlaskGroup
from reader.app import create_app


main = FlaskGroup(create_app=create_app)