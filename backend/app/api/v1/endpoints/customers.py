from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response, status

router = APIRouter()


@router.get("")
async def list_customers() -> dict[str, str]:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, detail="TODO: implement list_customers")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_customer() -> dict[str, str]:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, detail="TODO: implement create_customer")


@router.get("/{customer_id}")
async def get_customer(customer_id: str) -> dict[str, str]:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, detail="TODO: implement get_customer")


@router.put("/{customer_id}")
async def update_customer(customer_id: str) -> dict[str, str]:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, detail="TODO: implement update_customer")


@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    response_model=None,
)
async def delete_customer(customer_id: str) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, detail="TODO: implement delete_customer")
