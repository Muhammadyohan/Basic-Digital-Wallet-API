import math

from fastapi import APIRouter, HTTPException, Depends

from typing import Annotated

from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from .. import security
from .. import models

from ..models.wallet import Wallet, CreateWallet, UpdateWallet, WalletList
from ..models.db_models import DBWallet, DBMerchant, DBUser
from ..models.user import User

router = APIRouter(prefix="/wallets", tags=["wallet"])

SIZE_PER_PAGE = 50


@router.post("")
async def create_wallet(
    wallet: CreateWallet,
    current_user: Annotated[User, Depends(security.get_current_active_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> Wallet:
    db_wallet = DBWallet.model_validate(wallet)
    db_wallet.user = current_user
    db_wallet.owner_first_name = current_user.first_name
    db_wallet.owner_last_name = current_user.last_name

    session.add(db_wallet)
    await session.commit()
    await session.refresh(db_wallet)

    return Wallet.model_validate(db_wallet)


@router.get("")
async def get_wallets(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    page: int = 1,
) -> WalletList:
    result = await session.exec(
        select(DBWallet).offset((page - 1) * SIZE_PER_PAGE).limit(SIZE_PER_PAGE)
    )
    db_wallets = result.all()

    page_count = int(
        math.ceil(
            (await session.exec(select(func.count(DBWallet.id)))).first()
            / SIZE_PER_PAGE
        )
    )

    return WalletList.model_validate(
        dict(
            items=db_wallets,
            page=page,
            page_count=page_count,
            size_per_page=SIZE_PER_PAGE,
        )
    )


@router.get("/{wallet_id}")
async def get_wallet(
    wallet_id: int,
    current_user: Annotated[User, Depends(security.get_current_active_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> Wallet:
    db_wallet = await session.get(DBWallet, wallet_id)
    if db_wallet is None:
        raise HTTPException(status_code=404, detail="Item not found")

    if db_wallet.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return Wallet.model_validate(db_wallet)


@router.get("/user/{user_id}")
async def get_wallets_by_user(
    current_user: Annotated[User, Depends(security.get_current_active_user)],
    user_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    page: int = 1,
) -> WalletList:

    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    result = await session.exec(
        select(DBWallet)
        .where(DBWallet.user_id == user_id)
        .offset((page - 1) * SIZE_PER_PAGE)
        .limit(SIZE_PER_PAGE)
    )

    db_wallets = result.all()

    page_count = int(
        math.ceil(
            (await session.exec(select(func.count(DBWallet.id)))).first()
            / SIZE_PER_PAGE
        )
    )

    return WalletList.model_validate(
        dict(
            items=db_wallets,
            page=page,
            page_count=page_count,
            size_per_page=SIZE_PER_PAGE,
        )
    )


@router.put("/{wallet_id}")
async def update_wallet(
    wallet_id: int,
    wallet: UpdateWallet,
    current_user: Annotated[User, Depends(security.get_current_active_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> Wallet:
    data = wallet.model_dump()
    db_wallet = await session.get(DBWallet, wallet_id)

    if db_wallet is None:
        raise HTTPException(status_code=404, detail="Item not found")

    if db_wallet.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this wallet"
        )

    owner_first_name = db_wallet.owner_first_name
    owner_last_name = db_wallet.owner_last_name
    merchant_id = db_wallet.merchant_id
    user_id = db_wallet.user_id

    db_wallet.sqlmodel_update(data)
    db_wallet.owner_first_name = owner_first_name
    db_wallet.owner_last_name = owner_last_name
    db_wallet.merchant_id = merchant_id
    db_wallet.user_id = user_id

    session.add(db_wallet)
    await session.commit()
    await session.refresh(db_wallet)

    return Wallet.model_validate(db_wallet)


@router.delete("/{wallet_id}")
async def delete_wallet(
    wallet_id: int,
    current_user: Annotated[User, Depends(security.get_current_active_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> dict:
    db_wallet = await session.get(DBWallet, wallet_id)

    if db_wallet is None:
        raise HTTPException(status_code=404, detail="Item not found")

    if db_wallet.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this wallet"
        )

    await session.delete(db_wallet)
    await session.commit()

    return dict(message="Wallet deleted successfully")
