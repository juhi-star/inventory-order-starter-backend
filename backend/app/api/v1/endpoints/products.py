from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response, status

router = APIRouter()


@router.get("")
async def list_products() -> dict[str, str]:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, detail="TODO: implement list_products")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_product() -> dict[str, str]:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, detail="TODO: implement create_product")


@router.get("/{product_id}")
async def get_product(product_id: str) -> dict[str, str]:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, detail="TODO: implement get_product")


@router.put("/{product_id}")
async def update_product(product_id: str) -> dict[str, str]:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, detail="TODO: implement update_product")


@router.patch("/{product_id}/stock")
async def adjust_stock(product_id: str) -> dict[str, str]:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, detail="TODO: implement adjust_stock")


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    response_model=None,
)
async def delete_product(product_id: str) -> None:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, detail="TODO: implement delete_product")
