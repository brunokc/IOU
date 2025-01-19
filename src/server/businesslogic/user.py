
from datetime import datetime

from server.store import db
from server.store import models

from .group import Group
from .transaction import Transaction
from .debt import Debt
from .util import AttributeDelegator

class User(AttributeDelegator):
    def __init__(self, user: models.User):
        super().__init__(user)

    @staticmethod
    def create(name: str, email: str, password_hash: str, oauth_provider: str, oauth_id: str):
        user = models.User(name=name, email=email, password_hash=password_hash,
                           oauth_provider=oauth_provider, oauth_id=oauth_id)
        db.session.add(user)
        db.session.flush()
        return User(user)

    def add_friend(self, *friends: list["User"]):
        for friend in friends:
            self.friends.append(friend)
            friend.friends.append(self)
        db.session.flush()

    def create_group(self,
            group_name: str,
            /,
            icon: str | None = None,
            valid_from: datetime | None = None,
            valid_until: datetime | None = None):
        return Group.create(group_name, self, icon=icon, valid_from=valid_from,
                             valid_until=valid_until)

    def add_transaction(self, description: str, amount: float, debtor: "User",
                        group: "Group | None" = None):
        return Transaction.create(description, amount, self, self, debtor, group)

    def get_payments_to(self, user: "User"):
        return [Debt(debt) for debt in self.creditor_debts if debt.debtor == user]

    def get_debts_to(self, user: "User"):
        return [Debt(debt) for debt in self.debtor_debts if debt.creditor == user]
