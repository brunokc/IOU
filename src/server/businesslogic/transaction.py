
from functools import wraps
from sqlalchemy import event, inspect
from server.store import db
from server.store import models

SplitType = models.TransactionSplitType

from .comment import Comment
from .split import Split
from .util import AttributeDelegator, get_model_changes


def validator(func):
    @event.listens_for(models.Transaction, "before_insert")
    def validate_for_insert(mapper, connection, target):
        state = inspect(target)
        if state.modified:
            func(Transaction(target))

    @event.listens_for(models.Transaction, "before_update")
    def validate_for_update(mapper, connection, target):
        state = inspect(target)
        if state.modified:
            func(Transaction(target))

    return func


class Transaction(AttributeDelegator):
    def __init__(self, transaction: models.Transaction):
        super().__init__(transaction)

    @staticmethod
    def create(description: str, amount: float, created_by: "User", payer: "User",
               debtor_or_splits: "User | list[Split]", group: "Group | None" = None):

        from .user import User

        if not isinstance(debtor_or_splits, (User, list)):
            raise ValueError("debtor_or_splits needs to be either a User (single debtor) or a list of splits (multiple debtors)")

        transaction = models.Transaction(payer=payer, group=group, description=description,
                                         amount_cents=int(amount * 100), created_by=created_by)
        if isinstance(debtor_or_splits, User):
            transaction.debtor = debtor_or_splits
        else:
            for idx, split in enumerate(debtor_or_splits, 1):
                split._delegated.order = idx
                split._delegated.transaction = transaction

        db.session.add(transaction)
        db.session.flush()
        return Transaction(transaction)

    @validator
    def _validate(self):
        print("Running validation before insert/update")
        self._validate_splits()
        self._update_debts()

    @property
    def amount(self):
        return self.amount_cents / 100

    @amount.setter
    def amount(self, value):
        self.amount_cents = int(value * 100)

    def _validate_splits(self):
        # There's nothing to validate for the single debtor case
        if len(self._delegated.splits) == 0:
            return

        # sum = 0
        shares_sum = 0
        split_type = None
        for split in self._delegated.splits:
            # sum += split.amount_cents * 100
            if split.share:
                if not split_type:
                    split_type = split.type
                else:
                    if split.type != split_type:
                        raise ValueError("Inconsistent split type across multiple splits")

                if split.type == SplitType.Percentages and (split.share < 1 or split.share > 100):
                    raise ValueError("'Percentage' shares should be between 1% and 100%")

                shares_sum += split.share

        # For percentages, sum of all shares should be equal to 100%
        if split.type == SplitType.Percentages and shares_sum != 100:
            shares = list(f"{split.share}%" for split in self._delegated.splits)
            raise ValueError("Sum of all 'Percentage' shares should total 100% "
                             f"(got shares [{", ".join(shares)}]; total: {shares_sum}%)")


    def _update_debts(self):
        changes = get_model_changes(self)
        for change in changes:
            print(f"UpdateDebts: {change}")
        # if self.amount_cents.__name__ in changes or self.splits.__name__ in changes:
        #     for split in self.splits:
        #         if split.type == SplitType.Adjustments

    # def add_split(self, debtor: "User", order: int, split_type: models.TransactionSplitType,
    #               amount: float | None = None, share_numerator: int | None = None,
    #               share_denominator: int | None = None):
    #     return Split.create(self, debtor, order, split_type, amount, share_numerator, share_denominator)

    def add_comment(self, comment: str, user: "User"):
        return Comment.create(comment, user, transaction=self)
