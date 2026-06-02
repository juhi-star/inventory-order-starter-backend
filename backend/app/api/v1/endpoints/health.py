from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text

from app.api.v1.deps import DbSession

router = APIRouter()


@router.get("/live")
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def readiness(db: DbSession) -> dict[str, str]:
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"database unavailable: {exc}",
        ) from exc
    return {"status": "ready"}
