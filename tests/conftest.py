import sys
import os
from pathlib import Path

# Add the parent directory of 'digital_wallet' to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport


from typing import Any, Dict, Optional
from pydantic_settings import SettingsConfigDict

from digital_wallet import models, config, main, security

import pytest
import pytest_asyncio

import pathlib

import datetime


SettingsTesting = config.Settings
SettingsTesting.model_config = SettingsConfigDict(
    env_file=".testing.env", validate_assignment=True, extra="allow"
)


@pytest.fixture(name="app", scope="session")
def app_fixture():
    settings = SettingsTesting()
    path = pathlib.Path("test-data")
    if not path.exists():
        path.mkdir()

    app = main.create_app(settings)

    asyncio.run(models.recreate_table())

    yield app


@pytest.fixture(name="client", scope="session")
def client_fixture(app: FastAPI) -> AsyncClient:

    # client = TestClient(app)
    # yield client
    # app.dependency_overrides.clear()
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost")


@pytest_asyncio.fixture(name="session", scope="session")
async def get_session() -> models.AsyncIterator[models.AsyncSession]:
    settings = SettingsTesting()
    models.init_db(settings)

    async_session = models.sessionmaker(
        models.engine, class_=models.AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(name="user1")
async def example_user1(session: models.AsyncSession) -> models.DBUser:
    password = "123456"
    hash_password = security.get_password_hash(password)
    username = "user1"

    query = await session.exec(
        models.select(models.DBUser).where(models.DBUser.username == username).limit(1)
    )
    user = query.one_or_none()
    if user:
        return user

    user = models.DBUser(
        username=username,
        hashed_password=hash_password,
        email="test@test.com",
        telephone="0812345678",
        first_name="Firstname",
        last_name="lastname",
        disabled=False,
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture(name="token_user1")
async def oauth_token_user1(user1: models.DBUser) -> dict:
    settings = SettingsTesting()
    access_token_expires = datetime.timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    user = user1
    return models.Token(
        access_token=security.create_access_token(
            data={"sub": user.id},
            expires_delta=access_token_expires,
        ),
        refresh_token=security.create_refresh_token(
            data={"sub": user.id},
            expires_delta=access_token_expires,
        ),
        token_type="Bearer",
        scope="",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        expires_at=datetime.datetime.now() + access_token_expires,
        issued_at=datetime.datetime.now(),
        user_id=str(user.id),
    )


@pytest_asyncio.fixture(name="merchant_user1")
async def example_merchant_user1(
    session: models.AsyncSession, user1: models.DBUser
) -> models.DBMerchant:

    query = await session.exec(
        models.select(models.DBMerchant)
        .where(
            models.DBMerchant.user_id == user1.id,
        )
        .limit(1)
    )
    merchant = query.one_or_none()
    if merchant:
        return merchant

    merchant = models.DBMerchant(user=user1, description="Merchant Description")

    session.add(merchant)
    await session.commit()
    await session.refresh(merchant)
    return merchant


@pytest_asyncio.fixture(name="item_user1")
async def example_item_user1(
    session: models.AsyncSession,
    user1: models.DBUser,
    merchant_user1: models.DBMerchant,
) -> models.DBItem:
    name = "item1"
    price = 100
    stock = 10

    query = await session.exec(
        models.select(models.DBItem)
        .where(
            models.DBItem.name == name,
            models.DBItem.user_id == user1.id,
        )
        .limit(1)
    )
    item = query.one_or_none()
    if item:
        return item

    item = models.DBItem(
        name=name,
        user=user1,
        merchant_id=merchant_user1.id,
        description="Item Description",
        price=price,
        stock=stock,
    )

    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item
