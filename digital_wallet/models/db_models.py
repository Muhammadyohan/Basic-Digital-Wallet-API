from typing import Optional

from sqlmodel import Field, SQLModel, Relationship

from .merchant import Merchant
from .item import Item
from .wallet import Wallet
from .transaction import Transaction


class DBMerchant(Merchant, SQLModel, table=True):
    __tablename__ = "merchants"
    id: Optional[int] = Field(default=None, primary_key=True)

    items: list["DBItem"] = Relationship(back_populates="merchant", cascade_delete=True)
    wallet: Optional["DBWallet"] = Relationship(
        back_populates="merchant", cascade_delete=True
    )


class DBItem(Item, SQLModel, table=True):
    __tablename__ = "items"
    id: Optional[int] = Field(default=None, primary_key=True)

    merchant_id: Optional[int] = Field(default=None, foreign_key="merchants.id")
    merchant: Optional[DBMerchant] = Relationship(back_populates="items")

    transactions: list["DBTransaction"] = Relationship(back_populates="item")


class DBWallet(Wallet, SQLModel, table=True):
    __tablename__ = "wallets"
    id: Optional[int] = Field(default=None, primary_key=True)

    merchant_id: Optional[int] = Field(default=None, foreign_key="merchants.id")
    merchant: Optional[DBMerchant] = Relationship(back_populates="wallet")

    transactions: list["DBTransaction"] = Relationship(back_populates="wallet")


class DBTransaction(Transaction, SQLModel, table=True):
    __tablename__ = "transactions"
    id: Optional[int] = Field(default=None, primary_key=True)

    wallet_id: Optional[int] = Field(default=None, foreign_key="wallets.id")
    wallet: Optional[DBWallet] = Relationship(back_populates="transactions")

    item_id: Optional[int] = Field(default=None, foreign_key="items.id")
    item: Optional[DBItem] = Relationship(back_populates="transactions")
