from __future__ import annotations

import pytest_asyncio
from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture
async def seeded_admin(db_session: AsyncSession) -> User:
    user = User(
        email=settings.seed_admin_email.lower(),
        password_hash=hash_password(settings.seed_admin_password),
        full_name="Administrator",
        role="admin",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


async def _login(client: AsyncClient, *, email: str, password: str):
    return await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )


async def test_login_succeeds_returns_user_and_tokens(
    client: AsyncClient, seeded_admin: User
) -> None:
    response = await _login(
        client,
        email=settings.seed_admin_email,
        password=settings.seed_admin_password,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["user"]["email"] == settings.seed_admin_email.lower()
    assert body["user"]["role"] == "admin"
    assert body["user"]["is_active"] is True
    assert body["tokens"]["token_type"] == "bearer"
    assert body["tokens"]["access_token"]
    assert body["tokens"]["refresh_token"]
    assert body["tokens"]["expires_in"] == settings.jwt_access_token_ttl_seconds


async def test_login_with_wrong_password_returns_401(
    client: AsyncClient, seeded_admin: User
) -> None:
    response = await _login(client, email=settings.seed_admin_email, password="not-the-password")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_credentials"


async def test_login_with_unknown_email_returns_401(client: AsyncClient) -> None:
    response = await _login(client, email="nobody@example.com", password="anything")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_credentials"


async def test_me_without_token_returns_401(client: AsyncClient) -> None:
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


async def test_me_with_valid_token_returns_user(client: AsyncClient, seeded_admin: User) -> None:
    login = await _login(
        client,
        email=settings.seed_admin_email,
        password=settings.seed_admin_password,
    )
    access = login.json()["tokens"]["access_token"]
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == settings.seed_admin_email.lower()
    assert body["role"] == "admin"


async def test_refresh_rotates_and_rejects_old_refresh(
    client: AsyncClient, seeded_admin: User
) -> None:
    login = await _login(
        client,
        email=settings.seed_admin_email,
        password=settings.seed_admin_password,
    )
    old_refresh = login.json()["tokens"]["refresh_token"]
    rotated = await client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert rotated.status_code == 200
    new_refresh = rotated.json()["refresh_token"]
    assert new_refresh != old_refresh
    reuse = await client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert reuse.status_code == 401
    assert reuse.json()["error"]["code"] == "invalid_token"


async def test_logout_invalidates_refresh_token(client: AsyncClient, seeded_admin: User) -> None:
    login = await _login(
        client,
        email=settings.seed_admin_email,
        password=settings.seed_admin_password,
    )
    access = login.json()["tokens"]["access_token"]
    refresh = login.json()["tokens"]["refresh_token"]
    logout = await client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert logout.status_code == 204
    after = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert after.status_code == 401


async def test_refresh_rejects_access_token(client: AsyncClient, seeded_admin: User) -> None:
    login = await _login(
        client,
        email=settings.seed_admin_email,
        password=settings.seed_admin_password,
    )
    access = login.json()["tokens"]["access_token"]
    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": access})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_token"
