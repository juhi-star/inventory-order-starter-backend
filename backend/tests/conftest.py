from __future__ import annotations

import os

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("JWT_SECRET", "test-secret-test-secret-test-secret-test-secret")
os.environ.setdefault("SEED_ADMIN_PASSWORD", "test-admin-password")
os.environ.setdefault("SEED_ADMIN_EMAIL", "admin@example.com")

from collections.abc import AsyncIterator

import app.models
import pytest
import pytest_asyncio
from app.api.v1.deps import get_db_session
from app.db.base import Base
from app.main import create_app
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool


@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncIterator[AsyncSession]:
    session_factory = async_sessionmaker(db_engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session


@pytest.fixture
def app(db_session):
    application = create_app()
    application.state.limiter.enabled = False

    async def override_get_db() -> AsyncIterator[AsyncSession]:
        yield db_session

    application.dependency_overrides[get_db_session] = override_get_db
    return application


@pytest_asyncio.fixture
async def client(app) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
