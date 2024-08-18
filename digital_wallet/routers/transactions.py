import math

from fastapi import APIRouter, HTTPException, Depends

from typing import Annotated

from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from .. import models

from ..models.transaction import Transaction, CreateTransaction, TransactionList
from ..models.db_models import DBTransaction, DBWallet, DBItem

router = APIRouter(prefix="/transactions", tags=["transaction"])

SIZE_PER_PAGE = 50

@router.post("/{wallet_id}/{item_id}")
async def create_transaction(
    transaction: CreateTransaction,
    wallet_id: int,
    item_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> Transaction:
    data = transaction.dict()
    db_transaction = DBTransaction(**data)
    db_transaction.wallet_id = wallet_id
    db_transaction.item_id = item_id

    db_wallet = await session.get(DBWallet, wallet_id)
    db_item = await session.get(DBItem, item_id)
    if db_wallet is None or db_item is None:
        raise HTTPException(status_code=404, detail="Item or Wallet not found")

    total_price = db_item.price * db_transaction.quantity
    if db_wallet.balance < total_price:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    db_wallet.balance -= total_price
    db_wallet.sqlmodel_update(db_wallet.dict())

    db_transaction.total_price = total_price

    session.add(db_wallet)
    session.add(db_transaction)
    await session.commit()
    await session.refresh(db_transaction)

    return Transaction.from_orm(db_transaction)


@router.get("/{transaction_id}")
async def get_transaction(
    transaction_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> Transaction:
    db_transaction = await session.get(DBTransaction, transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return Transaction.from_orm(db_transaction)


@router.get("/{wallet_id}")
async def get_transactions(
    wallet_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> TransactionList:
    result = await session.exec(
        select(DBTransaction).where(DBTransaction.wallet_id == wallet_id)
    )
    db_transactions = result.all()

    return TransactionList(
        transactions=db_transactions,
        page=1,
        page_size=len(db_transactions),
        size_per_page=len(db_transactions),
    )


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> dict:
    db_transaction = await session.get(DBTransaction, transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    await session.delete(db_transaction)
    await session.commit()

    return dict(message="Transaction deleted successfully")
