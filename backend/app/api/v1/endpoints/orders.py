from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

router = APIRouter()


@router.get("")
async def list_orders() -> dict[str, str]:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, detail="TODO: implement list_orders")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_order() -> dict[str, str]:
    raise HTTPException(
        status.HTTP_501_NOT_IMPLEMENTED,
        detail="TODO: implement create_order with concurrency-safe stock deduction",
    )


@router.get("/{order_id}")
async def get_order(order_id: str) -> dict[str, str]:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, detail="TODO: implement get_order")


@router.post("/{order_id}/cancel")
async def cancel_order(order_id: str) -> dict[str, str]:
    raise HTTPException(
        status.HTTP_501_NOT_IMPLEMENTED,
        detail="TODO: implement cancel_order (idempotent, restores stock)",
    )
