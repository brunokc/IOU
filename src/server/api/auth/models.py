import time

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from authlib.integrations.sqla_oauth2 import (
    OAuth2ClientMixin,
    OAuth2AuthorizationCodeMixin,
    OAuth2TokenMixin,
)

from server.store import db, User

class OAuth2Client(db.Model, OAuth2ClientMixin):
    __tablename__ = "oauth2_client"

    # id = db.Column(db.Integer, primary_key=True)
    # user_id = db.Column(
    #     db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    # user = db.relationship('User')
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    # user: Mapped[User] = relationship(back_populates="oauth2_client", cascade="all, delete-orphan")
    user: Mapped[User] = relationship()


class OAuth2AuthorizationCode(db.Model, OAuth2AuthorizationCodeMixin):
    __tablename__ = "oauth2_code"

    # id = db.Column(db.Integer, primary_key=True)
    # user_id = db.Column(
    #     db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    # user = db.relationship('User')
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    # user: Mapped[User] = relationship(back_populates="oauth2_code", cascade="all, delete-orphan")
    user: Mapped[User] = relationship()


class OAuth2Token(db.Model, OAuth2TokenMixin):
    __tablename__ = "oauth2_token"

    # id = db.Column(db.Integer, primary_key=True)
    # user_id = db.Column(
    #     db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    # user = db.relationship('User')
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    # user: Mapped[User] = relationship(back_populates="oauth2_token", cascade="all, delete-orphan")
    user: Mapped[User] = relationship()

    def is_refresh_token_active(self):
        if self.revoked:
            return False
        expires_at = self.issued_at + self.expires_in * 2
        return expires_at >= time.time()
