from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    InvalidTokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenPair


class AuthenticationError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(slots=True)
class RequestContext:
    ip: str | None
    user_agent: str | None


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._users = UserRepository(session)
        self._audit = AuditRepository(session)

    async def login(
        self, *, email: str, password: str, context: RequestContext
    ) -> tuple[User, TokenPair]:
        user = await self._users.get_by_email(email)
        if user is None or not user.is_active:
            await self._record_failed_login(email, context, reason="user_not_found_or_inactive")
            await self._session.commit()
            raise AuthenticationError("invalid_credentials", "Invalid email or password")
        if not verify_password(password, user.password_hash):
            await self._record_failed_login(
                email, context, reason="bad_password", actor_user_id=user.id
            )
            await self._session.commit()
            raise AuthenticationError("invalid_credentials", "Invalid email or password")
        tokens = self._issue_tokens(user)
        await self._users.mark_login(user, refresh_jti=_extract_jti(tokens.refresh_token))
        await self._audit.record(
            event_type="auth.login.succeeded",
            success=True,
            actor_email=user.email,
            actor_user_id=user.id,
            ip=context.ip,
            user_agent=context.user_agent,
        )
        await self._session.commit()
        return user, tokens

    async def refresh(
        self, *, refresh_token: str, context: RequestContext
    ) -> tuple[User, TokenPair]:
        payload = self._decode_refresh(refresh_token)
        user = await self._users.get_by_id(str(payload["sub"]))
        if user is None or not user.is_active:
            raise AuthenticationError("invalid_token", "Refresh token no longer valid")
        if user.refresh_token_jti != payload.get("jti"):
            await self._users.rotate_refresh_jti(user, new_jti=None)
            await self._audit.record(
                event_type="auth.refresh.reuse_detected",
                success=False,
                actor_email=user.email,
                actor_user_id=user.id,
                ip=context.ip,
                user_agent=context.user_agent,
            )
            await self._session.commit()
            raise AuthenticationError("invalid_token", "Refresh token already used")
        tokens = self._issue_tokens(user)
        await self._users.rotate_refresh_jti(user, new_jti=_extract_jti(tokens.refresh_token))
        await self._audit.record(
            event_type="auth.refresh.succeeded",
            success=True,
            actor_email=user.email,
            actor_user_id=user.id,
            ip=context.ip,
            user_agent=context.user_agent,
        )
        await self._session.commit()
        return user, tokens

    async def logout(self, *, user: User, context: RequestContext) -> None:
        await self._users.rotate_refresh_jti(user, new_jti=None)
        await self._audit.record(
            event_type="auth.logout",
            success=True,
            actor_email=user.email,
            actor_user_id=user.id,
            ip=context.ip,
            user_agent=context.user_agent,
        )
        await self._session.commit()

    def _issue_tokens(self, user: User) -> TokenPair:
        access = create_access_token(user.id, extra_claims={"role": user.role})
        refresh_jti = str(uuid.uuid4())
        refresh = create_refresh_token(user.id, extra_claims={"jti": refresh_jti})
        return TokenPair(
            access_token=access,
            refresh_token=refresh,
            expires_in=settings.jwt_access_token_ttl_seconds,
        )

    def _decode_refresh(self, token: str) -> dict[str, object]:
        try:
            payload = decode_token(token)
        except InvalidTokenError as exc:
            raise AuthenticationError("invalid_token", str(exc)) from exc
        if payload.get("type") != "refresh":
            raise AuthenticationError("invalid_token", "Wrong token type")
        if not isinstance(payload.get("sub"), str):
            raise AuthenticationError("invalid_token", "Invalid token subject")
        return payload

    async def _record_failed_login(
        self,
        email: str,
        context: RequestContext,
        *,
        reason: str,
        actor_user_id: str | None = None,
    ) -> None:
        await self._audit.record(
            event_type="auth.login.failed",
            success=False,
            actor_email=email,
            actor_user_id=actor_user_id,
            ip=context.ip,
            user_agent=context.user_agent,
            details={"reason": reason},
        )


def _extract_jti(refresh_token: str) -> str:
    payload = decode_token(refresh_token)
    jti = payload.get("jti")
    if not isinstance(jti, str):
        raise AuthenticationError("invalid_token", "Refresh token missing jti")
    return jti
