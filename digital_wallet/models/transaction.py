from pydantic import BaseModel, ConfigDict

from .item import Item


class BaseTransaction(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_price: float
    quantity: int = 1
    item_name: str | None = None
    item_id: int | None = 0
    merchant_first_name: str | None = None
    merchant_last_name: str | None = None
    merchant_id: int | None = 0
    metchant_user_id: int | None = 0
    user_first_name: str | None = None
    user_last_name: str | None = None
    user_id: int | None = 0


class CreateTransaction(BaseTransaction):
    pass


class UpdateTransaction(BaseTransaction):
    pass


class Transaction(BaseTransaction):
    id: int


class TransactionList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    transactions: list[Transaction]
    page: int
    page_count: int
    size_per_page: int
