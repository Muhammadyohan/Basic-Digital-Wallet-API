from fastapi import APIRouter, HTTPException, Depends

from typing import Annotated

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .. import security
from .. import models

from ..models.item import Item, CreateItem, UpdateItem, ItemList
from ..models.db_models import DBItem
from ..models.user import User


router = APIRouter(prefix="/items", tags=["item"])


@router.post("/{merchant_id}")
async def create_item(
    current_user: Annotated[User, Depends(security.get_current_active_user)],
    item: CreateItem,
    merchant_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> Item:
    data = item.dict()
    db_item = DBItem(**data)
    db_item.merchant_id = merchant_id
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)

    return Item.from_orm(db_item)


@router.get("")
async def get_items(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    page: int = 1,
    page_size: int = 10,
) -> ItemList:
    result = await session.exec(
        select(DBItem).offset((page - 1) * page_size).limit(page_size)
    )
    db_items = result.all()

    return ItemList(
        items=db_items, page=page, page_size=page_size, size_per_page=len(db_items)
    )


@router.get("/{item_id}")
async def get_item(
    item_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> Item:
    db_item = await session.get(DBItem, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return Item.from_orm(db_item)


@router.put("/{item_id}")
async def update_item(
    current_user: Annotated[User, Depends(security.get_current_active_user)],
    item_id: int,
    item: UpdateItem,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> Item:
    db_item = await session.get(DBItem, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    for key, value in item.dict().items():
        setattr(db_item, key, value)
        session.add(db_item)
        await session.commit()
        await session.refresh(db_item)

    return Item.from_orm(db_item)


@router.delete("/{item_id}")
async def delete_item(
    current_user: Annotated[User, Depends(security.get_current_active_user)],
    item_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> dict:
    db_item = await session.get(DBItem, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    await session.delete(db_item)
    await session.commit()

    return dict(message="Item deleted successfully")
