from httpx import AsyncClient
from digital_wallet import models
import pytest


@pytest.mark.asyncio
async def test_create_items(
    client: AsyncClient, merchant_user1: models.DBMerchant, token_user1: models.Token
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    payload = {
        "user_id": token_user1.user_id,
        "merchant_id": merchant_user1.id,
        "name": "item1",
        "price": 100,
        "stock": 10,
    }
    response = await client.post(
        f"/items/{merchant_user1.id}", json=payload, headers=headers
    )

    data = response.json()

    assert response.status_code == 200
    assert data["id"] > 0
    assert data["user_id"] == int(token_user1.user_id)
    assert data["merchant_id"] == merchant_user1.id
    assert data["name"] == payload["name"]
    assert data["price"] == payload["price"]
    assert data["stock"] == payload["stock"]


@pytest.mark.asyncio
async def test_update_items(
    client: AsyncClient, item_user1: models.DBItem, token_user1: models.Token
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}

    payload = {
        "description": "test item description",
        "name": "Test Update Item",
        "price": 500,
        "stock": 50,
    }
    response = await client.put(
        f"/items/{item_user1.id}", json=payload, headers=headers
    )

    data = response.json()

    assert response.status_code == 200
    assert data["description"] == payload["description"]
    assert data["name"] == payload["name"]
    assert data["price"] == payload["price"]
    assert data["stock"] == payload["stock"]
    assert data["id"] == item_user1.id
