
from server.store import db
from server.store import models

from .util import AttributeDelegator

class Comment(AttributeDelegator):
    def __init__(self, comment: models.Comment):
        super().__init__(comment)

    @staticmethod
    def create(comment: str, user: "User", transaction: "Transaction"):
        comment = models.Comment(transaction=transaction, user=user, comment=comment)
        db.session.add(comment)
        db.session.flush()
        return Comment(comment)
