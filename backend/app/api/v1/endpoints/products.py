from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Response, status

from app.api.v1.deps import CurrentUser, DbSession
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate

router = APIRouter()


@router.get("", response_model=list[ProductResponse])
async def list_products(
    session: DbSession,
    current_user: CurrentUser,
    search: str = Query("", max_length=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> list[ProductResponse]:
    repo = ProductRepository(session)
    products = await repo.list_all(search=search, skip=skip, limit=limit)
    return [ProductResponse.model_validate(p) for p in products]


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreate,
    session: DbSession,
    current_user: CurrentUser,
) -> ProductResponse:
    repo = ProductRepository(session)
    existing = await repo.get_by_sku(payload.sku)
    if existing:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail={"code": "duplicate_sku", "message": "SKU already exists"},
        )
    product = await repo.create(
        name=payload.name,
        sku=payload.sku.upper(),
        price=payload.price,
        qty=payload.qty,
    )
    await session.commit()
    return ProductResponse.model_validate(product)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    session: DbSession,
    current_user: CurrentUser,
) -> ProductResponse:
    repo = ProductRepository(session)
    product = await repo.get_by_id(product_id)
    if not product:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Product not found")
    return ProductResponse.model_validate(product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    payload: ProductUpdate,
    session: DbSession,
    current_user: CurrentUser,
) -> ProductResponse:
    repo = ProductRepository(session)
    product = await repo.get_by_id(product_id)
    if not product:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Product not found")
    if payload.sku is not None:
        existing = await repo.get_by_sku(payload.sku)
        if existing and existing.id != product_id:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail={"code": "duplicate_sku", "message": "SKU already exists"},
            )
    updated = await repo.update(
        product,
        name=payload.name,
        sku=payload.sku,
        price=payload.price,
        qty=payload.qty,
    )
    await session.commit()
    return ProductResponse.model_validate(updated)


@router.patch("/{product_id}/stock", response_model=ProductResponse)
async def adjust_stock(
    product_id: str,
    session: DbSession,
    current_user: CurrentUser,
    delta: int = Query(..., description="Positive to add, negative to remove"),
) -> ProductResponse:
    repo = ProductRepository(session)
    product = await repo.get_by_id(product_id)
    if not product:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Product not found")
    if product.qty + delta < 0:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail={"code": "insufficient_stock", "message": "Not enough stock"},
        )
    updated = await repo.adjust_stock(product, delta=delta)
    await session.commit()
    return ProductResponse.model_validate(updated)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    response_model=None,
)
async def delete_product(
    product_id: str,
    session: DbSession,
    current_user: CurrentUser,
) -> None:
    repo = ProductRepository(session)
    product = await repo.get_by_id(product_id)
    if not product:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Product not found")
    await repo.delete(product)
    await session.commit()
