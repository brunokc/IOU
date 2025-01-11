
from server.store import db
from server.store import models

from .util import AttributeDelegator

class Group(AttributeDelegator):
    def __init__(self, group: models.Group):
        super().__init__(group)

    def add_user(self, user):
        self.users.append(user)
        db.session.flush()

    def remove_user(self, user):
        self.users.remove(user)
        db.session.flush()
