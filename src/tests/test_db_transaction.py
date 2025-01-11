
from sqlalchemy import select
from server.store.models import *

from .dbhelpers import setup_database, db_session, alice_user, bob_user

class TestGroups:
    def test_2_user_transaction_no_group(self, db_session, alice_user, bob_user):
        savepoint = db_session.begin_nested()
        db_session.add_all([alice_user, bob_user])
        savepoint.commit()

        savepoint = db_session.begin_nested()
        transaction = Transaction(description="Test transaction")
        transaction.payer = alice_user
        transaction.created_by = alice_user.id
        transaction.debtor = bob_user
        transaction.amount_cents = 10000
        transaction.comments = [Comment(user=alice_user, comment="Test comment")]
        db_session.add(transaction)
        savepoint.commit()

        assert transaction.id == 1
        assert transaction.comments[0].id == 1

        transaction_id = transaction.id
        transaction = db_session.execute(select(Transaction).where(Transaction.id == transaction_id)).scalar()
        assert transaction.description == "Test transaction"
        assert transaction.comments[0].comment == "Test comment"
