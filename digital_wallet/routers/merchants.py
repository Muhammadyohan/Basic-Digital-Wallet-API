from fastapi import APIRouter, HTTPException

from sqlmodel import Session, select

from .sqlmodel_engine import engine

from models.merchant import Merchant, CreateMerchant, UpdateMerchant, MerchantList
from models.db_models import DBMerchant

router = APIRouter()


@router.post("/merchant", tags=["merchant"])
async def create_merchant(item: CreateMerchant) -> Merchant:
    data = item.dict()
    db_item = DBMerchant(**data)
    with Session(engine) as db:
        db.add(db_item)
        db.commit()
        db.refresh(db_item)

    return Merchant.from_orm(db_item)
    
