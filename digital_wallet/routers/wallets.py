from fastapi import APIRouter, HTTPException

from sqlmodel import Session, select

from .sqlmodel_engine import engine

from models.wallet import Wallet, CreateWallet, UpdateWallet
from models.db_models import DBWallet

router = APIRouter()


@router.post("/wallet/{merchant_id}", tags=["wallet"])
async def create_wallet(wallet: CreateWallet, merchant_id: int) -> Wallet:
    data = wallet.dict()
    db_wallet = DBWallet(**data)
    db_wallet.merchant_id = merchant_id
    with Session(engine) as db:
        db.add(db_wallet)
        db.commit()
        db.refresh(db_wallet)

    return Wallet.from_orm(db_wallet)

