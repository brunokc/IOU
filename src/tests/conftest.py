import pytest
import os

from server import create_app
from dotenv import load_dotenv
from sqlalchemy import URL

load_dotenv()

@pytest.fixture()
def app():
    # app = create_app({
    #     "TESTING": True,
    #     "SQLALCHEMY_DATABASE_URI": URL.create(
    #         drivername="postgresql",
    #         username=os.getenv("DB_USER"),
    #         password=os.getenv("DB_USER_PASSWORD"),
    #         host=os.getenv("DB_HOST"),
    #         database=os.getenv("DB_NAME"))
    #     })

    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite+pysqlite:///:memory:"
        })

    # other setup can go here

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
