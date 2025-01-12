
from server.store import db
from server.store import models

SplitType = models.TransactionSplitType

from .util import AttributeDelegator

class Split(AttributeDelegator):
    def __init__(self, split: models.Split):
        super().__init__(split)

    @staticmethod
    def create(transaction: "Transaction", debtor: "User", order: int,
               type: SplitType, amount: float | None = None,
               share_numerator: int | None = None, share_denominator: int | None = None):

        if (type in (SplitType.Equally, SplitType.Unequally, SplitType.Adjustments) and not amount):
            raise ValueError("Transaction type 'Equally' or 'Adjustments' requires an amount")

        if (type in (SplitType.Percentages, SplitType.Shares) and
            (not share_numerator or not share_denominator)):
            raise ValueError("Transaction type 'Shares' or 'Percentages' requires share numerator and denominator")

        if share_numerator != 0 and share_denominator == 0:
            raise ZeroDivisionError("share_denominator needs to be non-zero when a share_numerator is supplied")

        split = models.Split(transaction=transaction, debtor=debtor, order=order, type=type,
                             amount=amount, share_numerator=share_numerator,
                             share_denominator=share_denominator)
        db.session.add(split)
        db.session.flush()
        return Split(split)

    @property
    def amount(self):
        return self.amount_cents / 100

    @amount.setter
    def amount(self, value):
        self.amount_cents = value * 100
