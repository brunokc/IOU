
from server.store import db
from server.store import models

from .comment import Comment
from .split import Split
from .util import AttributeDelegator

class Transaction(AttributeDelegator):
    def __init__(self, transaction: models.Transaction):
        super().__init__(transaction)

    @staticmethod
    def create(description: str, amount: float, created_by: "User", payer: "User",
               debtor: "User | None" = None, group: "Group | None" = None):
        transaction = models.Transaction(payer=payer, debtor=debtor, group=group,
                                         description=description, amount_cents=int(amount * 100),
                                         created_by=created_by)
        db.session.add(transaction)
        db.session.flush()
        return Transaction(transaction)

    @property
    def amount(self):
        return self.amount_cents / 100

    @amount.setter
    def amount(self, value):
        self.amount_cents = value * 100

    @property
    def splits(self):
        return [Split(split) for split in self._delegated.splits]

    @property
    def comments(self):
        return [Comment(comment) for comment in self._delegated.comments]

    def add_split(self, debtor: "User", order: int, split_type: models.TransactionSplitType,
                  amount: float | None = None, share_numerator: int | None = None,
                  share_denominator: int | None = None):
        return Split.create(self, debtor, order, split_type, amount, share_numerator, share_denominator)

    def add_comment(self, comment: str, user: "User"):
        return Comment.create(comment, user, transaction=self)
