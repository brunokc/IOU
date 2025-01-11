
from server.store import db
from server.store import models

from .util import AttributeDelegator

class Transaction(AttributeDelegator):
    def __init__(self, transaction: models.Transaction):
        super().__init__(transaction)

    @property
    def amount(self):
        return self.amount_cents / 100

    @amount.setter
    def amount(self, value):
        self.amount_cents = value * 100

    def add_split(self):
        pass

    def add_comment(self, comment):
        pass
