import math

from fastapi import APIRouter, HTTPException, Depends

from typing import Annotated

from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from .. import security
from .. import models

from ..models.merchant import Merchant, CreateMerchant, UpdateMerchant, MerchantList
from ..models.db_models import DBMerchant
from ..models.user import User

router = APIRouter(prefix="/merchants", tags=["merchant"])

SIZE_PER_PAGE = 50

@router.post("")
async def create_merchant(
    current_user: Annotated[User, Depends(security.get_current_active_user)],
    item: CreateMerchant,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> Merchant:
    data = item.dict()
    db_merchant = DBMerchant(**data)

    session.add(db_merchant)
    await session.commit()
    await session.refresh(db_merchant)

    return Merchant.from_orm(db_merchant)


@router.get("")
async def get_merchants(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    page: int = 1,
) -> MerchantList:
    result = await session.exec(
        select(DBMerchant).offset((page - 1) * SIZE_PER_PAGE).limit(SIZE_PER_PAGE)
    )
    db_merchants = result.all()

    page_count = int(
        math.ceil(
            (await session.exec(select(func.count(DBMerchant.id)))).first() / SIZE_PER_PAGE
        )
    )

    return MerchantList(
        merchants=db_merchants,
        page=page,
        page_count=page_count,
        size_per_page=SIZE_PER_PAGE,
    )


@router.get("/{merchant_id}")
async def get_merchant(
    merchant_id: int, session: Annotated[AsyncSession, Depends(models.get_session)]
) -> Merchant:
    db_merchant = await session.get(DBMerchant, merchant_id)
    if db_merchant is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return Merchant.from_orm(db_merchant)


@router.put("/{merchant_id}")
async def update_merchant(
    current_user: Annotated[User, Depends(security.get_current_active_user)],
    merchant_id: int,
    merchant: UpdateMerchant,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> Merchant:
    db_merchant = await session.get(DBMerchant, merchant_id)
    if db_merchant is None:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in merchant.dict().items():
        setattr(db_merchant, key, value)

    session.add(db_merchant)
    await session.commit()
    await session.refresh(db_merchant)

    return Merchant.from_orm(db_merchant)


@router.delete("/{merchant_id}")
async def delete_merchant(
    current_user: Annotated[User, Depends(security.get_current_active_user)],
    merchant_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> dict:
    db_merchant = await session.get(DBMerchant, merchant_id)
    if db_merchant is None:
        raise HTTPException(status_code=404, detail="Item not found")

    await session.delete(db_merchant)
    await session.commit()

    return dict(message="Merchant deleted successfully")
