
from server.store import db
from server.store import models

from .util import AttributeDelegator

class Debt(AttributeDelegator):
    def __init__(self, debt: models.Debt):
        super().__init__(debt)

    @staticmethod
    def create(creditor: "User", debtor: "User", amount: float, group: "Group | None" = None):
        debt = models.Debt(creditor=creditor, debtor=debtor, group=group, amount=amount)
        db.session.add(debt)
        db.session.flush()
        return Debt(debt)
