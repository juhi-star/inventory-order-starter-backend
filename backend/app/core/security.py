from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

_password_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return _password_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _password_context.verify(plain, hashed)


def create_access_token(subject: str, *, extra_claims: dict[str, Any] | None = None) -> str:
    return _encode_token(subject, settings.jwt_access_token_ttl_seconds, "access", extra_claims)


def create_refresh_token(subject: str, *, extra_claims: dict[str, Any] | None = None) -> str:
    return _encode_token(subject, settings.jwt_refresh_token_ttl_seconds, "refresh", extra_claims)


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise InvalidTokenError(str(exc)) from exc


def _encode_token(
    subject: str,
    ttl_seconds: int,
    token_type: str,
    extra_claims: dict[str, Any] | None,
) -> str:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=ttl_seconds)).timestamp()),
        "type": token_type,
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


class InvalidTokenError(Exception):
    pass
