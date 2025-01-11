
from datetime import datetime

from server.store import db
from server.store import models

from .group import Group
from .transaction import Transaction
from .util import AttributeDelegator

class User(AttributeDelegator):
    def __init__(self, user: models.User):
        super().__init__(user)

    @staticmethod
    # @transactional(db.session)
    def create(name: str, email: str, password_hash: str, oauth_provider: str, oauth_id: str):
        user = models.User(name=name, email=email, password_hash=password_hash,
                           oauth_provider=oauth_provider, oauth_id=oauth_id)
        db.session.add(user)
        db.session.flush()
        return User(user)

    @property
    def owed_transactions(self):
        return [Transaction(transaction) for transaction in self._delegated.owed_transactions]

    @property
    def owing_transactions(self):
        return [Transaction(transaction) for transaction in self._delegated.owing_transactions]

    def add_friend(self, *friends: list["User"]):
        for friend in friends:
            self.friends.append(friend)
            friend.friends.append(self)
        db.session.flush()

    def create_group(self,
            group_name: str,
            icon: str | None = None,
            valid_from: datetime | None = None,
            valid_until: datetime | None = None):
        group = models.Group(name=group_name, icon=icon, valid_from=valid_from,
                             valid_until=valid_until, owner=self)
        group.users.append(self)
        db.session.add(group)
        db.session.flush()
        return Group(group)

    def add_transaction(self, description: str, debtor: "User", amount: float,
                        group: Group | None = None):
        transaction = models.Transaction(payer=self, debtor=debtor, group=group,
                                         description=description, amount_cents=int(amount * 100),
                                         created_by=self)
        db.session.add(transaction)
        db.session.flush()
        return Transaction(transaction)
