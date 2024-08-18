import math

from fastapi import APIRouter, HTTPException, Depends

from typing import Annotated

from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from .. import security
from .. import models

from ..models.transaction import Transaction, CreateTransaction, TransactionList
from ..models.db_models import DBTransaction, DBWallet, DBItem, DBMerchant
from ..models.user import User

router = APIRouter(prefix="/transactions", tags=["transaction"])

SIZE_PER_PAGE = 50


@router.post("/{buyer_wallet_id}/{vendor_wallet_id}/{item_id}")
async def create_transaction(
    current_user: Annotated[User, Depends(security.get_current_active_user)],
    transaction: CreateTransaction,
    buyer_wallet_id: int,
    vendor_wallet_id: int,
    item_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> Transaction:
    db_transaction = DBTransaction.model_validate(transaction)

    db_buyer_wallet = await session.get(DBWallet, buyer_wallet_id)
    db_vendor_wallet = await session.get(DBWallet, vendor_wallet_id)
    db_item = await session.get(DBItem, item_id)
    db_merchant = await session.get(DBMerchant, db_item.merchant_id)

    if db_buyer_wallet is None or db_item is None:
        raise HTTPException(status_code=404, detail="Item or Wallet not found")

    if db_item.stock < db_transaction.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    total_price = db_item.price * db_transaction.quantity
    if db_buyer_wallet.balance < total_price:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    db_buyer_wallet.balance -= total_price
    db_vendor_wallet.balance += total_price
    db_item.stock -= db_transaction.quantity

    db_buyer_wallet.sqlmodel_update(db_buyer_wallet.dict())
    db_vendor_wallet.sqlmodel_update(db_vendor_wallet.dict())
    db_item.sqlmodel_update(db_item.dict())

    db_transaction.wallet_id = buyer_wallet_id

    db_transaction.total_price = total_price

    db_transaction.item_name = db_item.name
    db_transaction.item_id = item_id

    db_transaction.merchant_first_name = db_merchant.first_name
    db_transaction.merchant_last_name = db_merchant.last_name
    db_transaction.merchant_id = db_merchant.id

    db_transaction.user_first_name = current_user.first_name
    db_transaction.user_last_name = current_user.last_name
    db_transaction.user = current_user

    session.add(db_buyer_wallet)
    session.add(db_vendor_wallet)
    session.add(db_item)
    session.add(db_transaction)
    await session.commit()
    await session.refresh(db_transaction)

    return Transaction.model_validate(db_transaction)


@router.get("/{transaction_id}")
async def get_transaction(
    current_user: Annotated[User, Depends(security.get_current_active_user)],
    transaction_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> Transaction:
    db_transaction = await session.get(DBTransaction, transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return Transaction.model_validate(db_transaction)


@router.get("/user/{user_id}")
async def get_transactions(
    current_user: Annotated[User, Depends(security.get_current_active_user)],
    user_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    page: int = 1,
) -> TransactionList:
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    result = await session.exec(
        select(DBTransaction)
        .where(DBTransaction.user_id == user_id)
        .offset((page - 1) * SIZE_PER_PAGE)
        .limit(SIZE_PER_PAGE)
    )

    db_transactions = result.all()

    pages = math.ceil(
        (await session.exec(select(func.count(DBTransaction.id)))).first()
        / SIZE_PER_PAGE
    )

    return TransactionList.model_validate(
        dict(
            transactions=db_transactions,
            page=page,
            page_count=pages,
            size_per_page=SIZE_PER_PAGE,
        )
    )


@router.delete("/{transaction_id}")
async def delete_transaction(
    current_user: Annotated[User, Depends(security.get_current_active_user)],
    transaction_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> dict:
    db_transaction = await session.get(DBTransaction, transaction_id)

    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Item not found")

    if db_transaction.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    await session.delete(db_transaction)
    await session.commit()

    return dict(message="Transaction deleted successfully")
