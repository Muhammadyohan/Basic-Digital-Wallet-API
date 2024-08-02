from fastapi import FastAPI, HTTPException

from sqlmodel import create_engine, SQLModel, Session, select # type: ignore

from models.item import Item, CreateItem, UpdateItem, ItemList, DBItem

connect_args = {}

engine = create_engine(
    "postgresql+pg8000://postgres:123456@localhost/DigitalWalletDB",
    connect_args=connect_args,
)

SQLModel.metadata.create_all(engine)


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/items")
async def create_item(item: CreateItem) -> Item:
    data = item.dict()
    db_item = DBItem(**data)
    with Session(engine) as db:
        db.add(db_item)
        db.commit()
        db.refresh(db_item)

    return Item.from_orm(db_item)
