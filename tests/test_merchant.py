from httpx import AsyncClient
from digital_wallet import models
import pytest


@pytest.mark.asyncio
async def test_no_permission_create_merchants(
    client: AsyncClient, user1: models.DBUser
):
    payload = {"first_name": "merchants", "user_id": user1.id}
    response = await client.post("/merchants", json=payload)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_merchants(client: AsyncClient, token_user1: models.Token):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}
    payload = {"user_id": token_user1.user_id}
    response = await client.post("/merchants", json=payload, headers=headers)

    data = response.json()

    assert response.status_code == 200
    assert data["id"] > 0
    assert data["user_id"] == int(token_user1.user_id)


@pytest.mark.asyncio
async def test_update_merchants(
    client: AsyncClient, merchant_user1: models.DBMerchant, token_user1: models.Token
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}

    payload = {"description": "test merchant description"}
    response = await client.put(
        f"/merchants/{merchant_user1.id}", json=payload, headers=headers
    )

    data = response.json()

    assert response.status_code == 200
    assert data["description"] == payload["description"]
    assert data["id"] == merchant_user1.id


@pytest.mark.asyncio
async def test_delete_merchant(
    client: AsyncClient, merchant_user1: models.DBMerchant, token_user1: models.Token
):
    headers = {"Authorization": f"{token_user1.token_type} {token_user1.access_token}"}

    response = await client.delete(f"/merchants/{merchant_user1.id}", headers=headers)

    data = response.json()

    assert response.status_code == 200
    assert "success" in data["message"]


@pytest.mark.asyncio
async def test_list_merchants(
    client: AsyncClient, merchant_user1: models.DBMerchant, session: models.AsyncSession
):

    response = await client.get("/merchants")

    data = response.json()
    assert response.status_code == 200
    assert len(data["merchants"]) > 0
    check_merchant = None

    for merchant in data["merchants"]:
        if merchant["first_name"] == merchant_user1.first_name:
            check_merchant = merchant
            break

    assert check_merchant["id"] == merchant_user1.id
    assert check_merchant["first_name"] == merchant_user1.first_name
