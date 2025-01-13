
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
        group.members.append(owner)
        if members:
            for member in members:
                group.members.append(member)
        db.session.add(group)
        db.session.flush()
        return Group(group)

    @property
    def transactions(self):
        return [Transaction(transaction) for transaction in self._delegated.transactions]

    def add_member(self, member):
        self.members.append(member)
        db.session.flush()

    def remove_member(self, member):
        self.members.remove(member)
        db.session.flush()

    def add_transaction(self, description: str, amount: float, payer: "User",
                        debtor_or_splits: "User | list[Split]"):
        # Using payer as the creator of the transaction
        return Transaction.create(description, amount, payer, payer, debtor_or_splits, self)

    # Balances?
