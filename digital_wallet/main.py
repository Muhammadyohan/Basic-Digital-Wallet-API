from fastapi import FastAPI, HTTPException

from sqlmodel import create_engine, SQLModel, Session, select 

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
    db_item = DBItem(**data)
    with Session(engine) as db:
        db.add(db_item)
        db.commit()
        db.refresh(db_item)

    return Item.from_orm(db_item)


@app.get("/items")
async def get_items(page: int = 1, page_size: int = 10) -> ItemList:
    with Session(engine) as db:
        db_items = db.exec(
            select(DBItem).offset((page - 1) * page_size).limit(page_size)
        ).all()

    return ItemList(
        items=db_items, page=page, page_size=page_size, size_per_page=len(db_items)
    )


@app.get("/item/{item_id}")
async def get_item(item_id: int) -> Item:
    with Session(engine) as db:
        db_item = db.get(DBItem, item_id)
        if db_item is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return Item.from_orm(db_item)


@app.put("/item/{item_id}")
async def update_item(item_id: int, item: UpdateItem) -> Item:
    with Session(engine) as db:
        db_item = db.get(DBItem, item_id)
        if db_item is None:
            raise HTTPException(status_code=404, detail="Item not found")
        for key, value in item.dict().items():
            setattr(db_item, key, value)
            db.add(db_item)
            db.commit()
            db.refresh(db_item)

    return Item.from_orm(db_item)


@app.delete("/item/{item_id}")
async def delete_item(item_id: int) -> dict:
    with Session(engine) as db:
        db_item = db.get(DBItem, item_id)
        if db_item is None:
            raise HTTPException(status_code=404, detail="Item not found")
        db.delete(db_item)
        db.commit()

    return dict(message="Item deleted successfully")
