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


@router.get("/merchants", tags=["merchant"])
async def get_merchants(page: int = 1, page_size: int = 10) -> MerchantList:
    with Session(engine) as db:
        db_merchants = db.exec(
            select(DBMerchant).offset((page - 1) * page_size).limit(page_size)
        ).all()

    return MerchantList(
        merchants=db_merchants,
        page=page,
        page_size=page_size,
        size_per_page=len(db_merchants),
    )


@router.get("/merchant/{merchant_id}", tags=["merchant"])
async def get_merchant(merchant_id: int) -> Merchant:
    with Session(engine) as db:
        db_merchant = db.get(DBMerchant, merchant_id)
        if db_merchant is None:
            raise HTTPException(status_code=404, detail="Item not found")

    return Merchant.from_orm(db_merchant)


@router.put("/merchant/{merchant_id}", tags=["merchant"])
async def update_merchant(merchant_id: int, merchant: UpdateMerchant) -> Merchant:
    with Session(engine) as db:
        db_merchant = db.get(DBMerchant, merchant_id)
        if db_merchant is None:
            raise HTTPException(status_code=404, detail="Item not found")
        for key, value in merchant.dict().items():
            setattr(db_merchant, key, value)
        db.add(db_merchant)
        db.commit()
        db.refresh(db_merchant)

    return Merchant.from_orm(db_merchant)


@router.delete("/merchant/{merchant_id}", tags=["merchant"])
async def delete_merchant(merchant_id: int) -> dict:
    with Session(engine) as db:
        db_merchant = db.get(DBMerchant, merchant_id)
        if db_merchant is None:
            raise HTTPException(status_code=404, detail="Item not found")
        db.delete(db_merchant)
        db.commit()

    return dict(message="Merchant deleted successfully")
