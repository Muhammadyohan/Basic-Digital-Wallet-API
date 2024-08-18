import math

from fastapi import APIRouter, HTTPException, Depends

from typing import Annotated

from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from .. import security
from .. import models

from ..models.item import Item, CreateItem, UpdateItem, ItemList
from ..models.db_models import DBItem
from ..models.user import User


router = APIRouter(prefix="/items", tags=["item"])

SIZE_PER_PAGE = 50


@router.post("/{merchant_id}")
async def create_item(
    current_user: Annotated[User, Depends(security.get_current_active_user)],
    item: CreateItem,
    merchant_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> Item:
    db_item = DBItem.model_validate(item)
    db_item.merchant_id = merchant_id
    db_item.user = current_user
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)

    return Item.model_validate(db_item)


@router.get("")
async def get_items(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    page: int = 1,
) -> ItemList:
    result = await session.exec(
        select(DBItem).offset((page - 1) * SIZE_PER_PAGE).limit(SIZE_PER_PAGE)
    )
    db_items = result.all()

    page_count = int(
        math.ceil(
            (await session.exec(select(func.count(DBItem.id)))).first() / SIZE_PER_PAGE
        )
    )

    return ItemList.model_validate(
        dict(
            items=db_items,
            page=page,
            page_count=page_count,
            size_per_page=SIZE_PER_PAGE,
        )
    )


@router.get("/{item_id}")
async def get_item(
    item_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> Item:
    db_item = await session.get(DBItem, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return Item.model_validate(db_item)


@router.put("/{item_id}")
async def update_item(
    current_user: Annotated[User, Depends(security.get_current_active_user)],
    item_id: int,
    item: UpdateItem,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> Item:
    data = item.model_dump()
    db_item = await session.get(DBItem, item_id)

    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    if db_item.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    db_item.sqlmodel_update(data)
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)

    return Item.model_validate(db_item)


@router.delete("/{item_id}")
async def delete_item(
    current_user: Annotated[User, Depends(security.get_current_active_user)],
    item_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> dict:
    db_item = await session.get(DBItem, item_id)

    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    if db_item.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    await session.delete(db_item)
    await session.commit()

    return dict(message="Item deleted successfully")
