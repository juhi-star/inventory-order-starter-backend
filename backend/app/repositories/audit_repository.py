from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_event import AuditEvent


class AuditRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record(
        self,
        *,
        event_type: str,
        success: bool,
        actor_email: str | None = None,
        actor_user_id: str | None = None,
        ip: str | None = None,
        user_agent: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> AuditEvent:
        event = AuditEvent(
            event_type=event_type,
            success=success,
            actor_email=actor_email.lower() if actor_email else None,
            actor_user_id=actor_user_id,
            ip=ip,
            user_agent=user_agent,
            details=details or {},
        )
        self._session.add(event)
        await self._session.flush()
        return event
