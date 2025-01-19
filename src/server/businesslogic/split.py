
from server.store import db
from server.store import models

SplitType = models.TransactionSplitType

from .util import AttributeDelegator

class Split(AttributeDelegator):
    def __init__(self, split: models.Split):
        super().__init__(split)

    @staticmethod
    def create(debtor: "User", type: SplitType, /, amount: float | None = None,
               share: int | None = None):

        if (type in (SplitType.Equally, SplitType.Unequally, SplitType.Adjustments) and not amount):
            raise ValueError("Transaction type 'Equally' or 'Adjustments' requires an amount")

        if type in (SplitType.Shares, SplitType.Percentages) and not share:
            raise ValueError("Transaction type 'Shares' or 'Percentage' requires a share")

        split = models.Split(debtor=debtor, type=type, share=share)
        if amount:
            split.amount_cents = int(amount * 100)
        # db.session.add(split)
        # db.session.flush()
        return Split(split)

    @property
    def amount(self):
        return self.amount_cents / 100

    @amount.setter
    def amount(self, value):
        self.amount_cents = int(value * 100)

    # def is_share(self):
    #     return self.type in (SplitType.Shares, SplitType.Percentages)
