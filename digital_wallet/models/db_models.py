from typing import Optional

from sqlmodel import Field, SQLModel, Relationship

from .merchant import Merchant
from .item import Item
from .wallet import Wallet


class DBMerchant(Merchant, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    items: list["DBItem"] = Relationship(back_populates="merchant", cascade_delete=True)
    wallet: Optional["DBWallet"] = Relationship(back_populates="merchant", cascade_delete=True)


class DBItem(Item, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    merchant_id: Optional[int] = Field(default=None, foreign_key="dbmerchant.id")
    merchant: Optional[DBMerchant] = Relationship(back_populates="items")


class DBWallet(Wallet, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    merchant_id: Optional[int] = Field(default=None, foreign_key="dbmerchant.id")
    merchant: Optional[DBMerchant] = Relationship(back_populates="wallet")
