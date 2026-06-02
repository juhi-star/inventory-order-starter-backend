from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

router = APIRouter()


@router.get("/summary")
async def get_summary() -> dict[str, str]:
    raise HTTPException(
        status.HTTP_501_NOT_IMPLEMENTED,
        detail="TODO: implement dashboard summary with Redis caching",
    )
