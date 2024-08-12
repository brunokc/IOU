
# import bcrypt
from datetime import datetime
from enum import auto, StrEnum

from sqlalchemy import ForeignKey, String, DateTime, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class TransactionSplitType(StrEnum):
    Equally = auto()
    Unequally = auto()
    Percentages = auto()
    Shares = auto()
    Adjustments = auto()


# declarative base class
class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    email: Mapped[str] = mapped_column(String(100), CheckConstraint("email <> ''"), unique=True)
    name: Mapped[str] = mapped_column(String(100), CheckConstraint("name <> ''"), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(100), nullable=False)
    password_expiration: Mapped[datetime] = mapped_column(DateTime, default=datetime.min)

    groups: Mapped[list["Group"]] = relationship(back_populates="users", secondary="GroupMembership")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="payer")
    splits: Mapped[list["Split"]] = relationship(back_populates="debtor")

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


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    valid_from: Mapped[datetime] = mapped_column(nullable=True)
    valid_until: Mapped[datetime] = mapped_column(nullable=True)
    users: Mapped[list[User]] = relationship(back_populates="groups", secondary="GroupMembership")


class GroupMembership(Base):
    __tablename__ = "group_membership"
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)

    payer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    payer: Mapped[User] = relationship(back_populates="transactions")

    splits: Mapped[list["Split"]] = relationship(back_populates="transaction")
    debtors: Mapped[list[User]] = relationship(back_populates="debtor")

    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    description: Mapped[str] = mapped_column(String(200))
    amount: Mapped[float] = mapped_column()
    split_type: Mapped[TransactionSplitType] = mapped_column(nullable=False)

    def __repr__(self):
        return (f"Transaction(id={self.id!r}, description={self.description!r}, payer={self.payer.email!r}, "
                f"amount={self.amount!r}, split_type={self.split_type!r}")


class Split(Base):
    __tablename__ = "splits"

    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id", ondelete="CASCADE"), primary_key=True)
    transaction: Mapped[Transaction] = relationship(back_populates="splits")

    debtor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    debtor: Mapped[User] = relationship(back_populates="splits")

    share: Mapped[float] = mapped_column(nullable=False)
    extra: Mapped[float] = mapped_column(nullable=True)
