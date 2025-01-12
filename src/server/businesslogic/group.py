
from datetime import datetime
from server.store import db
from server.store import models

from .util import AttributeDelegator
from .transaction import Transaction

class Group(AttributeDelegator):
    def __init__(self, group: models.Group):
        super().__init__(group)

    @staticmethod
    def create(group_name: str,
               owner: "User",
               /,
               icon: str | None = None,
               members: list["User"] | None = None,
               valid_from: datetime | None = None,
               valid_until: datetime | None = None):
        group = models.Group(name=group_name, icon=icon, valid_from=valid_from,
                             valid_until=valid_until, owner=owner)
        group.users.append(owner)
        if members:
            for member in members:
                group.users.append(member)
        db.session.add(group)
        db.session.flush()
        return Group(group)

    @property
    def transactions(self):
        return [Transaction(transaction) for transaction in self._delegated.transactions]

    def add_user(self, user):
        self.users.append(user)
        db.session.flush()

    def remove_user(self, user):
        self.users.remove(user)
        db.session.flush()

    def add_transaction(self, description: str, amount: float, payer: "User",
                        debtor: "User | None" = None):
        # Using payer as the creator of the transaction
        return Transaction.create(description, amount, payer, payer, debtor, self)

    # Balances?
