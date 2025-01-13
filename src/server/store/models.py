
# import bcrypt
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import auto, StrEnum

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base

class TransactionSplitType(StrEnum):
    Equally = auto()
    Unequally = auto()
    Percentages = auto()
    Shares = auto()
    Adjustments = auto()


#
# Payment links:
#
# Venmo: https://venmo.com/<userid>
# PayPal (may need creating the link upfront): https://paypal.me/<userid>
# CashApp: https://cash.app/<$cashtag>
#
class PaymentProvider(StrEnum):
    PayPal = auto()
    Venmo = auto()
    CashApp = auto()

SUPPORTED_PAYMENT_LINKS = {
    PaymentProvider.PayPal: "https://paypal.me/{}",
    PaymentProvider.Venmo: "https://venmo.com/{}",
    PaymentProvider.CashApp: "https://cash.app/${}",
}

@dataclass
class PaymentLink:
    provider: str
    user: str
    link: str = field(init=False)

    def __post_init__(self):
        link = getattr(PaymentProvider, self.provider)
        self.link = link.format(self.user)


@dataclass
class PaymentLinks:
    payment_links: list[PaymentLink]


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100), CheckConstraint("name <> ''"), nullable=False)
    email: Mapped[str] = mapped_column(String(100), CheckConstraint("email <> ''"), unique=True)
    payment_links: Mapped[str] = mapped_column(Text, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(100), nullable=False)
    password_expiration: Mapped[datetime] = mapped_column(DateTime, default=datetime.min)

    profile_picture: Mapped[str] = mapped_column(Text, nullable=True)
    oauth_provider: Mapped[str] = mapped_column(String(100))
    oauth_id: Mapped[str] = mapped_column(String(200), unique=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc),
                                                 onupdate=datetime.now(timezone.utc))

    # Relationships
    # friends: Mapped[list["User"]] = relationship(secondary="friendship", foreign_keys="Friendship.user_id")
    friends: Mapped[list["User"]] = relationship(secondary="friendship",
                                                 primaryjoin="User.id == Friendship.user_id",
                                                 secondaryjoin="User.id == Friendship.friend_user_id")
    owned_groups: Mapped[list["Group"]] = relationship(back_populates="owner")
    groups: Mapped[list["Group"]] = relationship(back_populates="members", secondary="group_membership")
    splits: Mapped[list["Split"]] = relationship(back_populates="debtor")

    owed_transactions: Mapped[list["Transaction"]] = relationship(back_populates="payer", foreign_keys="Transaction.payer_id")
    owing_transactions: Mapped[list["Transaction"]] = relationship(back_populates="debtor", foreign_keys="Transaction.debtor_id")
    balances: Mapped[list["Balance"]] = relationship(back_populates="user")
    comments: Mapped[list["Comment"]] = relationship(back_populates="user")

    def __str__(self):
        return self.email

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r}, email={self.email!r})"

    def get_user_id(self):
        return self.id

    # def check_password(self, password):
    #     return password == 'valid'

    @property
    def password(self):
        raise AttributeError('password not readable')

    # @password.setter
    # def password(self, password):
    #     self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    # def verify_password(self, password):
    #     return bcrypt.checkpw(password.encode(), self.password_hash)


class Friendship(Base):
    __tablename__ = "friendship"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    friend_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(200), CheckConstraint("name <> ''"), nullable=False)
    icon: Mapped[str] = mapped_column(String(500), nullable=True)
    valid_from: Mapped[datetime] = mapped_column(nullable=True)
    valid_until: Mapped[datetime] = mapped_column(nullable=True)

    members: Mapped[list[User]] = relationship(back_populates="groups", secondary="group_membership")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="group")

    owner: Mapped[User] = relationship(back_populates="owned_groups")
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    # created_by: Mapped[User] = relationship(foreign_keys="Group.created_by_id")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc),
                                                 onupdate=datetime.now(timezone.utc))

    # Other relationships
    balances: Mapped[list["Balance"]] = relationship(back_populates="group")

    def __repr__(self):
        return f"Group(id={self.id!r}, name={self.name!r}, owner={self.owner.email!r})"


class GroupMembership(Base):
    __tablename__ = "group_membership"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))

    # user: Mapped[User] = relationship(back_populates="groups")
    # group: Mapped[Group] = relationship(back_populates="users")


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)

    payer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    payer: Mapped[User] = relationship(back_populates="owed_transactions", foreign_keys=payer_id)

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), nullable=True)
    group: Mapped[Group] = relationship(back_populates="transactions", foreign_keys=group_id)

    splits: Mapped[list["Split"]] = relationship(back_populates="transaction")

    debtor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    debtor: Mapped[User] = relationship(back_populates="owing_transactions", foreign_keys=debtor_id)

    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    description: Mapped[str] = mapped_column(String(200), CheckConstraint("description <> ''"), nullable=False)
    amount_cents: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    # split_type: Mapped[TransactionSplitType] = mapped_column(nullable=False)

    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_by: Mapped[User] = relationship(foreign_keys="Transaction.created_by_id")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc),
                                                 onupdate=datetime.now(timezone.utc))

    # Other relationships
    comments: Mapped[list["Comment"]] = relationship(back_populates="transaction")

    def __repr__(self):
        return (f"Transaction(id={self.id!r}, description={self.description!r}, payer={self.payer.email!r}, "
                f"group={self.group!r}, debtor={self.debtor!r}, amount_cents={self.amount_cents!r})")


class Split(Base):
    __tablename__ = "splits"

    id: Mapped[int] = mapped_column(primary_key=True)

    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id", ondelete="CASCADE"))
    transaction: Mapped[Transaction] = relationship(back_populates="splits")

    debtor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    debtor: Mapped[User] = relationship(back_populates="splits")

    order: Mapped[int] = mapped_column(nullable=False)
    type: Mapped[TransactionSplitType] = mapped_column(nullable=False)
    amount_cents: Mapped[int] = mapped_column(BigInteger, nullable=True)
    # share: Mapped[float] = mapped_column(nullable=True)
    share: Mapped[int] = mapped_column(nullable=True)
    # share_numerator: Mapped[int] = mapped_column(nullable=True)
    share_denominator: Mapped[int] = mapped_column(nullable=True)
    # extra_cents: Mapped[int] = mapped_column(BigInteger, nullable=True)

    def __repr__(self):
        return (f"Split(id={self.id!r}, transaction={self.transaction!r}, debtor={self.debtor!r}, "
                f"order={self.order!r}, type={self.type!r}, amount_cents={self.amount_cents!r}, "
                f"share={self.share!r}, share_denominator={self.share_denominator!r})")


class Balance(Base):
    __tablename__ = "balances"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user: Mapped[User] = relationship(back_populates="balances")

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), nullable=True)
    group: Mapped[Group] = relationship(back_populates="balances")

    amount_cents: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc),
                                                 onupdate=datetime.now(timezone.utc))

    def __repr__(self):
        return (f"Balance(id={self.id!r}, user={self.user.email!r}, group={self.group.name!r}, "
                f"amount_cents={self.amount_cents!r})")


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)

    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id", ondelete="CASCADE"),
                                                nullable=False)
    transaction: Mapped[Transaction] = relationship(back_populates="comments")

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user: Mapped[User] = relationship(back_populates="comments")

    comment: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc),
                                                 onupdate=datetime.now(timezone.utc))

    def __repr__(self):
        return (f"Comment(id={self.id!r}, transaction_id={self.transaction_id!r}, "
                f"user={self.user.email!r}, comment={self.comment!r})")


# class Receipt(Base):
#     __tablename__ = "receipts"

#     id: Mapped[int] = mapped_column(primary_key=True)

#     picture_url: Mapped[str] = mapped_column(String(500), nullable=True)

#     items: Mapped[list["ReceiptItem"]] = relationship(back_populates="receipt")
#     tax: Mapped[int] = mapped_column(nullable=True)
#     tip: Mapped[int] = mapped_column(nullable=True)


# class ReceiptItem(Base):
#     __tablename__ = "receipt_items"

#     id: Mapped[int] = mapped_column(primary_key=True)

#     receipt_id: Mapped[int] = mapped_column(ForeignKey("receipts.id", ondelete="CASCADE"))
#     receipt: Mapped[Receipt] = relationship(back_populates="items")

#     item: Mapped[str] = mapped_column(String(50), CheckConstraint("item <> ''"), nullable=False)
#     price: Mapped[int] = mapped_column(nullable=False)
#     quantity: Mapped[int] = mapped_column(default=0, nullable=False)


# class ReceiptItemAssignment(Base):
#     __tablename__ = "receipt_item_assignments"

#     id: Mapped[int] = mapped_column(primary_key=True)

#     debtor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
#     debtor: Mapped[User] = relationship(back_populates="")

#     receipt_item_id: Mapped[int] = mapped_column(ForeignKey("receipt_items.id", ondelete="CASCADE"))
#     receipt_item: Mapped[ReceiptItem] = relationship(back_populates="")

#     quantity: Mapped[int] = mapped_column(default=1, nullable=False)
