from fastapi import APIRouter, HTTPException

from sqlmodel import Session, select

from ..models import engine

from ..models.transaction import Transaction, CreateTransaction, TransactionList
from ..models.db_models import DBTransaction, DBWallet, DBItem

router = APIRouter(prefix="/transactions", tags=["transaction"])


@router.post("/{wallet_id}/{item_id}")
async def create_transaction(
    transaction: CreateTransaction, wallet_id: int, item_id: int
) -> Transaction:
    data = transaction.dict()
    db_transaction = DBTransaction(**data)
    db_transaction.wallet_id = wallet_id
    db_transaction.item_id = item_id

    with Session(engine) as db:
        db_wallet = db.get(DBWallet, wallet_id)
        db_item = db.get(DBItem, item_id)
        if db_wallet is None or db_item is None:
            raise HTTPException(status_code=404, detail="Item or Wallet not found")

        total_price = db_item.price * db_transaction.quantity
        if db_wallet.balance < total_price:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        db_wallet.balance -= total_price
        db_wallet.sqlmodel_update(db_wallet.dict())

        db_transaction.total_price = total_price

        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)

    return Transaction.from_orm(db_transaction)


@router.get("/{transaction_id}")
async def get_transaction(transaction_id: int) -> Transaction:
    with Session(engine) as db:
        db_transaction = db.get(DBTransaction, transaction_id)
        if db_transaction is None:
            raise HTTPException(status_code=404, detail="Item not found")

        return Transaction.from_orm(db_transaction)


@router.get("/{wallet_id}")
async def get_transactions(wallet_id: int) -> TransactionList:
    with Session(engine) as db:
        db_transactions = db.exec(
            select(DBTransaction).where(DBTransaction.wallet_id == wallet_id)
        ).all()

    return TransactionList(
        transactions=db_transactions,
        page=1,
        page_size=len(db_transactions),
        size_per_page=len(db_transactions),
    )


@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: int) -> dict:
    with Session(engine) as db:
        db_transaction = db.get(DBTransaction, transaction_id)
        if db_transaction is None:
            raise HTTPException(status_code=404, detail="Item not found")
        db.delete(db_transaction)
        db.commit()

    return dict(message="Transaction deleted successfully")