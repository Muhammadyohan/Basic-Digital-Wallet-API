from pydantic import BaseModel, ConfigDict


class BaseTransaction(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_price: float
    quantity: int = 1


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
    page_size: int
    size_per_page: int