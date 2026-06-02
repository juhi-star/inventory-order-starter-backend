from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_password
from app.repositories.user_repository import UserRepository


async def seed_admin_if_empty(session: AsyncSession) -> bool:
    if not settings.seed_admin_password:
        return False
    users = UserRepository(session)
    if await users.count() > 0:
        return False
    await users.create(
        email=settings.seed_admin_email,
        password_hash=hash_password(settings.seed_admin_password),
        full_name="Administrator",
        role="admin",
    )
    await session.commit()
    return True
