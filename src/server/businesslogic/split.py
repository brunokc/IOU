
from server.store import db
from server.store import models

SplitType = models.TransactionSplitType

from .util import AttributeDelegator

class Split(AttributeDelegator):
    def __init__(self, split: models.Split):
        super().__init__(split)

    @staticmethod
    def create(debtor: "User", type: SplitType, /, amount: float | None = None,
               share: int | None = None, share_denominator: int | None = None):

        if (type in (SplitType.Equally, SplitType.Unequally, SplitType.Adjustments) and not amount):
            raise ValueError("Transaction type 'Equally' or 'Adjustments' requires an amount")

        if type == SplitType.Shares and (not share or not share_denominator):
            raise ValueError("Transaction type 'Shares' requires share numerator and denominator")

        if type == SplitType.Percentages and not share:
            raise ValueError("Transaction type 'Percentages' requires a share numerator (share denominator is assumed to be 100)")

        if type == SplitType.Percentages:
            share_denominator = 100

        if share != 0 and share_denominator == 0:
            raise ZeroDivisionError("share_denominator needs to be non-zero when a share is supplied")

        # breakpoint()
        split = models.Split(debtor=debtor, type=type, share=share, share_denominator=share_denominator)
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
        self.amount_cents = value * 100


# class SplitList(list):
#     def append(self, split: Split):
#         if not split.order:
#             split.order = len(self) + 1

#         super().append(split)
