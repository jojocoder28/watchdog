import pytest

@pytest.mark.asyncio
async def test_register_success(async_client):
    response = await async_client.post(
        "/auth/register",
        json={"email": "newuser@example.com", "password": "securepassword"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data

@pytest.mark.asyncio
async def test_register_duplicate_email(async_client, test_user):
    response = await async_client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "securepassword"}
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

@pytest.mark.asyncio
async def test_login_success(async_client, test_user):
    response = await async_client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_wrong_password(async_client, test_user):
    response = await async_client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_get_me_authenticated(auth_client, test_user):
    response = await auth_client.get("/auth/me")
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_get_me_unauthenticated(async_client):
    response = await async_client.get("/auth/me")
    assert response.status_code == 401
