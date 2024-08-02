from typing import Optional

from pydantic import BaseModel, ConfigDict

from sqlmodel import Field, SQLModel  # type: ignore


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


class DBItem(Item, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class ItemList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[Item]
    page: int
    page_size: int
    size_per_page: int
