from fastapi import FastAPI

from routers import items, merchants, wallets, transactions

from sqlmodel import SQLModel

from routers.sqlmodel_engine import engine

app = FastAPI()


app.include_router(items.router)
app.include_router(merchants.router)
app.include_router(wallets.router)
app.include_router(transactions.router)


SQLModel.metadata.create_all(engine)


@app.get("/")
def read_root():
    return {"Hello": "World"}
