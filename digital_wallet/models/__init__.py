from typing import AsyncIterator

from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from . import db_models
from . import item
from . import merchant
from . import transaction
from . import user
from . import wallet

from .db_models import *
from .item import *
from .merchant import *
from .transaction import *
from .user import *
from .wallet import *


connect_args = {}

engine = None


def init_db(settings):
    global engine

    engine = create_async_engine(
        settings.SQLDB_URL,
        future=True,
        # echo=True,
        connect_args=connect_args,
    )


async def recreate_table():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncIterator[AsyncSession]:
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


async def close_session():
    global engine
    if engine is None:
        raise Exception("DatabaseSessionManager is not initialized")
    await engine.dispose()
