from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Response, status

from app.api.v1.deps import CurrentUser, DbSession
from app.repositories.customer_repository import CustomerRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.order import OrderCreate, OrderResponse

router = APIRouter()


@router.get("", response_model=list[OrderResponse])
async def list_orders(
    session: DbSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> list[OrderResponse]:
    repo = OrderRepository(session)
    orders = await repo.list_all(skip=skip, limit=limit)
    return [OrderResponse.model_validate(o) for o in orders]


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreate,
    session: DbSession,
    current_user: CurrentUser,
) -> OrderResponse:
    customer_repo = CustomerRepository(session)
    product_repo = ProductRepository(session)
    order_repo = OrderRepository(session)

    customer = await customer_repo.get_by_id(payload.customer_id)
    if not customer:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Customer not found")

    oversells: list[dict[str, object]] = []
    lines_data: list[tuple[object, int]] = []

    for line in payload.lines:
        product = await product_repo.get_by_id(line.product_id)
        if not product:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=f"Product {line.product_id} not found",
            )
        if product.qty < line.qty:
            oversells.append({
                "line": len(lines_data),
                "product_id": product.id,
                "requested": line.qty,
                "available": product.qty,
            })
        else:
            lines_data.append((product, line.qty))

    if oversells:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail={"code": "oversell", "message": "Insufficient stock for some items", "details": oversells},
        )

    for product, qty in lines_data:
        await product_repo.adjust_stock(product, delta=-qty)

    order = await order_repo.create(
        customer_id=customer.id,
        customer_name=customer.full_name,
        lines_data=lines_data,
    )
    await session.commit()
    return OrderResponse.model_validate(order)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    session: DbSession,
    current_user: CurrentUser,
) -> OrderResponse:
    repo = OrderRepository(session)
    order = await repo.get_by_id(order_id)
    if not order:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Order not found")
    return OrderResponse.model_validate(order)


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: str,
    session: DbSession,
    current_user: CurrentUser,
) -> OrderResponse:
    order_repo = OrderRepository(session)
    product_repo = ProductRepository(session)

    order = await order_repo.get_by_id(order_id)
    if not order:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.status != "placed":
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail={"code": "invalid_state", "message": "Order is not in placed state"},
        )

    for line in order.lines:
        product = await product_repo.get_by_id(line.product_id)
        if product:
            await product_repo.adjust_stock(product, delta=line.qty)

    await order_repo.cancel(order)
    await session.commit()
    return OrderResponse.model_validate(order)
