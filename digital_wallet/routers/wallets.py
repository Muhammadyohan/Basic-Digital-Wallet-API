from fastapi import APIRouter, HTTPException, Depends

from typing import Annotated

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .. import models

from ..models.wallet import Wallet, CreateWallet, UpdateWallet
from ..models.db_models import DBWallet, DBMerchant

router = APIRouter(prefix="/wallets", tags=["wallet"])


@router.post("/{merchant_id}")
async def create_wallet(
    wallet: CreateWallet,
    merchant_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> Wallet:
    data = wallet.dict()
    db_wallet = DBWallet(**data)
    db_wallet.merchant_id = merchant_id

    db_merchant = await session.get(DBMerchant, merchant_id)
    db_wallet.merchant_name = db_merchant.name

    session.add(db_wallet)
    await session.commit()
    await session.refresh(db_wallet)

    return Wallet.from_orm(db_wallet)


@router.get("/{wallet_id}")
async def get_wallet(
    wallet_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> Wallet:
    db_wallet = await session.get(DBWallet, wallet_id)
    if db_wallet is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return Wallet.from_orm(db_wallet)


@router.put("/{wallet_id}")
async def update_wallet(
    wallet_id: int,
    wallet: UpdateWallet,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> Wallet:
    db_wallet = await session.get(DBWallet, wallet_id)
    if db_wallet is None:
        raise HTTPException(status_code=404, detail="Item not found")

    for key, value in wallet.dict().items():
        setattr(db_wallet, key, value)

    session.add(db_wallet)
    await session.commit()
    await session.refresh(db_wallet)

    return Wallet.from_orm(db_wallet)


@router.delete("/{wallet_id}")
async def delete_wallet(
    wallet_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> dict:
    db_wallet = await session.get(DBWallet, wallet_id)
    if db_wallet is None:
        raise HTTPException(status_code=404, detail="Item not found")

    await session.delete(db_wallet)
    await session.commit()

    return dict(message="Wallet deleted successfully")
