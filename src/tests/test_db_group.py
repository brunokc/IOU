
from sqlalchemy import select
from server.store.models import *

from .dbhelpers import setup_database, db_session

class TestGroups:
    def test_add_user_to_group(self, db_session):
        alice = User(name="Alice", email="alice@example.com", password_hash="alicepwd",
                    oauth_provider="None", oauth_id="alice_oauth_id")
        bob = User(name="Bob", email="bob@example.com", password_hash="bobpwd",
                    oauth_provider="None", oauth_id="bob_oauth_id")
        savepoint = db_session.begin_nested()
        db_session.add_all([alice, bob])
        savepoint.commit()

        alice_id = alice.id
        assert alice_id > 0

        bob_id = bob.id
        assert bob_id > 0

        alice = db_session.execute(select(User).where(User.id == alice_id)).scalar()
        bob = db_session.execute(select(User).where(User.id == bob_id)).scalar()

        savepoint = db_session.begin_nested()
        group = Group(name="Test group", owner=alice)
        group.users = [alice, bob]
        db_session.add(group)
        savepoint.commit()

        group_id = group.id
        assert group_id > 0

        group = db_session.execute(select(Group).where(Group.id == group_id)).scalar()
        assert group.name == "Test group"
