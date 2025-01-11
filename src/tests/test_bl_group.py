
import pytest

# from sqlalchemy import select
# from unittest.mock import MagicMock

from server import businesslogic
from server.store import db, models

from .dbhelpers import setup_database, db_session, alice_user, bob_user

def mock_db_session(db, session):
    setattr(db, "oldsession", db.session)
    setattr(db, "session", session)


@pytest.fixture(scope="function")
def mock_session(db_session):
    mock_db_session(db, db_session)


class TestBusinessLogicGroups:
    def alice_and_bob(self, alice_user, bob_user):
        db.session.add_all([alice_user, bob_user])
        db.session.flush()
        alice = businesslogic.User(alice_user)
        bob = businesslogic.User(bob_user)
        assert alice.id == 1
        assert bob.id == 2
        return alice, bob
