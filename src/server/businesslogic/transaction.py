
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
               debtor_or_splits: "User | list[Split]", group: "Group | None" = None):

        from .user import User

        if not isinstance(debtor_or_splits, (User, list)):
            raise ValueError("debtor_or_splits needs to be either a User (single debtor) or a list of splits (multiple debtors)")

        transaction_model = models.Transaction(payer=payer, group=group, description=description,
                                         amount_cents=int(amount * 100), created_by=created_by)
        if isinstance(debtor_or_splits, User):
            transaction_model.debtor = debtor_or_splits
        else:
            for idx, split in enumerate(debtor_or_splits, 1):
                split._delegated.order = idx
                split._delegated.transaction = transaction_model
                # print(f"split {idx}: {split}")

        transaction = Transaction(transaction_model)
        transaction._validate_splits()

        db.session.add(transaction_model)
        db.session.flush()
        return transaction

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

    def _validate_splits(self):
        # There's nothing to validate for the single debtor case
        if len(self._delegated.splits) == 0:
            return

        # sum = 0
        shares = 0
        denominator = None
        for split in self._delegated.splits:
            # sum += split.amount_cents * 100
            if split.share:
                shares += split.share
            if not denominator:
                denominator = split.share_denominator
            else:
                if denominator != split.share_denominator:
                    raise ValueError("Split denominators should be all the same")

        # Sum of all shares should be equal the denominator, to get us 1/1 or 100%
        if shares != denominator:
            raise ValueError("Sum of all shares should be equal to denominator and result in a "
                             "1/1 proportion or 100% percentage")


    # def add_split(self, debtor: "User", order: int, split_type: models.TransactionSplitType,
    #               amount: float | None = None, share_numerator: int | None = None,
    #               share_denominator: int | None = None):
    #     return Split.create(self, debtor, order, split_type, amount, share_numerator, share_denominator)

    def add_comment(self, comment: str, user: "User"):
        return Comment.create(comment, user, transaction=self)
