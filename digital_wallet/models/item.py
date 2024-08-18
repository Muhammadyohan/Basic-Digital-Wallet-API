from pydantic import BaseModel, ConfigDict


class BaseItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str | None = None
    price: float = 0.12
    tax: float | None = None


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
