from pydantic import BaseModel, ConfigDict


class BaseItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str | None = None
    price: float = 0.12
    stock: int = 1
    tax: float | None = None
    user_id: int | None = 0
    merchant_id: int | None = 0


class CreateItem(BaseItem):
    pass


class UpdateItem(BaseItem):
    pass


class Item(BaseItem):
    id: int


class ItemList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[Item]
    page: int
    page_count: int
    size_per_page: int
