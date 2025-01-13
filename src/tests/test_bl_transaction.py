
import pytest

# from sqlalchemy import select
# from unittest.mock import MagicMock

from server import businesslogic
from server.businesslogic.split import SplitType
from server.store import db, models

from .dbhelpers import setup_database, db_session, alice_user, bob_user, charlie_user

def mock_db_session(db, session):
    setattr(db, "oldsession", db.session)
    setattr(db, "session", session)


@pytest.fixture(scope="function")
def mock_session(db_session):
    mock_db_session(db, db_session)


class TestBusinessLogicTransactions:
    def alice_and_bob(self, alice_user, bob_user):
        db.session.add_all([alice_user, bob_user])
        db.session.flush()
        alice = businesslogic.User(alice_user)
        bob = businesslogic.User(bob_user)
        assert alice.id == 1
        assert bob.id == 2

        group = alice.create_group("Hawaii 2024")
        group.members.append(bob)
        assert group.members[0] == alice
        assert group.members[1] == bob
        return alice, bob, group

    def alice_bob_charlie(self, alice_user, bob_user, charlie_user):
        db.session.add_all([alice_user, bob_user, charlie_user])
        db.session.flush()
        alice = businesslogic.User(alice_user)
        bob = businesslogic.User(bob_user)
        charlie = businesslogic.User(charlie_user)
        assert alice.id == 1
        assert bob.id == 2
        assert charlie.id == 3

        group = alice.create_group("Hawaii 2024")
        group.members.extend([bob, charlie])
        db.session.flush()
        assert group.members[0] == alice
        assert group.members[1] == bob
        assert group.members[2] == charlie
        return alice, bob, charlie, group

    def setup_user_group_transaction(self, alice_user, bob_user):
        alice, bob, group = self.alice_and_bob(alice_user, bob_user)
        transaction = group.add_transaction("ABC Store 12/22", 340.27, alice, bob)
        assert transaction.payer == alice
        assert transaction.debtor == bob
        assert transaction.amount == 340.27
        assert transaction.group == group

        assert len(group.transactions) == 1
        assert group.transactions[0] == transaction

        assert len(alice.owed_transactions) == 1
        assert len(alice.owing_transactions) == 0
        assert transaction in alice.owed_transactions

        assert len(bob.owed_transactions) == 0
        assert len(bob.owing_transactions) == 1
        assert transaction in bob.owing_transactions
        assert bob.owing_transactions[0].payer == alice
        assert bob.owing_transactions[0].amount == 340.27

        return alice, bob, group, transaction

    def test_add_group_transaction_single_debtor_comment(self, mock_session, alice_user, bob_user):
        alice, _, _, transaction = self.setup_user_group_transaction(alice_user, bob_user)
        comment = transaction.add_comment("Transaction created", alice)
        assert comment.id == 1
        assert comment in transaction.comments

    def test_add_group_transaction_simple_split(self, mock_session, alice_user, bob_user, charlie_user):
        alice, bob, charlie, group = self.alice_bob_charlie(alice_user, bob_user, charlie_user)
        bob_split = businesslogic.Split.create(bob, SplitType.Percentages, share=60)
        charlie_split = businesslogic.Split.create(charlie, SplitType.Percentages, share=40)
        transaction = group.add_transaction("ABC Store 12/22", 340.27, alice, [bob_split, charlie_split])
        assert bob_split in transaction.splits
        assert charlie_split in transaction.splits

    def test_add_group_transaction_invalid_split(self, mock_session, alice_user, bob_user, charlie_user):
        alice, bob, charlie, group = self.alice_bob_charlie(alice_user, bob_user, charlie_user)
        bob_split = businesslogic.Split.create(bob, SplitType.Percentages, share=60)
        charlie_split = businesslogic.Split.create(charlie, SplitType.Percentages, share=60)
        with pytest.raises(ValueError) as ex:
            transaction = group.add_transaction("ABC Store 12/22", 340.27, alice, [bob_split, charlie_split])
        assert "Sum of all shares" in str(ex.value)
