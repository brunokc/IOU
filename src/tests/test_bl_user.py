
import pytest

# from sqlalchemy import select
# from unittest.mock import MagicMock

from server import businesslogic
from server.store import db, models

from .dbhelpers import setup_database, db_session, alice_user, bob_user

def mock_db_session(db, session):
    # mock_session = MagicMock()
    # mock_session.configure_mock(
    #     **{
    #         "session.return_value": session
    #     }
    # )
    setattr(db, "oldsession", db.session)
    setattr(db, "session", session)


@pytest.fixture(scope="function")
def mock_session(db_session):
    mock_db_session(db, db_session)


class TestBusinessLogicUsers:
    # def setup_method(self, mock_session):
    #     self.mock_session = mock_session
    #     print("Mocking DB...")

    def alice_and_bob(self, alice_user, bob_user):
        db.session.add_all([alice_user, bob_user])
        db.session.flush()
        alice = businesslogic.User(alice_user)
        bob = businesslogic.User(bob_user)
        assert alice.id == 1
        assert bob.id == 2
        return alice, bob


    def test_add_user(self, mock_session):
        newuser = businesslogic.User.create(
            name="Test User", email="user@example.com", password_hash="abc123",
            oauth_provider="None", oauth_id="wxyz"
            )
        assert newuser.id == 1


    def test_friend_user(self, mock_session, alice_user, bob_user):
        alice, bob = self.alice_and_bob(alice_user, bob_user)

        alice.add_friend(bob)
        assert len(alice.friends) == 1
        assert bob in alice.friends
        assert len(bob.friends) == 1
        assert alice in bob.friends


    def test_add_user_to_group(self, mock_session, alice_user):
        db.session.add(alice_user)
        db.session.flush()
        alice = businesslogic.User(alice_user)
        # assert alice._user.id == 1
        assert alice.id == 1

        group = alice.create_group("Alice's group")
        assert group.id == 1
        assert group.owner == alice
        assert alice in group.users


    def test_user_to_user_transaction(self, mock_session, alice_user, bob_user):
        alice, bob = self.alice_and_bob(alice_user, bob_user)
        transaction = alice.add_transaction("Lunch at McDonald's", 123.45, bob)
        assert transaction.payer == alice
        assert transaction.debtor == bob
        assert transaction.amount_cents == 12345
        assert transaction.amount == 123.45

        assert len(alice.owed_transactions) == 1
        assert len(alice.owing_transactions) == 0
        assert transaction in alice.owed_transactions

        assert len(bob.owed_transactions) == 0
        assert len(bob.owing_transactions) == 1
        assert transaction in bob.owing_transactions
        assert bob.owing_transactions[0].payer == alice
        assert bob.owing_transactions[0].amount == 123.45
