from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import InvalidTokenError, decode_token
from app.db.session import get_db_session
from app.models.user import User
from app.repositories.user_repository import UserRepository

DbSession = Annotated[AsyncSession, Depends(get_db_session)]

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user_id(token: Annotated[str | None, Depends(_oauth2_scheme)]) -> str:
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = decode_token(token)
    except InvalidTokenError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    if payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Wrong token type")
    subject = payload.get("sub")
    if not isinstance(subject, str):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")
    return subject


CurrentUserId = Annotated[str, Depends(get_current_user_id)]


async def get_current_user(user_id: CurrentUserId, session: DbSession) -> User:
    user = await UserRepository(session).get_by_id(user_id)
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
