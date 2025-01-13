
import pytest

from server.store.db import Base
from server.store import models

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite://", echo=True)
Session = sessionmaker(bind=engine)

@pytest.fixture(scope="session")
def setup_database():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def db_session(setup_database):
    session = Session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture(scope="function")
def alice_user():
    alice = models.User(name="Alice", email="alice@example.com", password_hash="alicepwd",
                oauth_provider="ExampleProvider", oauth_id="alice_oauth_id")
    return alice

@pytest.fixture(scope="function")
def bob_user():
    bob = models.User(name="Bob", email="bob@example.com", password_hash="bobpwd",
                oauth_provider="ExampleProvider", oauth_id="bob_oauth_id")
    return bob

@pytest.fixture(scope="function")
def charlie_user():
    charlie = models.User(name="Charlie", email="charlie@example.com", password_hash="charliepwd",
                oauth_provider="ExampleProvider", oauth_id="charlie_oauth_id")
    return charlie

@pytest.fixture(scope="function")
def david_user():
    david = models.User(name="David", email="david@example.com", password_hash="davidpwd",
                oauth_provider="ExampleProvider", oauth_id="david_oauth_id")
    return david
