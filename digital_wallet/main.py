from fastapi import FastAPI, HTTPException

from sqlmodel import create_engine, SQLModel, Session, select  # type: ignore

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


@app.post("/item")
async def create_item(item: CreateItem) -> Item:
    data = item.dict()
    dbItem = DBItem(**data)
    with Session(engine) as db:
        db.add(dbItem)
        db.commit()
        db.refresh(dbItem)

    return Item.from_orm(dbItem)


@app.get("/items")
async def get_items(page: int = 1, page_size: int = 10) -> ItemList:
    with Session(engine) as db:
        dbItems = db.exec(
            select(DBItem).offset((page - 1) * page_size).limit(page_size)
        ).all()

    return ItemList(
        items=dbItems, page=page, page_size=page_size, size_per_page=len(dbItems)
    )


@app.get("/item/{item_id}")
async def get_item(item_id: int) -> Item:
    with Session(engine) as db:
        dbItem = db.get(DBItem, item_id)
        if dbItem is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return Item.from_orm(dbItem)
