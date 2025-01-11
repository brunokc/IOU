
import json

from server.store.models import *

from .dbhelpers import setup_database, db_session, alice_user

class TestUsers:
    def test_valid_user(self, db_session):
        savepoint = db_session.begin_nested()
        user = User(name="Test User", email="user@example.com", password_hash="abc123",
                    oauth_provider="None", oauth_id="wxyz")
        db_session.add(user)
        savepoint.commit()

    def test_payment_links(self, db_session, alice_user):
        savepoint = db_session.begin_nested()
        db_session.add(alice_user)
        savepoint.commit()

        savepoint = db_session.begin_nested()
        links = [
            PaymentLink(provider="PayPal", user="alice"),
            PaymentLink(provider="Venmo", user="alice"),
            PaymentLink(provider="CashApp", user="alice"),
        ]
        alice_user.payment_links = json.dumps(links)
        savepoint.commit()
