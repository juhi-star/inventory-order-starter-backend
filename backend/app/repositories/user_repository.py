from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email.lower())
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: str) -> User | None:
        return await self._session.get(User, user_id)

    async def create(
        self,
        *,
        email: str,
        password_hash: str,
        full_name: str,
        role: str = "user",
    ) -> User:
        user = User(
            email=email.lower(),
            password_hash=password_hash,
            full_name=full_name,
            role=role,
        )
        self._session.add(user)
        await self._session.flush()
        return user

    async def mark_login(self, user: User, *, refresh_jti: str | None) -> User:
        user.last_login_at = datetime.now(UTC)
        user.refresh_token_jti = refresh_jti
        await self._session.flush()
        return user

    async def rotate_refresh_jti(self, user: User, *, new_jti: str | None) -> User:
        user.refresh_token_jti = new_jti
        await self._session.flush()
        return user

    async def count(self) -> int:
        from sqlalchemy import func

        stmt = select(func.count()).select_from(User)
        result = await self._session.execute(stmt)
        return int(result.scalar_one())
